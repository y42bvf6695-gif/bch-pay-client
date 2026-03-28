"""
BCHPay - Bitcoin Cash payment client for AI agents.

This module provides the main BCHPay class that orchestrates payment operations
through a pluggable backend system (demo, paytaca, watchtower, etc.).
"""

import json
import uuid
import time
from pathlib import Path
from typing import Optional, Dict, Any, List

from .exceptions import BCHPayError, InsufficientAmount
from .backends import BCHBackend, DemoBackend, Invoice, PaytacaBackend


class BCHPay:
    """
    Cliente para pagos Bitcoin Cash con backend configurable.

    Attributes:
        storage_path: Ruta al archivo JSON de almacenamiento local
        network: Red de BCH ('mainnet' o 'testnet')
        backend: Instancia del backend activo (DemoBackend, PaytacaBackend, etc.)
        explorer_url: URL del explorador de bloques (para get_payment_url)
    """

    def __init__(
        self,
        storage_path: Optional[str] = None,
        network: str = "mainnet",
        backend: Optional[str] = None,
        paytaca_cli: str = "paytaca",
        bch_node_url: Optional[str] = None,  # kept for compatibility
        explorer_url: Optional[str] = None,
        **backend_kwargs
    ):
        """
        Inicializa el cliente BCHPay.

        Args:
            storage_path: Ruta personalizada para almacenamiento local de facturas
            network: 'mainnet' o 'testnet'
            backend: Backend a usar ('demo', 'paytaca', 'watchtower'). Si None, se autodetecta.
            paytaca_cli: Ruta al ejecutable de paytaca (solo para backend='paytaca')
            bch_node_url: (Deprecated) URL de nodo BCH JSON-RPC - no usado actualmente
            explorer_url: URL base del explorador de bloques (para get_payment_url)
            **backend_kwargs: Argumentos adicionales para el backend

        Backend Selection:
        - 'demo': Simulación local (default si no hay paytaca instalado)
        - 'paytaca': Usa Paytaca CLI (requiere Node.js + paytaca-cli)
        - 'watchtower': Usa Watchtower.cash API directa (próximamente)

        Environment Variables:
        - BCH_BACKEND: Fuerza backend específico
        - PAYTACA_CLI: Ruta personalizada a paytaca
        """
        self.network = network
        self.storage_path = Path(storage_path or Path.home() / ".bch_pay.json")
        self.bch_node_url = bch_node_url  # kept for backwards compatibility
        self.explorer_url = explorer_url or {
            "mainnet": "https://explorer.bitcoin.com/bch",
            "testnet": "https://explorer.bitcoin.com/testnet"
        }.get(network, "https://explorer.bitcoin.com/bch")

        # Local invoice cache
        self._invoices: Dict[str, Dict[str, Any]] = {}

        # Select backend
        backend = backend or self._autodetect_backend()
        self.backend = self._create_backend(
            backend,
            paytaca_cli=paytaca_cli,
            network=network,
            storage_path=str(self.storage_path),
            **backend_kwargs
        )

        # Load local invoice cache (works across backends)
        self._load()

    def _autodetect_backend(self) -> str:
        """Auto-detect available backend."""
        import shutil
        if shutil.which("paytaca") is not None:
            return "paytaca"
        return "demo"

    def _create_backend(
        self,
        backend_name: str,
        **kwargs
    ) -> BCHBackend:
        """Instantiate the selected backend."""
        if backend_name == "demo":
            return DemoBackend(
                storage_path=kwargs.get("storage_path"),
                network=kwargs.get("network", "mainnet")
            )
        elif backend_name == "paytaca":
            return PaytacaBackend(
                paytaca_cli=kwargs.get("paytaca_cli", "paytaca"),
                network=kwargs.get("network", "mainnet"),
                storage_path=kwargs.get("storage_path")
            )
        elif backend_name == "watchtower":
            # Placeholder for future implementation
            raise NotImplementedError("Watchtower backend not yet implemented")
        else:
            raise ValueError(f"Unknown backend: {backend_name}. Use 'demo' or 'paytaca'")

    def _load(self) -> None:
        """Carga las facturas desde el almacenamiento local."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    self._invoices = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._invoices = {}

    def _save(self) -> None:
        """Guarda las facturas en el almacenamiento local."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self._invoices, f, indent=2)

    def create_invoice(
        self,
        amount: float,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
        token_category: Optional[str] = None
    ) -> Invoice:
        """
        Crea una nueva factura de pago (BCH o token).

        Args:
            amount: Cantidad en BCH o unidades de token
            description: Descripción del pago
            metadata: Datos adicionales opcionales
            token_category: ID de categoría CashToken (64 hex chars). Si se omite, es BCH.

        Returns:
            Invoice: Objeto de factura creada

        Raises:
            BCHPayError: Si el monto es inválido o falla el backend
        """
        if amount <= 0:
            raise InsufficientAmount("El monto debe ser mayor a 0")

        try:
            invoice = self.backend.create_invoice(
                amount, description, metadata, token_category
            )

            # Cache invoice locally
            self._invoices[invoice.id] = invoice.to_dict()
            self._save()

            return invoice
        except Exception as e:
            raise BCHPayError(f"Failed to create invoice: {str(e)}")

    def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        """
        Obtiene una factura por su ID.

        First checks local cache, falls back to backend if needed.
        """
        # Try local cache first
        data = self._invoices.get(invoice_id)
        if data:
            return Invoice(**data)

        # Backend might have it even if not in local cache
        invoice = self.backend.get_invoice(invoice_id)
        if invoice:
            # Update local cache
            self._invoices[invoice_id] = invoice.to_dict()
            self._save()

        return invoice

    def check_payment(self, invoice_id: str) -> bool:
        """
        Verifica si una factura ha sido pagada.

        Args:
            invoice_id: ID de la factura

        Returns:
            bool: True si está pagada con al menos 1 confirmación

        Raises:
            BCHPayError: Si falla la verificación en el backend
        """
        invoice = self.get_invoice(invoice_id)
        if not invoice:
            return False

        if invoice.paid:
            return True

        try:
            is_paid = self.backend.check_payment(invoice_id)
            if is_paid:
                # Update local cache
                updated = self.backend.get_invoice(invoice_id)
                if updated and updated.paid:
                    self._invoices[invoice_id] = updated.to_dict()
                    self._save()
            return is_paid
        except Exception as e:
            raise BCHPayError(f"Failed to check payment: {str(e)}")

    def get_balance(self, token_category: Optional[str] = None) -> float:
        """
        Obtiene el balance del wallet.

        Args:
            token_category: Si se especifica, devuelve balance de ese token.
                          Si None, devuelve balance BCH.

        Returns:
            float: Balance en BCH o unidades de token
        """
        try:
            # Backends nuevos soportan token_category
            return self.backend.get_balance(token_category=token_category)
        except TypeError:
            # Backend antiguo sin soporte token_category
            if token_category:
                return 0.0
            return self.backend.get_balance()
        except Exception as e:
            raise BCHPayError(f"Failed to get balance: {str(e)}")

    def list_tokens(self) -> List[Dict[str, Any]]:
        """
        Lista todos los CashTokens en el wallet.

        Returns:
            Lista de dicts con: category, symbol, name, decimals, balance
        """
        try:
            return self.backend.list_tokens()
        except AttributeError:
            # Backend no soporta tokens
            return []

    def list_invoices(self, limit: int = 100) -> list[Invoice]:
        """Lista todas las facturas (últimas primero)."""
        try:
            # Prefer backend list (it may have invoices not in local cache)
            invoices = self.backend.list_invoices(limit=limit)

            # Merge with local (more complete metadata)
            local_invoices = [
                Invoice(**data) for data in self._invoices.values()
            ]
            # Combine and dedupe by ID (prefer backend data if paid status differs)
            combined = {}
            for inv in invoices + local_invoices:
                combined[inv.id] = inv

            return sorted(combined.values(), key=lambda x: x.created_at, reverse=True)[:limit]
        except Exception as e:
            raise BCHPayError(f"Failed to list invoices: {str(e)}")

    def total_earned(self) -> float:
        """Retorna el total de BCH recibidos (desde facturas pagadas)."""
        return sum(
            inv.amount for inv in self.list_invoices()
            if inv.paid
        )

    def send_payment(
        self,
        address: str,
        amount: float,
        token_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envía un pago (BCH o CashToken).

        Args:
            address: Dirección destinatario
            amount: Cantidad
            token_category: ID de categoría token (si es token payment)

        Returns:
            dict con keys: success (bool), txid (str, opcional), error (str, opcional)
        """
        try:
            return self.backend.send_payment(address, amount, token_category)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_payment_url(self, invoice_id: str) -> str:
        """Genera URL de pago (requiere explorer_url configurado)."""
        invoice = self.get_invoice(invoice_id)
        if not invoice:
            raise BCHPayError("Factura no encontrada")

        return f"{self.explorer_url}/address/{invoice.address}"

    def generate_qr(self, invoice_id: str, size: int = 300) -> bytes:
        """
        Genera un código QR para la dirección de pago.

        Args:
            invoice_id: ID de la factura
            size: Tamaño en píxeles

        Returns:
            bytes: Imagen PNG en bytes

        Raises:
            BCHPayError: Si no se encuentra la factura o falta qrcode
        """
        invoice = self.get_invoice(invoice_id)
        if not invoice:
            raise BCHPayError("Factura no encontrada")

        try:
            import qrcode
            from io import BytesIO
        except ImportError:
            raise BCHPayError("Instala 'qrcode' y 'pillow' para generar QR codes")

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(invoice.address)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize((size, size))

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()
