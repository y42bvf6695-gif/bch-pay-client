#!/usr/bin/env python3
"""
Agente CLI BCHPay - Interfaz de línea de comandos

Este agente:
- Crea facturas desde la terminal
- Lista y verifica pagos
- Monitorea en tiempo real
- Funciona como herramienta de desarrollo/gestión
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import Optional
import threading

from bch_pay_client import BCHPay, BCHPayError


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")


def print_success(text: str):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_info(text: str):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def print_warning(text: str):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_error(text: str):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def format_bch(amount: float) -> str:
    return f"{amount:.6f} BCH"


def format_time(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


class BCHPayCLI:
    def __init__(self):
        self.pay = BCHPay(
            network=os.getenv("BCH_NETWORK", "testnet")
        )
        self.running = False

    def show_banner(self):
        print_header("╔══════════════════════════════════════╗")
        print_header("║    🤖 Agente BCHPay CLI v1.0        ║")
        print_header("║    Pagos Bitcoin Cash autónomos    ║")
        print_header("╚══════════════════════════════════════╝")
        print_info(f"Red: {self.pay.network}")
        print_info(f"Storage: {self.pay.storage_path}")
        print_info(f"Total ganado: {format_bch(self.pay.total_earned())}\n")

    def create_invoice(self, amount: float, description: str):
        try:
            invoice = self.pay.create_invoice(amount=amount, description=description)
            print_success(f"Factura creada: {invoice.id[:12]}...")
            print(f"\n💰 Monto: {format_bch(invoice.amount)}")
            print(f"📝 Descripción: {invoice.description}")
            print(f"📍 Dirección: {invoice.address}")
            print(f"🔗 URL: {self.pay.get_payment_url(invoice.id)}")

            # Generar QR si está disponible
            try:
                qr_file = f"qr_{invoice.id[:8]}.png"
                qr_bytes = self.pay.generate_qr(invoice.id)
                with open(qr_file, 'wb') as f:
                    f.write(qr_bytes)
                print_info(f"QR guardado en: {qr_file}")
            except Exception as e:
                print_warning(f"No se pudo generar QR: {e}")

            print(f"\nComando para verificar: bchpay-cli check {invoice.id[:8]}")
            return invoice

        except BCHPayError as e:
            print_error(f"Error: {str(e)}")
            return None

    def check_invoice(self, invoice_id: str):
        """Busca y verifica una factura por ID parcial."""
        all_invoices = self.pay.list_invoices(limit=100)
        invoice = next(
            (inv for inv in all_invoices if inv.id.startswith(invoice_id)),
            None
        )

        if not invoice:
            print_error("Factura no encontrada")
            return

        is_paid = self.pay.check_payment(invoice.id)

        print(f"\n🏷️  ID: {invoice.id}")
        print(f"💰 Monto: {format_bch(invoice.amount)}")
        print(f"📝 Descripción: {invoice.description}")
        print(f"📍 Dirección: {invoice.address}")
        print(f"📅 Creada: {format_time(invoice.created_at)}")

        if is_paid:
            print_success(f"Estado: PAGADA ✅")
            print(f"⏰ Pagada: {format_time(invoice.paid_at)}")
            print(f"🔗 TXID: {invoice.txid}")
        else:
            print_warning(f"Estado: PENDIENTE ⏳")

    def list_invoices(self, limit: int = 20, show_all: bool = False):
        invoices = self.pay.list_invoices(limit=limit)
        if not show_all:
            invoices = [inv for inv in invoices if inv.paid]  # Solo pagadas por defecto

        if not invoices:
            print_info("No hay facturas que mostrar")
            return

        print(f"\n📋 Últimas {len(invoices)} facturas:")
        print("-" * 80)
        for inv in invoices:
            status = f"{Colors.OKGREEN}PAGADA{Colors.ENDC}" if inv.paid else f"{Colors.WARNING}PENDIENTE{Colors.ENDC}"
            print(f"[{status}] {inv.id[:12]}... | {format_bch(inv.amount)} | {inv.description[:40]}")
            if inv.paid:
                print(f"         Pagada: {format_time(invoice.paid_at)}, TX: {inv.txid[:16]}...")
        print("-" * 80)

    def monitor_mode(self, interval: int = 10):
        """Modo monitor: verifica pagos pendientes en bucle."""
        print_info(f"Iniciando monitor (revisando cada {interval}s). Presiona Ctrl+C para salir.\n")
        self.running = True

        try:
            while self.running:
                pending = [inv for inv in self.pay.list_invoices(limit=100) if not inv.paid]
                if pending:
                    print(f"\n⏳ {len(pending)} facturas pendientes")
                    for inv in pending[:5]:
                        if self.pay.check_payment(inv.id):
                            print_success(f"✅ {inv.id[:12]}... pagada! ({format_bch(inv.amount)})")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n🛑 Monitor detenido")
            self.running = False

    def show_stats(self):
        total = self.pay.total_earned()
        invoices = self.pay.list_invoices(limit=1000)
        paid = len([inv for inv in invoices if inv.paid])
        pending = len(invoices) - paid

        print(f"\n📊 Estadísticas:")
        print(f"   Total facturas: {len(invoices)}")
        print(f"   Pagadas: {paid}")
        print(f"   Pendientes: {pending}")
        print(f"   Total ganado: {format_bch(total)}")
        print(f"   Storage: {self.pay.storage_path}")


def print_help():
    print("""
Uso: bchpay-cli <comando> [argumentos]

Comandos:
  create <amount> <desc>     Crear factura
  check <invoice_id>         Verificar estado de pago
  list [--all]               Listar facturas (pagadas por defecto, --all muestra todas)
  monitor                    Monitorear pagos pendientes en tiempo real
  stats                      Mostrar estadísticas
  help                       Mostrar esta ayuda

Ejemplos:
  bchpay-cli create 0.01 "Consulta GPT-4"
  bchpay-cli check abc123
  bchpay-cli list --all
    """)


def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    cli = BCHPayCLI()
    cli.show_banner()

    command = sys.argv[1]

    if command == "create" and len(sys.argv) >= 4:
        amount = float(sys.argv[2])
        description = " ".join(sys.argv[3:])
        cli.create_invoice(amount, description)

    elif command == "check" and len(sys.argv) >= 3:
        cli.check_invoice(sys.argv[2])

    elif command == "list":
        show_all = "--all" in sys.argv
        cli.list_invoices(show_all=show_all)

    elif command == "monitor":
        cli.monitor_mode()

    elif command == "stats":
        cli.show_stats()

    elif command in ["help", "--help", "-h"]:
        print_help()

    else:
        print_error(f"Comando desconocido: {command}")
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()