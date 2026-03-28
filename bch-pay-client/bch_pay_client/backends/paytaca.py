"""
Paytaca CLI backend for bch-pay-client.

Uses the `paytaca` command-line tool to perform real BCH operations.
Requires:
- Node.js 20+
- paytaca-cli installed globally (`npm install -g paytaca-cli`)
- Wallet initialized (`paytaca wallet create` or `import`)

This backend delegates to the Paytaca CLI, which uses Watchtower.cash as backend.
"""

import subprocess
import json
import time
import uuid
from typing import Optional, Dict, Any, List
from pathlib import Path

from .base import BCHBackend, Invoice


class PaytacaBackend(BCHBackend):
    """Backend using Paytaca CLI."""

    def __init__(
        self,
        paytaca_cli: str = "paytaca",
        network: str = "testnet",
        storage_path: Optional[str] = None
    ):
        """
        Initialize Paytaca backend.

        Args:
            paytaca_cli: Path to paytaca executable (default: 'paytaca')
            network: 'testnet' (chipnet) or 'mainnet'
            storage_path: Local storage for invoice tracking
        """
        self.paytaca_cli = paytaca_cli
        self.network = network
        self.is_chipnet = (network == "testnet")
        self.storage_path = Path(storage_path or Path.home() / ".bch_pay.json")
        self._invoices: Dict[str, Dict[str, Any]] = {}
        self._load()

        # Verify paytaca is available
        self._verify_paytaca_installed()

    def _load(self) -> None:
        """Load local invoice storage."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    self._invoices = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._invoices = {}

    def _save(self) -> None:
        """Save invoices to local storage."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self._invoices, f, indent=2)

    def _verify_paytaca_installed(self) -> None:
        """Check that paytaca CLI is available."""
        try:
            result = subprocess.run(
                [self.paytaca_cli, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError(f"Paytaca CLI not working: {result.stderr}")
        except FileNotFoundError:
            raise RuntimeError(
                f"Paytaca CLI not found at '{self.paytaca_cli}'. "
                "Install with: npm install -g paytaca-cli"
            )

    def _run_paytaca(self, args: List[str]) -> Dict[str, Any]:
        """Run paytaca CLI command and return parsed result."""
        cmd = [self.paytaca_cli] + args
        if self.is_chipnet and "--chipnet" not in args:
            cmd.append("--chipnet")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr.strip() or "Unknown error",
                    "output": result.stdout
                }
            return {"success": True, "output": result.stdout}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Paytaca command timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_next_address_index(self) -> int:
        """Get next available address index (simple counter)."""
        # Use invoice count + any existing indices
        indices = []
        for data in self._invoices.values():
            idx = data.get("address_index")
            if isinstance(idx, int):
                indices.append(idx)
        return max(indices, default=-1) + 1

    def create_invoice(
        self,
        amount: float,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
        token_category: Optional[str] = None
    ) -> Invoice:
        """
        Create a new invoice.

        Args:
            amount: Amount in BCH or token units
            description: Description of what's being sold
            metadata: Optional extra data
            token_category: If set, creates a token invoice (CashToken)
                           Requires a 64-char hex category ID (e.g., MUSD)
        """
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")

        invoice_id = str(uuid.uuid4())
        index = self._get_next_address_index()

        # Get appropriate address
        if token_category:
            # Token-aware address (z-prefix)
            result = self._run_paytaca([
                "receive", "--no-qr",
                f"--index={index}",
                "--token", token_category
            ])
        else:
            # Regular BCH address
            result = self._run_paytaca([
                "receive", "--no-qr",
                f"--index={index}"
            ])

        if not result["success"]:
            raise RuntimeError(f"Failed to get address: {result.get('error')}")

        # Parse address from output
        address = None
        for line in result["output"].split("\n"):
            if "Address:" in line:
                address = line.split("Address:")[1].strip()
                break
        if not address:
            raise RuntimeError("Could not parse address from paytaca output")

        invoice = Invoice(
            id=invoice_id,
            amount=amount,
            description=description,
            address=address,
            created_at=time.time(),
            paid=False,
            txid=None,
            confirmations=0,
            metadata=metadata or {}
        )

        # Store with extra token info
        invoice_data = invoice.to_dict()
        invoice_data["address_index"] = index
        invoice_data["token_category"] = token_category
        self._invoices[invoice_id] = invoice_data
        self._save()

        return invoice

    def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        """Get invoice from local storage."""
        data = self._invoices.get(invoice_id)
        if data:
            # Remove backend-specific fields
            data.pop("address_index", None)
            data.pop("token_category", None)
            return Invoice(**data)
        return None

    def check_payment(self, invoice_id: str) -> bool:
        """
        Check payment by scanning Paytaca history.

        Handles both BCH and token payments.
        """
        invoice_data = self._invoices.get(invoice_id)
        if not invoice_data:
            return False

        if invoice_data.get("paid", False):
            return True

        # Determine if this is a token invoice
        token_category = invoice_data.get("token_category")

        # Fetch history from Paytaca
        args = ["history", "--json"]
        if token_category:
            args.extend(["--token", token_category])

        result = self._run_paytaca(args)
        if not result["success"]:
            return False

        try:
            history = json.loads(result["output"])
        except json.JSONDecodeError:
            # Try NDJSON
            history = []
            for line in result["output"].strip().split("\n"):
                try:
                    history.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        expected_amount = invoice_data["amount"]
        target_address = invoice_data["address"]

        for tx in history:
            # Both BCH and token history have record_type
            if tx.get("record_type") != "incoming":
                continue

            # Check recipients
            recipients = tx.get("recipients", [])
            for recipient in recipients:
                if recipient.get("address") == target_address:
                    tx_amount = float(recipient.get("amount", 0))
                    if tx_amount >= expected_amount - 1e-8:
                        # Payment found!
                        invoice_data["paid"] = True
                        invoice_data["paid_at"] = time.time()
                        invoice_data["txid"] = tx.get("txid")
                        invoice_data["confirmations"] = tx.get("confirmations", 1)
                        self._invoices[invoice_id] = invoice_data
                        self._save()
                        return True

        return False

    def get_balance(
        self,
        token_category: Optional[str] = None
    ) -> float:
        """
        Get wallet balance.

        Args:
            token_category: If set, returns balance for that token.
                           If None, returns BCH balance.
        """
        if token_category:
            # Token balance
            result = self._run_paytaca([
                "token", "list", "--json"
            ])
            if not result["success"]:
                return 0.0

            try:
                tokens = json.loads(result["output"])
                # tokens is a list of fungible tokens
                for token in tokens:
                    if token.get("category", "").lower() == token_category.lower():
                        return float(token.get("balance", 0))
            except (json.JSONDecodeError, KeyError):
                pass
            return 0.0
        else:
            # BCH balance
            result = self._run_paytaca(["balance"])
            if not result["success"]:
                return 0.0

            output = result["output"]
            try:
                for line in output.split("\n"):
                    if "BCH" in line:
                        parts = line.split()
                        for part in parts:
                            try:
                                return float(part)
                            except ValueError:
                                continue
            except Exception:
                pass
            return 0.0

    def list_invoices(self, limit: int = 100) -> List[Invoice]:
        """List all invoices from local storage."""
        invoices = []
        for data in self._invoices.values():
            data.pop("address_index", None)
            data.pop("token_category", None)
            invoices.append(Invoice(**data))
        return sorted(invoices, key=lambda x: x.created_at, reverse=True)[:limit]

    def send_payment(
        self,
        address: str,
        amount: float,
        token_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send BCH or token payment.

        Args:
            address: Recipient address
            amount: Amount (BCH or token units)
            token_category: If set, sends CashToken; otherwise BCH

        Returns:
            dict with keys: success (bool), txid (str), error (str)
        """
        try:
            if token_category:
                # Send token: paytaca token send <address> <amount> --token <category>
                cmd = [
                    "token", "send",
                    address, str(amount),
                    "--token", token_category
                ]
            else:
                # Send BCH: paytaca send <address> <amount>
                cmd = ["send", address, f"{amount:.8f}"]

            result = self._run_paytaca(cmd)
            if result["success"]:
                # Extract txid from output
                txid = None
                for line in result["output"].split("\n"):
                    if "txid:" in line.lower():
                        txid = line.split(":", 1)[1].strip()
                        break
                return {"success": True, "txid": txid}
            else:
                return {"success": False, "error": result.get("error", "Unknown error")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_tokens(self) -> List[Dict[str, Any]]:
        """
        List all CashTokens in the wallet.

        Returns:
            List of token dicts with keys: category, symbol, name, decimals, balance
        """
        result = self._run_paytaca(["token", "list", "--json"])
        if not result["success"]:
            return []

        try:
            tokens = json.loads(result["output"])
            # Normalize format
            normalized = []
            for t in tokens:
                normalized.append({
                    "category": t.get("category", ""),
                    "symbol": t.get("symbol", ""),
                    "name": t.get("name", "Unknown Token"),
                    "decimals": int(t.get("decimals", 0)),
                    "balance": float(t.get("balance", 0))
                })
            return normalized
        except (json.JSONDecodeError, KeyError):
            return []
