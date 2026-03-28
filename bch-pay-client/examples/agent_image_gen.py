#!/usr/bin/env python3
"""
Agente: AI Image Generation Pay-Per-Use

Este agente genera imágenes a cambio de pagos en BCH.

Features:
- Generación de imágenes con Stable Diffusion / OpenAI / DALL-E
- Pago por generación (precio variable por tamaño/resolución)
- Cola de trabajos (FIFO)
- Entrega de imágenes tras pago
"""

import os
import uuid
import time
from typing import Dict, Optional

from bch_pay_client import BCHPay, BCHPayError

pay = BCHPay(network=os.getenv("BCH_NETWORK", "testnet"))

# Precios por resolución
PRICING = {
    "512x512": 0.001,
    "768x512": 0.0015,
    "1024x768": 0.0025,
    "1536x1024": 0.005
}

# Cola de trabajos
job_queue = []
completed_jobs = {}


def generate_image_request(
    prompt: str,
    resolution: str = "512x512",
    model: str = "stable-diffusion",
    user_id: str = None
) -> Optional[Dict]:
    """
    Solicita generación de imagen.

    Returns:
        dict con job_id y factura
    """
    if resolution not in PRICING:
        return None

    price = PRICING[resolution]

    invoice = pay.create_invoice(
        amount=price,
        description=f"Imagen: {prompt[:50]}...",
        metadata={
            "type": "image_gen",
            "prompt": prompt,
            "resolution": resolution,
            "model": model,
            "user_id": user_id
        }
    )

    job_id = str(uuid.uuid4())[:8]
    job_queue.append({
        "job_id": job_id,
        "invoice_id": invoice.id,
        "prompt": prompt,
        "resolution": resolution,
        "model": model,
        "user_id": user_id,
        "status": "pending_payment",
        "created_at": time.time()
    })

    # Ordenar por tiempo de creación
    job_queue.sort(key=lambda x: x["created_at"])

    return {
        "job_id": job_id,
        "invoice": invoice,
        "price_bch": price,
        "payment_url": pay.get_payment_url(invoice.id),
        "status": "waiting_payment"
    }


def process_job_queue():
    """Procesa cola de trabajos (pagos verificados)."""
    for job in job_queue[:]:
        if job["status"] == "pending_payment":
            invoice = pay.get_invoice(job["invoice_id"])
            if invoice and pay.check_payment(invoice.id):
                job["status"] = "processing"
                print(f"🎨 Procesando job {job['job_id']}: {job['prompt'][:40]}...")

                # Aquí llamarías a tu modelo de generación
                # image = generate_with_model(job['prompt'], job['resolution'])
                # Simular
                time.sleep(5)

                job["status"] = "completed"
                job["completed_at"] = time.time()
                job["image_url"] = f"/generated/{job['job_id']}.png"
                completed_jobs[job["job_id"]] = job
                job_queue.remove(job)

                print(f"✅ Job {job['job_id']} completado")


def get_job_result(job_id: str) -> Optional[Dict]:
    """Obtiene resultado de trabajo completado."""
    if job_id in completed_jobs:
        return completed_jobs[job_id]

    for job in job_queue:
        if job["job_id"] == job_id:
            return job

    return None


def cancel_job(job_id: str) -> bool:
    """Cancela trabajo pendiente (solo si no pagado)."""
    for i, job in enumerate(job_queue):
        if job["job_id"] == job_id and job["status"] == "pending_payment":
            job_queue.pop(i)
            # En producción, también podrías marcar la factura como cancelada
            return True
    return False


if __name__ == "__main__":
    print("🎨 AI Image Generation Agent")
    print(f"💰 Balance: {pay.total_earned():.6f} BCH\n")

    print("Precios por resolución:")
    for res, price in PRICING.items():
        print(f"  {res}: {price} BCH")

    print("\n🧪 Ejemplo de solicitud:")
    result = generate_image_request(
        prompt="A beautiful sunset over mountains, photorealistic, 8k",
        resolution="1024x768",
        user_id="user_001"
    )

    if result:
        print(f"\n📋 Job creado: {result['job_id']}")
        print(f"💳 Factura: {result['invoice'].id[:12]}... ({result['price_bch']} BCH)")
        print(f"🔗 Pagar: {result['payment_url']}")
        print("\n⌛ Esperando pago para generar imagen...\n")

        # Simular verificación de pago
        for _ in range(20):
            process_job_queue()
            time.sleep(2)

        final = get_job_result(result['job_id'])
        if final and final['status'] == 'completed':
            print(f"\n✅ Imagen lista: {final['image_url']}")