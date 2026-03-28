#!/usr/bin/env python3
"""
BCHPay Runner - Selector de agentes

Uso: python run.py <agent> [args...]

Agentes disponibles:
  api         - API REST FastAPI (puerto 8000)
  discord     - Bot Discord
  telegram    - Bot Telegram
  cli         - CLI interactivo
  hybrid      - Todos los agentes simultáneamente
  finetune    - Fine-tuning as a Service
  datasets    - Dataset Marketplace
  gpu         - GPU Rental
  compute     - Compute Rental
  image       - Image Generation
  llm         - LLM API con balance prepago

Ejemplos:
  python run.py api
  python run.py cli
"""

import sys
import subprocess
from pathlib import Path

AGENTS = {
    "api": "examples/agent_api.py",
    "discord": "examples/agent_discord.py",
    "telegram": "examples/agent_telegram.py",
    "cli": "examples/agent_cli.py",
    "hybrid": "examples/agent_hybrid.py",
    "finetune": "examples/agent_finetune.py",
    "datasets": "examples/agent_dataset_marketplace.py",
    "gpu": "examples/agent_gpu_rental.py",
    "compute": "examples/agent_compute_rental.py",
    "image": "examples/agent_image_gen.py",
    "llm": "examples/agent_llm_api.py",
}

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("Agentes disponibles:", ", ".join(AGENTS.keys()))
        sys.exit(1)

    agent = sys.argv[1]
    if agent not in AGENTS:
        print(f"❌ Agente '{agent}' no encontrado")
        print("Disponibles:", ", ".join(AGENTS.keys()))
        sys.exit(1)

    script = Path(__file__).parent / AGENTS[agent]
    args = [sys.executable, str(script)] + sys.argv[2:]

    print(f"🚀 Iniciando agente '{agent}'...")
    print(f"   Script: {AGENTS[agent]}\n")
    try:
        subprocess.run(args, check=False)
    except KeyboardInterrupt:
        print(f"\n🛑 Agente '{agent}' detenido")
        sys.exit(0)

if __name__ == "__main__":
    main()