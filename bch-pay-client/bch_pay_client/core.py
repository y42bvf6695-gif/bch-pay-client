import json
import uuid
import time
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from pathlib import Path
import requests

from .exceptions import BCHPayError, InsufficientAmount, InvalidAddress


@dataclass
class Invoice:
    """Representa una factura de pago en BCH."""
    id: str
    amount: float  # en BCH
    description: str
    address: str
    created_at: float
    paid: bool = False
    paid_at: Optional[float] = None
    txid: Optional[str] = None
    confirmations: int = 0
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Payment:
    """Representa un pago recibido."""
    invoice_id: str
    amount: float
    txid: str
    confirmations: int
    timestamp: float


class BCHPay:
    """
    Cliente para pagos Bitcoin Cash.

    Attributes:
        storage_path: Ruta al archivo JSON de almacenamiento local (por defecto: ~/.bch_pay.json)
        network: Red de BCH ('mainnet' o 'testnet')
        explorer_url: URL del explorador de bloques para verificar transacciones
    """

    def __init__(
        self,
        storage_path: Optional[str] = None,
        network: str = "mainnet",
        bch_node_url: Optional[str] = None,
        explorer_url: Optional[str] = None,
    ):
        """
        Inicializa el cliente BCHPay.

        Args:
            storage_path: Ruta personalizada para almacenamiento local
            network: 'mainnet' o 'testnet'
            bch_node_url: URL de un nodo BCH JSON-RPC (opcional, para verificación real)
            explorer_url: URL base del explorador de bloques (ej: https://explorer.bitcoin.com/bch)
        """
        self.network = network
        self.storage_path = Path(storage_path or Path.home() / ".bch_pay.json")
        self.bch_node_url = bch_node_url
        self.explorer_url = explorer_url or {
            "mainnet": "https://explorer.bitcoin.com/bch",
            "testnet": "https://explorer.bitcoin.com/testnet"
        }.get(network, "https://explorer.bitcoin.com/bch")

        # Cargar datos existentes
        self._invoices: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        """Carga las facturas desde el almacenamiento local."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    self._invoices = json.load(f)
            except json.JSONDecodeError:
                self._invoices = {}

    def _save(self) -> None:
        """Guarda las facturas en el almacenamiento local."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self._invoices, f, indent=2)

    def _generate_address(self) -> str:
        """
        Genera una dirección BCH.

        En un entorno real, esto debería conectar con un wallet real.
        Por ahora, genera direcciones de testnet válidas en formato CashAddr para pruebas.
        """
        # Generar una dirección de testnet válida (comienza con 'bchtest:')
        # Esto es SOLO para demostración. En producción, usa un wallet real.
        import random
        prefix = "bchtest:" if self.network == "testnet" else "bitcoincash:"
        random_part = ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=70))
        return f"{prefix}{random_part}"

    def _is_valid_bch_address(self, address: str) -> bool:
        """Validación básica de dirección BCH."""
        # Chequeo simple: debe comenzar con bitcoincash: o bchtest:
        return address.startswith(("bitcoincash:", "bchtest:"))

    def create_invoice(
        self,
        amount: float,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Invoice:
        """
        Crea una nueva factura de pago.

        Args:
            amount: Cantidad en BCH (ej: 0.01)
            description: Descripción del pago
            metadata: Datos adicionales opcionales

        Returns:
            Invoice: Objeto de factura creada

        Raises:
            InsufficientAmount: Si el monto es menor o igual a 0
        """
        if amount <= 0:
            raise InsufficientAmount("El monto debe ser mayor a 0")

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
        """Obtiene una factura por su ID."""
        data = self._invoices.get(invoice_id)
        if data:
            return Invoice(**data)
        return None

    def check_payment(self, invoice_id: str) -> bool:
        """
        Verifica si una factura ha sido pagada.

        Args:
            invoice_id: ID de la factura

        Returns:
            bool: True si está pagada con al menos 1 confirmación

        Note:
            En modo demo, esto simula verificación.
            Para verificación real, configura `bch_node_url`.
        """
        invoice = self.get_invoice(invoice_id)
        if not invoice:
            return False

        if invoice.paid:
            return True

        # Si se proporcionó un nodo BCH, consultar transacciones reales
        if self.bch_node_url:
            return self._check_payment_real(invoice)

        # Modo demo: simular verificación
        return self._check_payment_demo(invoice)

    def _check_payment_real(self, invoice: Invoice) -> bool:
        """Consulta el nodo BCH para verificar transacciones."""
        try:
            # Aquí implementarías la llamada JSON-RPC a tu nodo
            # Ejemplo conceptual:
            # response = requests.post(self.bch_node_url, json={
            #     "method": "getaddressinfo",
            #     "params": [invoice.address]
            # })
            # Verificar si hay UTXOs no gastados que sumen >= invoice.amount
            pass
        except Exception:
            return False
        return False

    def _check_payment_demo(self, invoice: Invoice) -> bool:
        """
        Simulación de verificación de pago.
        Para pruebas: automáticamente marca como pagada después de 5 segundos.
        """
        # En un demo, podrías simular que el pago arrive después de un tiempo
        if not invoice.paid and (time.time() - invoice.created_at) > 5:
            invoice.paid = True
            invoice.paid_at = time.time()
            invoice.txid = f"demo-tx-{uuid.uuid4().hex[:16]}"
            invoice.confirmations = 1
            self._invoices[invoice.id] = invoice.to_dict()
            self._save()
            return True
        return False

    def get_payment_url(self, invoice_id: str) -> str:
        """Genera URL de pago (para redirigir al usuario)."""
        invoice = self.get_invoice(invoice_id)
        if not invoice:
            raise BCHPayError("Factura no encontrada")

        # En producción, esto sería el URL de tu checkout o dirección directa
        return f"{self.explorer_url}/address/{invoice.address}"

    def generate_qr(self, invoice_id: str, size: int = 300) -> bytes:
        """
        Genera un código QR para la dirección de pago.

        Args:
            invoice_id: ID de la factura
            size: Tamaño en píxeles

        Returns:
            bytes: Imagen PNG en bytes
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

    def list_invoices(self, limit: int = 100) -> list[Invoice]:
        """Lista todas las facturas (últimas primero)."""
        invoices = [
            Invoice(**data)
            for data in self._invoices.values()
        ]
        return sorted(invoices, key=lambda x: x.created_at, reverse=True)[:limit]

    def total_earned(self) -> float:
        """Retorna el total de BCH recibidos."""
        return sum(
            inv.amount for inv in self.list_invoices()
            if inv.paid
        )
