#!/usr/bin/env python3
"""
Agente: GPU/CPU Renting

Este agente alquila recursos de cómputo por tiempo, cobrando en BCH.

Features:
- Listar recursos disponibles (GPU/CPU)
- Reservar recurso por tiempo
- Pago por uso (por minuto/hora)
- Check-in/check-out automático
- Metrías de uso
"""

import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from bch_pay_client import BCHPay, BCHPayError

pay = BCHPay(network=os.getenv("BCH_NETWORK", "testnet"))

# Catálogo de recursos (simulado)
RESOURCES = {
    "gpu-v100": {
        "name": "NVIDIA Tesla V100",
        "type": "gpu",
        "specs": "32GB HBM2, 5120 cores",
        "price_per_hour": 0.02,
        "available": True
    },
    "gpu-a100": {
        "name": "NVIDIA A100 80GB",
        "type": "gpu",
        "specs": "80GB HBM2e, 6912 cores",
        "price_per_hour": 0.05,
        "available": True
    },
    "cpu-16core": {
        "name": "AMD EPYC 16-core",
        "type": "cpu",
        "specs": "16 cores, 32 threads, 128GB RAM",
        "price_per_hour": 0.005,
        "available": True
    }
}

# Registro de reservas
reservations = {}


def list_resources(filter_type: Optional[str] = None) -> List[Dict]:
    """Lista recursos disponibles."""
    resources = []
    for rid, res in RESOURCES.items():
        if filter_type and res["type"] != filter_type:
            continue
        resources.append({
            "id": rid,
            **res,
            "available": res["available"] and not any(
                r["resource_id"] == rid and r["status"] == "active"
                for r in reservations.values()
            )
        })
    return resources


def reserve_resource(
    resource_id: str,
    user_id: str,
    hours: float = 1.0,
    auto_start: bool = False
) -> Optional[Dict]:
    """
    Reserva un recurso y crea factura.

    Args:
        resource_id: ID del recurso
        user_id: ID del usuario
        hours: Duración en horas
        auto_start: Si True, inicia automáticamente tras pago

    Returns:
        dict con detalles de la reserva y factura
    """
    if resource_id not in RESOURCES:
        return None

    resource = RESOURCES[resource_id]
    if not resource["available"]:
        return None

    # Verificar si ya está reservado
    if any(r["resource_id"] == resource_id and r["status"] == "active" for r in reservations.values()):
        return None

    amount = resource["price_per_hour"] * hours

    invoice = pay.create_invoice(
        amount=amount,
        description=f"Alquiler {resource['name']} ({hours}h)",
        metadata={
            "type": "rental",
            "resource_id": resource_id,
            "user_id": user_id,
            "hours": hours,
            "auto_start": auto_start
        }
    )

    reservation_id = str(uuid.uuid4())[:8]
    reservations[reservation_id] = {
        "reservation_id": reservation_id,
        "resource_id": resource_id,
        "user_id": user_id,
        "invoice_id": invoice.id,
        "duration_hours": hours,
        "status": "pending_payment",
        "created_at": time.time(),
        "started_at": None,
        "ended_at": None
    }

    return {
        "reservation_id": reservation_id,
        "invoice": invoice,
        "amount_bch": amount,
        "resource": resource,
        "payment_url": pay.get_payment_url(invoice.id)
    }


def activate_reservation(reservation_id: str) -> bool:
    """Activa una reserva pagada."""
    if reservation_id not in reservations:
        return False

    reservation = reservations[reservation_id]
    invoice = pay.get_invoice(reservation["invoice_id"])

    if not invoice or not pay.check_payment(invoice.id):
        return False

    reservation["status"] = "active"
    reservation["started_at"] = time.time()

    # Calcular tiempo de finalización
    end_time = datetime.now() + timedelta(hours=reservation["duration_hours"])
    reservation["end_time"] = end_time.isoformat()

    return True


def release_reservation(reservation_id: str, user_initiated: bool = True) -> bool:
    """Libera una reserva (devolución parcial si queda tiempo)."""
    if reservation_id not in reservations:
        return False

    reservation = reservations[reservation_id]
    if reservation["status"] != "active":
        return False

    # Calcular tiempo no utilizado (simple)
    end_time = datetime.fromisoformat(reservation["end_time"])
    now = datetime.now()

    if now < end_time:
        remaining_hours = (end_time - now).total_seconds() / 3600
        refund_percentage = remaining_hours / reservation["duration_hours"]
        print(f"💰 Devolución proporcional: {refund_percentage*100:.1f}%")
        # En producción, generarías una factura de devolución

    reservation["status"] = "released"
    reservation["released_at"] = time.time()
    reservation["user_initiated"] = user_initiated

    return True


def get_reservation_status(reservation_id: str) -> Optional[Dict]:
    """Consulta estado de reserva."""
    if reservation_id not in reservations:
        return None

    reservation = reservations[reservation_id].copy()
    invoice = pay.get_invoice(reservation["invoice_id"])

    if invoice:
        reservation["paid"] = invoice.paid

    if reservation["status"] == "active":
        end_time = datetime.fromisoformat(reservation["end_time"])
        remaining = end_time - datetime.now()
        reservation["remaining_minutes"] = max(0, int(remaining.total_seconds() / 60))

    return reservation


def check_expired_reservations():
    """Revisa y libera reservas expiradas."""
    now = datetime.now()
    for rid, reservation in reservations.items():
        if reservation["status"] == "active":
            end_time = datetime.fromisoformat(reservation["end_time"])
            if now >= end_time:
                reservation["status"] = "expired"
                reservation["expired_at"] = now.isoformat()
                print(f"⏰ Reserva {rid} expirada")


if __name__ == "__main__":
    print("🖥️  GPU/CPU Renting Agent")
    print(f"💰 Balance: {pay.total_earned():.6f} BCH\n")

    print("Recursos disponibles:")
    for res in list_resources():
        print(f"\n🖥️  {res['id']}: {res['name']}")
        print(f"   Specs: {res['specs']}")
        print(f"   💰 {res['price_per_hour']} BCH/h")

    # Ejemplo de reserva
    print("\n\n🧪 Ejemplo de reserva:")
    result = reserve_resource("gpu-v100", "user_123", hours=2, auto_start=True)
    if result:
        print(f"✅ Reserva creada: {result['reservation_id']}")
        print(f"💳 Factura: {result['invoice'].id[:12]}... ({result['amount_bch']} BCH)")
        print(f"🔗 Pagar: {pay.get_payment_url(result['invoice'].id)}")

        # Simular verificación
        print("\n⌛ Esperando pago...")
        time.sleep(6)
        if activate_reservation(result['reservation_id']):
            print(f"🚀 Reserva activada! Recurso disponible por 2h")