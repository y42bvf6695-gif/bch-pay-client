# API Reference

## BCHPay Class

```python
from bch_pay_client import BCHPay, Invoice, Payment
```

### Constructor

```python
BCHPay(
    storage_path: Optional[str] = None,
    network: str = "testnet",
    bch_node_url: Optional[str] = None,
    explorer_url: Optional[str] = None
)
```

**Args:**
- `storage_path`: Ruta al archivo JSON para almacenamiento local de facturas (default: `~/.bch_pay.json`)
- `network`: `'testnet'` o `'mainnet'`
- `bch_node_url`: URL del nodo BCH JSON-RPC (opcional, para verificación real)
- `explorer_url`: URL base del explorador de bloques BCH

---

### Métodos principales

#### `create_invoice(amount: float, description: str, metadata: Optional[Dict] = None) -> Invoice`

Crea una nueva factura de pago.

**Params:**
- `amount`: Cantidad en BCH (debe ser > 0)
- `description`: Descripción del pago (max 200 caracteres)
- `metadata`: Datos adicionales (ej: user_id, order_id)

**Returns:** `Invoice` object

**Raises:** `InsufficientAmount` si amount <= 0

---

#### `get_invoice(invoice_id: str) -> Optional[Invoice]`

Obtiene una factura por su UUID.

**Returns:** `Invoice` o `None` si no existe.

---

#### `check_payment(invoice_id: str) -> bool`

Verifica si una factura fue pagada (al menos 1 confirmación).

**Returns:** `True` si pagada, `False` en otro caso.

**Note:** En modo demo (sin `bch_node_url`), simula verificación después de 5 segundos.

---

#### `get_payment_url(invoice_id: str) -> str`

Genera URL de pago para redirigir al usuario al explorador.

**Returns:** URL string.

---

#### `generate_qr(invoice_id: str, size: int = 300) -> bytes`

Genera imagen PNG de código QR para la dirección.

**Requires:** `pip install bch-pay-client[qr]`

**Returns:** Bytes PNG.

---

#### `list_invoices(limit: int = 100) -> List[Invoice]`

Lista facturas, ordenadas por fecha descendente.

**Params:** `limit` - máximo número a devolver.

---

#### `total_earned() -> float`

Retorna total de BCH ganados (suma de facturas pagadas).

---

## Data Models

### Invoice

```python
@dataclass
class Invoice:
    id: str                    # UUID
    amount: float              # BCH amount
    description: str           # Descripción
    address: str               # Dirección BCH (CashAddr)
    created_at: float          # Timestamp Unix
    paid: bool = False
    paid_at: Optional[float] = None
    txid: Optional[str] = None
    confirmations: int = 0
    metadata: Optional[Dict[str, Any]] = None
```

---

## Exceptions

- `BCHPayError` - Base exception
- `InsufficientAmount` - Monto inválido (<= 0)
- `InvalidAddress` - Dirección BCH inválida
- `PaymentNotFound` - Factura no encontrada

---

## Ejemplos

### FastAPI

```python
from fastapi import FastAPI, HTTPException
from bch_pay_client import BCHPay

app = FastAPI()
pay = BCHPay()

@app.post("/invoices")
async def create(amount: float, description: str):
    invoice = pay.create_invoice(amount, description)
    return {
        "invoice_id": invoice.id,
        "address": invoice.address,
        "payment_url": pay.get_payment_url(invoice.id),
        "qr": base64.b64encode(pay.generate_qr(invoice.id)).decode()
    }

@app.get("/invoices/{invoice_id}/status")
async def status(invoice_id: str):
    invoice = pay.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(404, "Not found")
    return {
        "paid": pay.check_payment(invoice_id),
        "amount": invoice.amount
    }
```

### Discord Bot

```python
import discord
from discord.ext import commands
from bch_pay_client import BCHPay

bot = commands.Bot(command_prefix="!")
pay = BCHPay()

@bot.command()
async def pay(ctx, amount: float, *, desc: str = "Servicio IA"):
    invoice = pay.create_invoice(amount, f"{ctx.author}: {desc}")
    await ctx.send(
        f"Paga {amount} BCH a: {invoice.address}\n"
        f"URL: {pay.get_payment_url(invoice.id)}"
    )
```

### Telegram Bot

```python
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from bch_pay_client import BCHPay

pay = BCHPay()

async def invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount = float(context.args[0])
    invoice = pay.create_invoice(amount, "Telegram bot payment")
    keyboard = [[InlineKeyboardButton("Pagar", url=pay.get_payment_url(invoice.id))]]
    await update.message.reply_text(
        f"Factura: {invoice.id}\nDirección: {invoice.address}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
```

---

## Storage Format

Las facturas se guardan en JSON:

```json
{
  "uuid-here": {
    "id": "uuid-here",
    "amount": 0.01,
    "description": "Mi pago",
    "address": "bitcoincash:qz...",
    "created_at": 1704067200.0,
    "paid": true,
    "paid_at": 1704067210.0,
    "txid": "abc123...",
    "confirmations": 1,
    "metadata": {"user_id": "123"}
  }
}
```

Backups manuales recomendados en producción.

---

## Production Checklist

- [ ] Usar `network="mainnet"`
- [ ] Configurar `bch_node_url` con tu propio nodo o servicio confiable
- [ ] Hacer backups de `storage_path` periódicamente
- [ ] Usar HTTPS para APIs/webhooks
- [ ] Rate limiting en endpoints públicos
- [ ] Logging de todas las transacciones
- [ ] Monitoreo de balance y facturas pendientes
- [ ] Rotación de fondos a cold wallet periódicamente

---

¿Preguntas? Abre un issue en GitHub.