#!/usr/bin/env python3
"""
Agente API BCHPay - Servidor REST autónomo

Este agente:
- Acepta crear facturas
- Verifica pagos automáticamente
- Expone webhooks para notificaciones
- Puede funcionar como microservicio independiente
"""

import os
import json
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field
import uvicorn

from bch_pay_client import BCHPay, Invoice, BCHPayError

app = FastAPI(
    title="BCHPay Agent API",
    description="Agente autónomo para procesar pagos Bitcoin Cash",
    version="1.0.0"
)

# Instancia global del agente (configurable via env vars)
pay = BCHPay(
    network=os.getenv("BCH_NETWORK", "testnet"),
    storage_path=os.getenv("BCH_STORAGE_PATH", None)
)

# Almacenar webhooks registrados
webhooks: list[Dict[str, Any]] = []


class CreateInvoiceRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Cantidad en BCH")
    description: str = Field(..., min_length=1, max_length=200)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    callback_url: str = Field(None, description="URL para webhook (opcional)")


class InvoiceResponse(BaseModel):
    id: str
    amount: float
    description: str
    address: str
    payment_url: str
    qr_code_base64: str
    created_at: float
    paid: bool


@app.get("/")
async def root():
    """Información del agente."""
    return {
        "agent": "BCHPay API",
        "version": "1.0.0",
        "status": "active",
        "network": pay.network,
        "total_earned_bch": pay.total_earned(),
        "endpoints": {
            "POST /invoices": "Crear factura",
            "GET /invoices/{id}": "Obtener factura",
            "GET /invoices": "Listar facturas",
            "POST /invoices/{id}/check": "Verificar pago manual",
            "POST /webhooks": "Registrar webhook"
        }
    }


@app.get("/health")
async def health():
    """Health check para monitoreo."""
    return {"status": "healthy", "timestamp": __import__('time').time()}


@app.post("/invoices", response_model=InvoiceResponse)
async def create_invoice(req: CreateInvoiceRequest, background_tasks: BackgroundTasks):
    """Crea una nueva factura de pago."""
    try:
        invoice = pay.create_invoice(
            amount=req.amount,
            description=req.description,
            metadata=req.metadata
        )

        # Preparar respuesta
        response = InvoiceResponse(
            id=invoice.id,
            amount=invoice.amount,
            description=invoice.description,
            address=invoice.address,
            payment_url=pay.get_payment_url(invoice.id),
            qr_code_base64="data:image/png;base64," + __import__('base64').b64encode(
                pay.generate_qr(invoice.id)
            ).decode('utf-8'),
            created_at=invoice.created_at,
            paid=invoice.paid
        )

        # Si hay callback, programar verificación periódica en background
        if req.callback_url:
            background_tasks.add_task(
                schedule_payment_check,
                invoice.id,
                req.callback_url
            )

        return response

    except BCHPayError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@app.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str):
    """Obtiene detalles de una factura."""
    invoice = pay.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    return {
        "id": invoice.id,
        "amount": invoice.amount,
        "description": invoice.description,
        "address": invoice.address,
        "payment_url": pay.get_payment_url(invoice.id),
        "created_at": invoice.created_at,
        "paid": invoice.paid,
        "paid_at": invoice.paid_at,
        "txid": invoice.txid,
        "confirmations": invoice.confirmations,
        "metadata": invoice.metadata
    }


@app.get("/invoices")
async def list_invoices(limit: int = 50, paid_only: bool = False):
    """Lista facturas."""
    invoices = pay.list_invoices(limit=limit)
    if paid_only:
        invoices = [inv for inv in invoices if inv.paid]

    return {
        "invoices": [
            {
                "id": inv.id,
                "amount": inv.amount,
                "description": inv.description,
                "paid": inv.paid,
                "created_at": inv.created_at
            }
            for inv in invoices
        ],
        "total": len(invoices)
    }


@app.post("/invoices/{invoice_id}/check")
async def check_invoice(invoice_id: str):
    """Verifica manualmente si una factura fue pagada."""
    is_paid = pay.check_payment(invoice_id)
    invoice = pay.get_invoice(invoice_id)

    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    return {
        "paid": invoice.paid,
        "confirmations": invoice.confirmations,
        "txid": invoice.txid,
        "paid_at": invoice.paid_at
    }


async def schedule_payment_check(invoice_id: str, callback_url: str):
    """Programa verificación periódica y envía webhook cuando se pague."""
    import time
    import requests

    max_attempts = 30  # 30 intentos
    for attempt in range(max_attempts):
        if pay.check_payment(invoice_id):
            invoice = pay.get_invoice(invoice_id)
            # Enviar webhook
            try:
                resp = requests.post(callback_url, json={
                    "event": "payment.received",
                    "invoice_id": invoice_id,
                    "amount": invoice.amount,
                    "txid": invoice.txid,
                    "paid_at": invoice.paid_at
                }, timeout=5)
                print(f"Webhook enviado a {callback_url}: {resp.status_code}")
            except Exception as e:
                print(f"Error enviando webhook: {e}")
            break
        time.sleep(10)  # Revisar cada 10 segundos


@app.post("/webhooks")
async def register_webhook(request: Request):
    """Registra un webhook para notificaciones de pago."""
    data = await request.json()
    webhook_url = data.get("url")
    if not webhook_url:
        raise HTTPException(status_code=400, detail="URL requerida")

    webhooks.append({"url": webhook_url, "created_at": __import__('time').time()})
    return {"status": "registered", "total_webhooks": len(webhooks)}


# Si se ejecuta directamente
if __name__ == "__main__":
    host = os.getenv("BCHPAY_HOST", "0.0.0.0")
    port = int(os.getenv("BCHPAY_PORT", 8000))
    print(f"🚀 Iniciando BCHPay Agent API en http://{host}:{port}")
    print(f"📡 Red: {pay.network}")
    print(f"💾 Almacenamiento: {pay.storage_path}")
    uvicorn.run(app, host=host, port=port)