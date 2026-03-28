#!/usr/bin/env python3
"""
Agente: Dataset Marketplace

Este agente vende datasets curados para entrenamiento de IA a cambio de BCH.

Features:
- Listar datasets disponibles
- Crear factura por dataset
- Entregar enlace de descarga tras pago
- Historial de compras por usuario
"""

import os
import json
from typing import Dict, List

from bch_pay_client import BCHPay, BCHPayError

pay = BCHPay(network=os.getenv("BCH_NETWORK", "testnet"))

# Catálogo simulado de datasets
DATASETS = {
    "reddit-qa": {
        "name": "Reddit Q&A Dataset",
        "description": "100k preguntas y respuestas de Reddit (formato JSONL)",
        "price": 0.05,
        "size": "500 MB",
        "format": "jsonl",
        "license": "CC BY-SA 4.0"
    },
    "code-python": {
        "name": "Python Code Corpus",
        "description": "1M de snippets de código Python con comentarios",
        "price": 0.1,
        "size": "2 GB",
        "format": "json",
        "license": "MIT"
    },
    "medical-qa": {
        "name": "Medical Q&A",
        "description": "Dataset de preguntas médicas con respuestas validadas por doctores",
        "price": 0.25,
        "size": "300 MB",
        "format": "csv",
        "license": "Research Only"
    }
}

# Registro de compras
purchases = {}


def list_datasets() -> List[Dict]:
    """Lista todos los datasets disponibles."""
    return [
        {
            "id": ds_id,
            **DATASETS[ds_id],
            "price_bch": DATASETS[ds_id]["price"]
        }
        for ds_id in DATASETS
    ]


def buy_dataset(ds_id: str, user_id: str) -> Optional[Dict]:
    """Crea factura para comprar dataset."""
    if ds_id not in DATASETS:
        return None

    dataset = DATASETS[ds_id]
    invoice = pay.create_invoice(
        amount=dataset["price"],
        description=f"Dataset: {dataset['name']}",
        metadata={
            "type": "dataset",
            "dataset_id": ds_id,
            "user_id": user_id
        }
    )

    # Registrar compra pendiente
    purchases[invoice.id] = {
        "dataset_id": ds_id,
        "user_id": user_id,
        "invoice_id": invoice.id,
        "status": "pending"
    }

    return {
        "invoice": invoice,
        "dataset": dataset,
        "download_url": f"/download/{invoice.id}"  # Protegido tras pago
    }


def check_and_deliver(invoice_id: str) -> Optional[str]:
    """Verifica pago y entrega el dataset si corresponde."""
    if invoice_id not in purchases:
        return None

    purchase = purchases[invoice_id]
    invoice = pay.get_invoice(invoice_id)

    if not invoice:
        return None

    if not pay.check_payment(invoice.id):
        return "pending"

    # Pago confirmado
    purchase["status"] = "delivered"
    purchase["delivered_at"] = __import__('time').time()

    # En producción, aquí generarías un enlace temporal firmado
    ds_id = purchase["dataset_id"]
    return f"✅_dataset_delivered:{ds_id}:{invoice_id}"


def get_user_purchases(user_id: str) -> List[Dict]:
    """Obtiene historial de compras de un usuario."""
    user_purchases = []
    for inv_id, purchase in purchases.items():
        if purchase["user_id"] == user_id:
            invoice = pay.get_invoice(inv_id)
            user_purchases.append({
                **purchase,
                "invoice": invoice,
                "status": "delivered" if check_and_deliver(inv_id) else "pending"
            })
    return user_purchases


if __name__ == "__main__":
    print("🗃️  Dataset Marketplace Agent")
    print(f"💰 Balance: {pay.total_earned():.6f} BCH\n")
    print("Datasets disponibles:")

    for ds in list_datasets():
        print(f"\n📦 {ds['id']}: {ds['name']}")
        print(f"   💰 {ds['price_bch']} BCH")
        print(f"   📝 {ds['description']}")
        print(f"   📊 {ds['size']}, {ds['format']}")

    # Ejemplo de compra
    print("\n\n🧪 Ejemplo de compra:")
    result = buy_dataset("code-python", "user_test_001")
    if result:
        print(f"✅ Factura creada: {result['invoice'].id[:12]}...")
        print(f"🔗 Pagar en: {pay.get_payment_url(result['invoice'].id)}")