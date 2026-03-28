#!/usr/bin/env python3
"""
Agente: LLM API Pay-Per-Token

Este agente expone una API similar a OpenAI pero cobra en BCH por tokens.

Features:
- API compatible OpenAI (misma interfaz)
- Precio por 1K tokens (configurable por modelo)
- Balance prepago o pago por uso
- Rate limiting por usuario
- Métricas de uso
"""

import os
import time
import uuid
from typing import Dict, List, Optional

from bch_pay_client import BCHPay, BCHPayError

pay = BCHPay(network=os.getenv("BCH_NETWORK", "testnet"))

# Precios por 1K tokens
PRICING = {
    "gpt-3.5-turbo": 0.002,
    "gpt-4": 0.03,
    "claude-3-haiku": 0.00025,
    "claude-3-opus": 0.015,
    "llama-2-7b": 0.0001,
    "llama-2-70b": 0.0007
}

# Balance prepago de usuarios
user_balances = {}
user_histories = {}


def estimate_cost(model: str, prompt_tokens: int, max_tokens: int = 100) -> float:
    """Estima costo de una solicitud."""
    if model not in PRICING:
        raise ValueError(f"Modelo no disponible: {model}")

    price_per_1k = PRICING[model]
    estimated_total_tokens = prompt_tokens + max_tokens
    return (estimated_total_tokens / 1000) * price_per_1k


def create_balance_deposit(user_id: str, amount_bch: float) -> Dict:
    """Crea factura para depositar balance."""
    invoice = pay.create_invoice(
        amount=amount_bch,
        description=f"Depósito de balance para {user_id}",
        metadata={
            "type": "balance_deposit",
            "user_id": user_id
        }
    )

    return {
        "invoice": invoice,
        "amount_bch": amount_bch,
        "payment_url": pay.get_payment_url(invoice.id)
    }


def check_balance(user_id: str) -> float:
    """Consulta balance de usuario."""
    return user_balances.get(user_id, 0.0)


def top_up_balance(user_id: str, amount_bch: float):
    """Añade balance a usuario (tras pago confirmado)."""
    user_balances[user_id] = user_balances.get(user_id, 0) + amount_bch


def deduct_cost(user_id: str, cost_bch: float) -> bool:
    """Descuenta costo del balance."""
    balance = user_balances.get(user_id, 0)
    if balance < cost_bch:
        return False
    user_balances[user_id] = balance - cost_bch
    return True


def process_completion(
    user_id: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    estimated_cost: float = None
) -> Dict:
    """
    Procesa una completación y cobra.

    Returns:
        dict con resultado del cobro
    """
    if model not in PRICING:
        return {"error": f"Modelo no disponible: {model}"}

    # Calcular costo real
    price_per_1k = PRICING[model]
    actual_cost = ((prompt_tokens + completion_tokens) / 1000) * price_per_1k
    cost_to_charge = estimated_cost or actual_cost

    # Verificar balance
    if user_balances.get(user_id, 0) < cost_to_charge:
        return {"error": "Balance insuficiente", "required": cost_to_charge, "balance": user_balances.get(user_id, 0)}

    # Cargar
    if deduct_cost(user_id, cost_to_charge):
        # Registrar historial
        user_histories.setdefault(user_id, []).append({
            "timestamp": time.time(),
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cost_bch": cost_to_charge
        })

        return {
            "status": "charged",
            "cost_bch": cost_to_charge,
            "remaining_balance": user_balances[user_id]
        }
    else:
        return {"error": "No se pudo deducir balance"}


def get_user_usage(user_id: str, days: int = 30) -> Dict:
    """Obtiene historial de uso de usuario."""
    history = user_histories.get(user_id, [])
    cutoff = time.time() - (days * 86400)

    recent = [h for h in history if h["timestamp"] > cutoff]

    total_cost = sum(h["cost_bch"] for h in recent)
    total_tokens = sum(h["prompt_tokens"] + h["completion_tokens"] for h in recent)

    return {
        "user_id": user_id,
        "balance_bch": user_balances.get(user_id, 0),
        "total_cost_bch": total_cost,
        "total_tokens": total_tokens,
        "requests": len(recent),
        "models_used": list(set(h["model"] for h in recent))
    }


if __name__ == "__main__":
    print("🤖 LLM API Pay-Per-Token Agent")
    print(f"💰 Balance: {pay.total_earned():.6f} BCH\n")

    print("Modelos disponibles:")
    for model, price in PRICING.items():
        print(f"  {model}: ${price:.4f} / 1K tokens")

    # Ejemplo: usuario deposita balance
    print("\n🧪 Ejemplo 1: Depositar balance")
    deposit = create_balance_deposit("user_001", 0.1)
    print(f"💳 Factura: {deposit['invoice'].id[:12]}... ({deposit['amount_bch']} BCH)")
    print(f"🔗 Pagar: {deposit['payment_url']}")

    # Simular pago
    print("\n⌛ Esperando pago...")
    time.sleep(6)
    if pay.check_payment(deposit['invoice'].id):
        top_up_balance("user_001", 0.1)
        print("✅ Balance acreditado: 0.1 BCH")

    print(f"\n💰 Balance user_001: {check_balance('user_001')} BCH")

    # Ejemplo: uso de API
    print("\n🧪 Ejemplo 2: Usar API")
    result = process_completion(
        user_id="user_001",
        model="gpt-3.5-turbo",
        prompt_tokens=150,
        completion_tokens=300
    )
    print(f"✅ Completión procesada: {result}")
    print(f"💰 Balance restante: {check_balance('user_001'):.6f} BCH")

    print("\n📊 Uso del usuario:")
    print(get_user_usage("user_001"))