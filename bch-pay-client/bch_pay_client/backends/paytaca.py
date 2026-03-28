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
import shlex
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
                raise RuntimeError(f"Paytaca error: {result.stderr}")
            return {"success": True, "output": result.stdout}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Paytaca command timed out"}

    def _get_or_create_address_index(self) -> int:
        """
        Determine next address index to use.
        For simplicity, we'll derive a new index based on invoice count.
        """
        return len(self._invoices)

    def create_invoice(
        self,
        amount: float,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Invoice:
        """Create a new invoice with a real BCH address from Paytaca."""
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")

        invoice_id = str(uuid.uuid4())

        # Get a receiving address from Paytaca
        index = self._get_or_create_address_index()
        result = self._run_paytaca(["receive", "--no-qr", f"--index={index}"])
        if not result["success"]:
            raise RuntimeError(f"Failed to get address: {result.get('error')}")

        # Parse address from output (look for "Address:  <address>")
        address = None
        for line in result["output"].split("\n"):
            if line.strip().startswith("Address:"):
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
            metadata=metadata or {},
        )

        # Store with the address index used (for later verification)
        invoice_data = invoice.to_dict()
        invoice_data["address_index"] = index
        self._invoices[invoice_id] = invoice_data
        self._save()

        return invoice

    def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        """Get invoice from local storage."""
        data = self._invoices.get(invoice_id)
        if data:
            return Invoice(**{k: v for k, v in data.items() if k != "address_index"})
        return None

    def check_payment(self, invoice_id: str) -> bool:
        """
        Check payment by scanning Paytaca history for a transaction
        that pays to the invoice's address with the expected amount.
        """
        invoice_data = self._invoices.get(invoice_id)
        if not invoice_data:
            return False

        if invoice_data.get("paid", False):
            return True

        # Fetch history from Paytaca
        result = self._run_paytaca(["history", "--json"])
        if not result["success"]:
            return False

        try:
            # Paytaca history --json outputs JSON lines or full JSON?
            history = json.loads(result["output"])
        except json.JSONDecodeError:
            # Maybe it's NDJSON? Try parsing line by line
            history = []
            for line in result["output"].strip().split("\n"):
                try:
                    history.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        # Look for a transaction that:
        # - Is incoming (record_type == "incoming")
        # - The recipients include our address
        # - Amount >= invoice amount (allow overpayment)
        expected_amount = invoice_data["amount"]
        target_address = invoice_data["address"]

        for tx in history:
            if tx.get("record_type") != "incoming":
                continue

            # Check if any recipient matches our address
            recipients = tx.get("recipients", [])
            for recipient in recipients:
                if recipient.get("address") == target_address:
                    tx_amount = float(recipient.get("amount", 0))
                    if tx_amount >= expected_amount - 1e-8:  # Float tolerance
                        # Payment found!
                        invoice_data["paid"] = True
                        invoice_data["paid_at"] = time.time()
                        invoice_data["txid"] = tx.get("txid")
                        invoice_data["confirmations"] = tx.get("confirmations", 1)
                        self._invoices[invoice_id] = invoice_data
                        self._save()
                        return True

        return False

    def get_balance(self) -> float:
        """
        Get wallet balance from Paytaca.
        Note: This returns TOTAL wallet balance, not just invoices.
        For invoice-specific earnings, use BCHPay.total_earned() which sums paid invoices.
        """
        result = self._run_paytaca(["balance"])
        if not result["success"]:
            return 0.0

        # Parse balance from output (e.g., "Balance: 0.123 BCH")
        output = result["output"]
        try:
            # Look for a line with BCH amount
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
        invoices = [
            Invoice(**{k: v for k, v in data.items() if k != "address_index"})
            for data in self._invoices.values()
        ]
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
                # Try to extract txid from output
                txid = None
                for line in result["output"].split("\n"):
                    if line.startswith("txid:") or "txid" in line.lower():
                        txid = line.split(":")[1].strip() if ":" in line else line.strip()
                        break
                return {"success": True, "txid": txid}
            else:
                return {"success": False, "error": result.get("error", "Unknown error")}
        except Exception as e:
            return {"success": False, "error": str(e)}
