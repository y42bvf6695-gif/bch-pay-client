"""Excepciones personalizadas de bch_pay_client."""


class BCHPayError(Exception):
    """Base exception for BCHPay errors."""
    pass


class InsufficientAmount(BCHPayError):
    """El monto de la factura es inválido."""
    pass


class InvalidAddress(BCHPayError):
    """La dirección BCH proporcionada no es válida."""
    pass


class PaymentNotFound(BCHPayError):
    """El pago o factura no existe."""
    pass