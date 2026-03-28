"""
Base backend interface and shared data classes.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any, List


@dataclass
class Invoice:
    """Invoice representation (backend-agnostic)."""
    id: str
    amount: float
    description: str
    address: str
    created_at: float
    paid: bool = False
    paid_at: Optional[float] = None
    txid: Optional[str] = None
    confirmations: int = 0
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "amount": self.amount,
            "description": self.description,
            "address": self.address,
            "created_at": self.created_at,
            "paid": self.paid,
            "paid_at": self.paid_at,
            "txid": self.txid,
            "confirmations": self.confirmations,
            "metadata": self.metadata or {}
        }


@dataclass
class Payment:
    """Payment received representation."""
    invoice_id: str
    amount: float
    txid: str
    confirmations: int
    timestamp: float


class BCHBackend(ABC):
    """Abstract base class for BCH payment backends."""

    @abstractmethod
    def create_invoice(
        self,
        amount: float,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
        token_category: Optional[str] = None
    ) -> Invoice:
        """Create a new payment invoice (BCH or token)."""
        pass

    @abstractmethod
    def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        """Retrieve an invoice by ID."""
        pass

    @abstractmethod
    def check_payment(self, invoice_id: str) -> bool:
        """Check if an invoice has been paid."""
        pass

    @abstractmethod
    def get_balance(self, token_category: Optional[str] = None) -> float:
        """Get wallet balance (BCH or specific token)."""
        pass

    @abstractmethod
    def list_invoices(self, limit: int = 100) -> List[Invoice]:
        """List all invoices."""
        pass

    @abstractmethod
    def list_tokens(self) -> List[Dict[str, Any]]:
        """List all CashTokens in wallet (symbol, category, balance, decimals)."""
        pass

    def send_payment(
        self,
        address: str,
        amount: float,
        token_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a payment (BCH or token).
        Returns dict with keys: success (bool), txid (str), error (str).
        """
        raise NotImplementedError("Sending not implemented in this backend")
