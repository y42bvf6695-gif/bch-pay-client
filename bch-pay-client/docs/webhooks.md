# Webhooks

Webhooks permiten recibir notificaciones automáticas cuando un pago se confirma, sin necesidad de polling.

## Configuración

```python
from bch_pay_client import BCHPay

pay = BCHPay()

# Crear factura con callback URL
invoice = pay.create_invoice(
    amount=0.01,
    description="Producto digital",
    metadata={"order_id": "12345"},
    callback_url="https://tu-servidor.com/webhooks/bch-payment"
)
```

## Payload del webhook

POST request con JSON:

```json
{
  "event": "payment.received",
  "invoice_id": "uuid-v4",
  "amount": 0.01,
  "txid": "bch-tx-hash",
  "paid_at": 1704067200.0,
  "signature": "hmac-sha256..."  // opcional si configuras secret
}
```

**Campos:**
- `event`: `payment.received`, `payment.failed`, `invoice.expired`
- `invoice_id`: UUID de la factura
- `amount`: monto en BCH
- `txid`: transaction ID en blockchain
- `paid_at`: timestamp Unix
- `signature`: HMAC-SHA256 del payload con tu secret (recomendado)

## Verificar firma (seguridad)

```python
import hmac
import hashlib

def verify_signature(payload: dict, signature: str, secret: str) -> bool:
    # Payload debe ordenarse keys alfabéticamente
    body = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    expected = hmac.new(
        secret.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

---

## Ejemplo FastAPI webhook

```python
from fastapi import FastAPI, Request, HTTPException
import hmac
import hashlib
import json

app = FastAPI()
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

@app.post("/webhooks/bch-payment")
async def bch_webhook(request: Request):
    payload = await request.json()
    signature = request.headers.get("X-BCH-Signature")

    # Verificar firma
    if not verify_signature(payload, signature, WEBHOOK_SECRET):
        raise HTTPException(401, "Invalid signature")

    event = payload["event"]

    if event == "payment.received":
        invoice_id = payload["invoice_id"]

        # Entregar producto/servicio
        deliver_product(invoice_id)

        # Notificar usuario via Telegram/email/etc
        send_notification(payload)

    elif event == "payment.failed":
        handle_failed_payment(payload)

    return {"status": "ok"}
```

---

## Webhook en agentes preconstruidos

Al crear factura via API:

```bash
POST /invoices
{
  "amount": 0.01,
  "description": "API call",
  "callback_url": "https://api.tu-app.com/bch-webhook"
}
```

El agente automáticamente:
1. Crea factura
2. Inicia hilo background que revisa cada 10s
3. Al pagar, envía POST a `callback_url`

---

## Manejo de failures

El agente reintenta hasta 3 veces con backoff exponencial.

Tu endpoint debe responder `200 OK` rápidamente. Si demora >5s, se reintenta.

Para colas durable:

```python
# En tu webhook:
if event == "payment.received":
    # 1. Guardar en cola (Redis/RabbitMQ)
    redis.rpush("bch_events", json.dumps(payload))
    # 2. Responder 200 inmediatamente
    return {"status": "queued"}
    # 3. Worker procesa cola asincrónicamente
```

---

## Ejemplo CLI listener

```python
import subprocess

# Escuchar factura específica
invoice_id = "abc..."

# Poll manual cada 30s
while True:
    result = subprocess.run(
        ["bchpay-cli", "check", invoice_id[:8]],
        capture_output=True
    )
    if b"PAGADA" in result.stdout:
        print("✅ Factura pagada!")
        break
    time.sleep(30)
```

---

## Troubleshooting

| Problema | Solución |
|----------|----------|
| Webhook no llega | Revisar firewall/ingress rules (HTTPS required) |
| Firma inválida | Ordenar keys alfabéticamente, usar mismo encoding |
| Duplicados | Idempotency: procesar solo una vez por `invoice_id` |
| Timeout | Respuesta <2s; procesar en background |

---

¿Necesitas ayuda? Abre un issue con tag `question`.