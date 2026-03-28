#!/usr/bin/env python3
"""
Agente autónomo híbrido: múltiples interfaces en uno.

Este agente combina:
- API REST (FastAPI) en puerto 8000
- Discord bot (si token configurado)
- Telegram bot (si token configurado)
- CLI integrado

Ejecuta todos los servicios simultáneamente.
"""

import os
import sys
import threading
import time
import uvicorn
from typing import Optional

# Importar módulos locales (usar bch_pay_client como paquete instalable)
from bch_pay_client import BCHPay

pay = BCHPay(network=os.getenv("BCH_NETWORK", "testnet"))


def run_api():
    """Ejecuta la API FastAPI."""
    print("🚀 Iniciando API en puerto 8000...")
    # Cambiar al directorio de ejemplos para que los imports funcionen
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    uvicorn.run(
        "agent_api:app",
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


def run_discord():
    """Ejecuta el bot Discord si el token está disponible."""
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("⚠️  DISCORD_BOT_TOKEN no configurado, saltando Discord")
        return

    print("🤖 Iniciando bot Discord...")
    # Cambiar al directorio de ejemplos
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    import subprocess
    subprocess.run([sys.executable, "agent_discord.py"])


def run_telegram():
    """Ejecuta el bot Telegram si el token está disponible."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("⚠️  TELEGRAM_BOT_TOKEN no configurado, saltando Telegram")
        return

    print("📱 Iniciando bot Telegram...")
    # Cambiar al directorio de ejemplos
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    import subprocess
    subprocess.run([sys.executable, "agent_telegram.py"])


def main():
    print("╔══════════════════════════════════════╗")
    print("║    🤖 Agente BCHPay Híbrido v1.0    ║")
    print("╚══════════════════════════════════════╝\n")
    print(f"📡 Red BCH: {pay.network}")
    print(f"💰 Balance: {pay.total_earned():.6f} BCH\n")

    services = []

    # API siempre activa
    api_thread = threading.Thread(target=run_api, daemon=True)
    services.append(("API", api_thread))
    api_thread.start()

    time.sleep(2)  # Esperar a que API inicie

    # Bots opcionales
    if os.getenv("DISCORD_BOT_TOKEN"):
        discord_thread = threading.Thread(target=run_discord, daemon=True)
        services.append(("Discord", discord_thread))
        discord_thread.start()

    if os.getenv("TELEGRAM_BOT_TOKEN"):
        telegram_thread = threading.Thread(target=run_telegram, daemon=True)
        services.append(("Telegram", telegram_thread))
        telegram_thread.start()

    print("\n✅ Servicios activos:")
    for name, _ in services:
        print(f"   • {name}")

    print("\n📋 Endpoints API:")
    print("   • http://localhost:8000/ (doc)")
    print("   • POST /invoices → Crear factura")
    print("   • GET /invoices/{id} → Ver factura")
    print("   • GET /balance → Balance total")

    print("\nPresiona Ctrl+C para detener todos los servicios.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo agentes...")


if __name__ == "__main__":
    main()