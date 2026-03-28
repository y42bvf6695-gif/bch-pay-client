#!/usr/bin/env python3
"""
Agente: Compute Rental (CPU/GPU genérico)

Similar a GPU rental pero más simple, para alquiler de cómputo general.

Features:
- Define paquetes precios (x tokens/min)
- Pago por uso en tiempo real
- Check-in automático y detención tras falta de pago
"""

import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict

from bch_pay_client import BCHPay

pay = BCHPay(network=os.getenv("BCH_NETWORK", "testnet"))

# Paquetes de cómputo
PACKAGES = {
    "basic-cpu": {
        "name": "Basic CPU Compute",
        "tokens_per_second": 100,
        "price_per_hour": 0.001,
        "min_hours": 0.5
    },
    "standard-gpu": {
        "name": "Standard GPU Compute",
        "tokens_per_second": 1000,
        "price_per_hour": 0.01,
        "min_hours": 0.5
    },
    "premium-gpu": {
        "name": "Premium GPU (A100)",
        "tokens_per_second": 5000,
        "price_per_hour": 0.05,
        "min_hours": 0.25
    }
}

# Sesiones activas
sessions = {}


def start_compute_session(
    package_id: str,
    user_id: str,
    hours: float
) -> Dict:
    """Inicia sesión de cómputo."""
    if package_id not in PACKAGES:
        raise ValueError("Paquete no válido")

    pkg = PACKAGES[package_id]
    if hours < pkg["min_hours"]:
        raise ValueError(f"Mínimo {pkg['min_hours']}h")

    amount = pkg["price_per_hour"] * hours

    invoice = pay.create_invoice(
        amount=amount,
        description=f"Compute: {pkg['name']} ({hours}h)",
        metadata={
            "type": "compute",
            "package_id": package_id,
            "user_id": user_id,
            "hours": hours
        }
    )

    session_id = str(uuid.uuid4())[:8]
    sessions[session_id] = {
        "session_id": session_id,
        "package_id": package_id,
        "user_id": user_id,
        "invoice_id": invoice.id,
        "duration_hours": hours,
        "status": "pending_payment",
        "created_at": time.time(),
        "started_at": None,
        "tokens_consumed": 0,
        "total_cost": amount
    }

    return {
        "session_id": session_id,
        "invoice": invoice,
        "package": pkg,
        "payment_url": pay.get_payment_url(invoice.id)
    }


def get_session_usage(session_id: str) -> Optional[Dict]:
    """Obtiene uso de una sesión."""
    if session_id not in sessions:
        return None

    s = sessions[session_id].copy()
    invoice = pay.get_invoice(s["invoice_id"])

    if invoice:
        s["paid"] = invoice.paid

    if s["status"] == "active":
        # Calcular tokens y costo actual
        if s["started_at"]:
            elapsed_hours = (time.time() - s["started_at"]) / 3600
            pkg = PACKAGES[s["package_id"]]
            s["tokens_consumed"] = int(pkg["tokens_per_second"] * elapsed_hours * 3600)
            s["current_cost"] = pkg["price_per_hour"] * elapsed_hours

    return s


def heartbeat(session_id: str) -> bool:
    """Mantiene sesión activa (check-in)."""
    if session_id not in sessions:
        return False

    s = sessions[session_id]
    invoice = pay.get_invoice(s["invoice_id"])

    if not invoice or not pay.check_payment(invoice.id):
        s["status"] = "payment_failed"
        return False

    if s["status"] == "pending_payment":
        s["status"] = "active"
        s["started_at"] = time.time()
        print(f"▶️  Sesión {session_id} activada")
        return True

    # Sesión activa, renovar heartbeat
    s["last_heartbeat"] = time.time()
    return True


if __name__ == "__main__":
    print("⚡ Compute Rental Agent")
    print(f"💰 Balance: {pay.total_earned():.6f} BCH\n")

    print("Paquetes disponibles:")
    for pid, pkg in PACKAGES.items():
        print(f"\n  {pid}: {pkg['name']}")
        print(f"     Tokens/s: {pkg['tokens_per_second']}")
        print(f"     💰 {pkg['price_per_hour']} BCH/h")

    print("\n🧪 Ejemplo de inicio de sesión:")
    result = start_compute_session("standard-gpu", "user_test", hours=1)
    print(f"\n✅ Sesión: {result['session_id']}")
    print(f"💳 Factura: {result['invoice'].id[:12]}... ({result['invoice'].amount} BCH)")
    print(f"🔗 Pagar: {pay.get_payment_url(result['invoice'].id)}")

    print("\n⌛ Esperando pago...")
    time.sleep(6)

    # Simular heartbeat
    if heartbeat(result['session_id']):
        print(f"\n▶️  Sesión activada! Usa heartbeat cada 60s")
        usage = get_session_usage(result['session_id'])
        print(f"   Tokens/s: {PACKAGES['standard-gpu']['tokens_per_second']}")
        print(f"   Costo/h: {PACKAGES['standard-gpu']['price_per_hour']} BCH")