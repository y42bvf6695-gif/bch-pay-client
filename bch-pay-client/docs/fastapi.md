# Integración con FastAPI

Guía completa para integrar BCHPay en tu aplicación FastAPI.

## Instalación

```bash
pip install bch-pay-client[web]
```

## Ejemplo básico

```python
from fastapi import FastAPI, HTTPException, Depends
from bch_pay_client import BCHPay, BCHPayError
import uvicorn

app = FastAPI()
pay = BCHPay(network="testnet")

@app.post("/invoices")
async def create_invoice(amount: float, description: str, user_id: str = None):
    try:
        invoice = pay.create_invoice(
            amount=amount,
            description=description,
            metadata={"user_id": user_id} if user_id else None
        )
        return {
            "invoice_id": invoice.id,
            "address": invoice.address,
            "payment_url": pay.get_payment_url(invoice.id),
            "qr_code": pay.generate_qr(invoice.id)  # bytes PNG
        }
    except BCHPayError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str):
    invoice = pay.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@app.post("/invoices/{invoice_id}/check")
async def check_invoice(invoice_id: str):
    is_paid = pay.check_payment(invoice_id)
    invoice = pay.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {
        "paid": invoice.paid,
        "confirmations": invoice.confirmations,
        "txid": invoice.txid
    }

@app.get("/balance")
async def get_balance():
    return {"total_earned_bch": pay.total_earned()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Middleware para autenticación

```python
from fastapi import Request, HTTPException, Depends
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != "tu-secret-key":
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

@app.post("/invoices")
async def create_invoice(
    amount: float,
    description: str,
    api_key: str = Depends(verify_api_key)
):
    # ...
```

## Webhook endpoint

```python
from pydantic import BaseModel

class PaymentWebhook(BaseModel):
    event: str
    invoice_id: str
    amount: float
    txid: str
    paid_at: float

@app.post("/webhook/payment")
async def payment_webhook(data: PaymentWebhook, request: Request):
    # Verificar firma (opcional pero recomendado)
    signature = request.headers.get("X-BCH-Signature")
    # TODO: verificar firma con tu clave secreta

    if data.event == "payment.received":
        invoice = pay.get_invoice(data.invoice_id)
        if invoice:
            # Entregar producto/servicio
            grant_access_to_user(invoice.metadata.get("user_id"))
            # Enviar email/telegram通知

    return {"status": "ok"}
```

## Protección CSRF

Si tu endpoint modifica estado (pagos), usa CORS:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tu-frontend.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Rate limiting

Con `slowapi`:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

@app.post("/invoices")
@limiter.limit("5/minute")
async def create_invoice(...):
    # ...
```

## Deploy

```bash
#构建 Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

Best practices:
- Mantén `pay` como variable global o usa `Depends(lambda: pay)`
- Backup de `storage_path` en volume montado (no en container ephemeral)
- Usa `mainnet` solo con nodo BCH propio (no nodos públicos)
- Logs estructurados (JSON) para debugging