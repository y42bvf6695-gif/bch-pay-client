#!/usr/bin/env python3
"""
Agente local interactivo - CLI con menú

Uso: python agent_local.py
"""

import os
import sys
import time
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bch_pay_client import BCHPay


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_menu():
    print("\n" + "="*60)
    print("🤖 AGENTE BCHPAY INTERACTIVO")
    print("="*60)
    print("1. 📦 Crear factura")
    print("2. ✅ Verificar factura")
    print("3. 📋 Listar facturas")
    print("4. 📊 Estadísticas")
    print("5. 🏠 Iniciar API REST")
    print("6. 🚀 Iniciar modo híbrido (API + bots)")
    print("7. ❓ Ayuda")
    print("0. 🚪 Salir")
    print("="*60)


def create_invoice_interactive(pay: BCHPay):
    print("\n📦 CREAR FACTURA")
    try:
        amount = float(input("Monto en BCH: "))
        if amount <= 0:
            print("❌ Monto debe ser > 0")
            return

        desc = input("Descripción: ").strip() or "Pago IA"
        meta = input("Metadata JSON (opcional): ").strip()

        metadata = {}
        if meta:
            try:
                metadata = json.loads(meta)
            except:
                print("⚠️  Metadata inválida, se ignorará")

        invoice = pay.create_invoice(amount, desc, metadata)

        print(f"\n✅ Factura creada: {invoice.id}")
        print(f"💰 Monto: {invoice.amount} BCH")
        print(f"📍 Dirección: {invoice.address}")
        print(f"🔗 URL: {pay.get_payment_url(invoice.id)}")

        # QR
        try:
            qr_file = f"qr_{invoice.id[:8]}.png"
            with open(qr_file, 'wb') as f:
                f.write(pay.generate_qr(invoice.id))
            print(f"🖼️  QR guardado en: {qr_file}")
        except Exception as e:
            print(f"⚠️  No se pudo generar QR: {e}")

    except ValueError:
        print("❌ Monto inválido")
    except BCHPayError as e:
        print(f"❌ Error: {e}")


def check_invoice_interactive(pay: BCHPay):
    print("\n✅ VERIFICAR FACTURA")
    invoice_id = input("ID (o prefijo) de factura: ").strip()
    if not invoice_id:
        print("❌ ID requerido")
        return

    all_invoices = pay.list_invoices(limit=100)
    invoice = next(
        (inv for inv in all_invoices if inv.id.startswith(invoice_id)),
        None
    )

    if not invoice:
        print("❌ Factura no encontrada")
        return

    is_paid = pay.check_payment(invoice.id)

    print(f"\n🏷️  ID: {invoice.id}")
    print(f"💰 Monto: {invoice.amount} BCH")
    print(f"📝 Desc: {invoice.description}")
    print(f"📍 Dir: {invoice.address}")
    print(f"📅 Creada: {time.ctime(invoice.created_at)}")

    status = "✅ PAGADA" if is_paid else "⏳ PENDIENTE"
    print(f"🔄 Estado: {status}")

    if is_paid:
        print(f"⏰ Pagada: {time.ctime(invoice.paid_at)}")
        print(f"🔗 TXID: {invoice.txid}")


def list_invoices_interactive(pay: BCHPay):
    print("\n📋 LISTAR FACTURAS")
    limit = input("Mostrar últimas [20]: ") or "20"
    try:
        limit = min(int(limit), 100)
    except:
        limit = 20

    show_all = input("¿Mostrar todas (solo pendientes por defecto)? [n]: ").lower().startswith('s')

    invoices = pay.list_invoices(limit)
    if not show_all:
        invoices = [inv for inv in invoices if True]  # could filter

    if not invoices:
        print("📭 No hay facturas")
        return

    print(f"\nMostrando {len(invoices)} facturas:")
    print("-" * 80)
    for i, inv in enumerate(invoices, 1):
        status = "✅" if inv.paid else "⏳"
        print(f"{i:02d}. {status} {inv.id[:12]}... | {inv.amount:8.6f} BCH | {inv.description[:40]}")
    print("-" * 80)
    print(f"Total: {len(invoices)} facturas")


def stats_interactive(pay: BCHPay):
    print("\n📊 ESTADÍSTICAS")
    total = pay.total_earned()
    invoices = pay.list_invoices(limit=1000)
    paid = len([inv for inv in invoices if inv.paid])
    pending = len(invoices) - paid

    print(f"📦 Total facturas: {len(invoices)}")
    print(f"✅ Pagadas: {paid}")
    print(f"⏳ Pendientes: {pending}")
    print(f"💰 Balance total: {total:.6f} BCH")
    print(f"💾 Storage: {pay.storage_path}")
    print(f"🌐 Red: {pay.network}")


def start_api():
    print("\n🚀 Iniciando API REST en http://0.0.0.0:8000")
    print("   Presiona Ctrl+C para detener\n")
    try:
        uvicorn.run("agent_api:app", host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        print("\n🛑 API detenida")


def start_hybrid():
    print("\n🚀 Iniciando modo híbrido")
    try:
        import subprocess
        subprocess.run([sys.executable, "agent_hybrid.py"])
    except KeyboardInterrupt:
        print("\n🛑 Servicios híbridos detenidos")


def main():
    pay = BCHPay(network=os.getenv("BCH_NETWORK", "testnet"))

    clear()
    print_menu()
    print_info(f"Red: {pay.network}, Balance: {pay.total_earned():.6f} BCH")

    while True:
        try:
            choice = input("\n👉 Seleccionar opción: ").strip()

            if choice == "1":
                create_invoice_interactive(pay)
            elif choice == "2":
                check_invoice_interactive(pay)
            elif choice == "3":
                list_invoices_interactive(pay)
            elif choice == "4":
                stats_interactive(pay)
            elif choice == "5":
                start_api()
            elif choice == "6":
                start_hybrid()
            elif choice == "7":
                print("""
Ayuda BCHPay:

1. Crear factura:
   - Ingresa monto (ej: 0.01) y descripción
   - Se genera dirección BCH y QR
   - El cliente paga a esa dirección

2. Verificar factura:
   - Usa el ID o los primeros caracteres
   - Se consulta el estado (pagada/pendiente)

3. Listar facturas:
   - Muestra facturas recientes
   - Opción para ver todas

4. Estadísticas:
   - Balance total ganado
   - Número de facturas

5. Iniciar API:
   - Ejecuta servidor REST en puerto 8000
   - Documentación en /docs

6. Modo híbrido:
   - Inicia API + Discord + Telegram simultáneamente

Configuración via variables de entorno:
  BCH_NETWORK=testnet|mainnet
  DISCORD_BOT_TOKEN=...
  TELEGRAM_BOT_TOKEN=...
                """)
            elif choice == "0":
                print("\n👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida")

            input("\nPresiona Enter para continuar...")
            clear()
            print_menu()

        except KeyboardInterrupt:
            print("\n\n👋 Saliendo...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()