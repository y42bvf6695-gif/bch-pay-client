"""
Demo backend for bch-pay-client.

Simulates BCH payments for testing/development.
- Auto-approves invoices after 5 seconds
- No real blockchain interaction
- Uses local JSON storage
"""

import json
import time
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List

from .base import BCHBackend, Invoice


class DemoBackend(BCHBackend):
    """Demo backend with simulated payments."""

    def __init__(self, storage_path: Optional[str] = None, network: str = "testnet"):
        """
        Initialize demo backend.

        Args:
            storage_path: Path to JSON storage file
            network: 'testnet' or 'mainnet' (informational only in demo)
        """
        self.network = network
        self.storage_path = Path(storage_path or Path.home() / ".bch_pay.json")
        self._invoices: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        """Load invoices from storage."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    self._invoices = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._invoices = {}

    def _save(self) -> None:
        """Save invoices to storage."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self._invoices, f, indent=2)

    def _generate_address(self) -> str:
        """Generate a fake BCH address."""
        import random
        prefix = "bchtest:" if self.network == "testnet" else "bitcoincash:"
        random_part = ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=70))
        return f"{prefix}{random_part}"

    def create_invoice(
        self,
        amount: float,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Invoice:
        """Create a new invoice."""
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")

        invoice_id = str(uuid.uuid4())
        address = self._generate_address()

        invoice = Invoice(
            id=invoice_id,
            amount=amount,
            description=description,
            address=address,
            created_at=time.time(),
            metadata=metadata or {}
        )

        self._invoices[invoice_id] = invoice.to_dict()
        self._save()

        return invoice

    def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        """Get invoice by ID."""
        data = self._invoices.get(invoice_id)
        if data:
            return Invoice(**data)
        return None

    def check_payment(self, invoice_id: str) -> bool:
        """Check if invoice is paid (auto-approves after 5s in demo)."""
        invoice = self.get_invoice(invoice_id)
        if not invoice:
            return False

        if invoice.paid:
            return True

        # Demo mode: auto-approve after 5 seconds
        if (time.time() - invoice.created_at) > 5:
            invoice.paid = True
            invoice.paid_at = time.time()
            invoice.txid = f"demo-tx-{uuid.uuid4().hex[:16]}"
            invoice.confirmations = 1
            self._invoices[invoice_id] = invoice.to_dict()
            self._save()
            return True

        return False

    def get_balance(self) -> float:
        """Calculate total earned from paid invoices."""
        return sum(
            inv.amount for inv in self.list_invoices()
            if inv.paid
        )

    def list_invoices(self, limit: int = 100) -> List[Invoice]:
        """List all invoices, newest first."""
        invoices = [Invoice(**data) for data in self._invoices.values()]
        return sorted(invoices, key=lambda x: x.created_at, reverse=True)[:limit]

    def send_payment(
        self,
        address: str,
        amount: float,
        token_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Demo: simulate sending (not implemented)."""
        return {
            "success": False,
            "error": "Sending not supported in demo backend"
        }
