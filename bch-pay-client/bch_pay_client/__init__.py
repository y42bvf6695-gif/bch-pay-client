"""
bch_pay_client - Bitcoin Cash payments for AI agents
"""

from .core import BCHPay
from .backends.base import Invoice, Payment
from .exceptions import BCHPayError, InsufficientAmount, InvalidAddress, PaymentNotFound

__version__ = "0.1.0"
__all__ = [
    "BCHPay",
    "Invoice",
    "Payment",
    "BCHPayError",
    "InsufficientAmount",
    "InvalidAddress",
    "PaymentNotFound"
]