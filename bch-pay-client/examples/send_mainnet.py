"""
Script para enviar BCH en mainnet usando Paytaca backend.

**IMPORTANTE**: Este script NO contiene ninguna seedphrase.
Requiere que tengas:
1. Node.js 20+ instalado
2. paytaca-cli instalado globally: npm install -g paytaca-cli
3. Wallet creada/importada: paytaca wallet create (o import)
4. Fondos en la wallet (suficientes para el envío + fee)

Uso:
    python examples/send_mainnet.py --amount 0.00242019 --address bitcoincash:qz8983kqe0pwccwg3urj462mlzrm02q4vc3z22j9w4

Opciones:
    --dry-run    Simula el envío sin ejecutarlo (default: False)
    --verbose    Muestra información detallada

¡ADVERTENCIA! Las transacciones en mainnet son irreversibles.
Verifica la dirección y el monto antes de ejecutar.
"""

import argparse
import sys
from pathlib import Path

from bch_pay_client import BCHPay, BCHPayError

def main():
    parser = argparse.ArgumentParser(description="Enviar BCH en mainnet via Paytaca")
    parser.add_argument("--amount", type=float, required=True, help="Cantidad en BCH")
    parser.add_argument("--address", type=str, required=True, help="Dirección destino (bitcoincash:...)")
    parser.add_argument("--dry-run", action="store_true", help="Simular sin enviar")
    parser.add_argument("--verbose", action="store_true", help="Mostrar detalles")
    args = parser.parse_args()

    # Validar dirección (chequeo básico)
    if not args.address.startswith(("bitcoincash:", "bchtest:")):
        print(f"❌ Dirección inválida: {args.address}")
        print("   Debe empezar con 'bitcoincash:' (mainnet) o 'bchtest:' (testnet)")
        sys.exit(1)

    # Validar monto
    if args.amount <= 0:
        print(f"❌ Monto inválido: {args.amount}")
        sys.exit(1)

    print("=" * 60)
    print("ENVÍO BCH EN MAINNET")
    print("=" * 60)
    print(f" destinatario: {args.address}")
    print(f" monto:        {args.amount:.8f} BCH")
    print(f" dry-run:      {args.dry_run}")
    print("=" * 60)

    if not args.dry_run:
        confirm = input("¿CONFIRMAS este envío? (escribe 'SI' para continuar): ")
        if confirm != "SI":
            print("❌ Envío cancelado")
            sys.exit(0)

    try:
        # Inicializar Paytaca backend en mainnet
        if args.verbose:
            print("🔄 Inicializando BCHPay(backend='paytaca', network='mainnet')...")
        pay = BCHPay(backend='paytaca', network='mainnet')

        if args.dry_run:
            print("✅ [DRY RUN] Todo listo para enviar (no se ejecutó)")
            print(f"   Paytaca CLI: {pay.backend.paytaca_cli}")
            print(f"   Wallet address: (usará la predeterminada de Paytaca)")
            return

        # Ejecutar envío
        if args.verbose:
            print("🔄 Ejecutando send_payment()...")
        result = pay.send_payment(
            address=args.address,
            amount=args.amount
        )

        if result["success"]:
            print("✅ ¡ENVÍO EXITOSO!")
            print(f"   TXID: {result.get('txid', 'N/A')}")
            print(f"   Puedes ver la transacción en: https://explorer.bitcoin.com/bch/tx/{result.get('txid', '')}")
        else:
            print("❌ ERROR al enviar")
            print(f"   Mensaje: {result.get('error', 'Desconocido')}")
            sys.exit(1)

    except BCHPayError as e:
        print(f"❌ Error de BCHPay: {e}")
        sys.exit(1)
    except RuntimeError as e:
        if "Paytaca CLI not found" in str(e):
            print("❌ Paytaca CLI no encontrado!")
            print("   Instala con: npm install -g paytaca-cli")
            print("   Y verifica: paytaca --version")
        elif "Failed to get address" in str(e) or "Could not parse" in str(e):
            print("❌ Error al interactuar con Paytaca CLI")
            print("   Asegúrate de tener wallet creada: paytaca wallet create")
            print("   Y fondos suficientes en mainnet.")
        else:
            print(f"❌ RuntimeError: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {type(e).__name__}: {e}")
        sys.exit(1)

    print("=" * 60)

if __name__ == "__main__":
    main()
