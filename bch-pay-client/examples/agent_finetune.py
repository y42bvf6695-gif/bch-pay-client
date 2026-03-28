#!/usr/bin/env python3
"""
Agente de ejemplo: Fine-tuning as a Service

Este agente acepta pagos en BCH para ajustar modelos de IA.

Flujo:
1. Usuario envía dataset + modelo base
2. Agente crea factura
3. Al recibir pago, inicia fine-tuning
4. Notifica cuando esté listo
"""

import os
import uuid
from datetime import datetime
from typing import Optional

from bch_pay_client import BCHPay, BCHPayError

pay = BCHPay(network=os.getenv("BCH_NETWORK", "testnet"))

# Simulación de cola de trabajos
jobs = {}


def submit_finetune_job(user_id: str, dataset_url: str, base_model: str, amount: float) -> dict:
    """
    Inicia un trabajo de fine-tuning.

    Returns:
        dict: {'job_id': ..., 'invoice': ..., 'status': 'pending'}
    """
    job_id = str(uuid.uuid4())[:8]

    invoice = pay.create_invoice(
        amount=amount,
        description=f"Fine-tuning: {base_model}",
        metadata={
            "job_id": job_id,
            "user_id": user_id,
            "dataset_url": dataset_url,
            "base_model": base_model,
            "type": "finetune"
        }
    )

    jobs[job_id] = {
        "job_id": job_id,
        "invoice_id": invoice.id,
        "user_id": user_id,
        "dataset_url": dataset_url,
        "base_model": base_model,
        "amount": amount,
        "status": "waiting_payment",
        "created_at": datetime.now().isoformat(),
        "progress": 0
    }

    return {
        "job_id": job_id,
        "invoice": invoice,
        "status": "waiting_payment",
        "message": f"Paga {amount} BCH para iniciar fine-tuning"
    }


def check_and_process_jobs():
    """Revisa pagos pendientes y activa trabajos pagados."""
    for job_id, job in jobs.items():
        if job["status"] == "waiting_payment":
            invoice = pay.get_invoice(job["invoice_id"])
            if invoice and pay.check_payment(invoice.id):
                job["status"] = "processing"
                job["started_at"] = datetime.now().isoformat()
                print(f"✅ Job {job_id} pagado, iniciando fine-tuning...")
                # Aquí ejecutarías el fine-tuning real
                simulate_finetuning(job_id)


def simulate_finetuning(job_id: str):
    """Simula progreso de fine-tuning."""
    import threading
    import time

    def worker():
        for progress in range(0, 101, 10):
            jobs[job_id]["progress"] = progress
            time.sleep(2)  # Simular trabajo
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["completed_at"] = datetime.now().isoformat()
        print(f"✅ Job {job_id} completado!")

    threading.Thread(target=worker, daemon=True).start()


def get_job_status(job_id: str) -> Optional[dict]:
    """Consulta estado de un trabajo."""
    if job_id not in jobs:
        return None

    job = jobs[job_id].copy()
    job.pop("dataset_url", None)  # No exponer en respuesta

    # Añadir estado de pago
    invoice = pay.get_invoice(job["invoice_id"])
    if invoice:
        job["paid"] = invoice.paid
        if invoice.paid:
            job["txid"] = invoice.txid

    return job


# === EJEMPLO DE USO ===
if __name__ == "__main__":
    print("🤖 Fine-tuning as a Service Agent")
    print(f"💰 Balance: {pay.total_earned():.6f} BCH\n")

    # Simular usuario que envía un trabajo
    result = submit_finetune_job(
        user_id="user_123",
        dataset_url="https://example.com/dataset.jsonl",
        base_model="meta-llama/Llama-3-8B",
        amount=0.5
    )

    print(f"📋 Trabajo creado: {result['job_id']}")
    print(f"💳 Factura: {result['invoice'].id[:12]}...")
    print(f"🔗 Pagar: {pay.get_payment_url(result['invoice'].id)}")

    # Simular revisión de pagos
    print("\n⌛ Esperando pago...\n")
    for _ in range(10):
        check_and_process_jobs()
        time.sleep(2)

    # Consultar estado
    status = get_job_status(result['job_id'])
    print(f"\n📊 Estado final: {status}")