#!/usr/bin/env python3
"""
Ejemplo mínimo: agente que cobra porconsultas

Uso:
  python simple_demo.py create <amount> <description>
  python simple_demo.py check <invoice_id>
"""

import sys
from bch_pay_client import BCHPay

def create(amount: float, description: str):
    pay = BCHPay(network="testnet")
    invoice = pay.create_invoice(amount, description)
    print(f"✅ Factura creada: {invoice.id}")
    print(f"📍 Dirección: {invoice.address}")
    print(f"🔗 URL: {pay.get_payment_url(invoice.id)}")
    print(f"\nPuedes verificar con: python simple_demo.py check {invoice.id[:8]}")
    return invoice

def check(invoice_id: str):
    pay = BCHPay(network="testnet")
    invoices = pay.list_invoices(limit=100)
    invoice = next((i for i in invoices if i.id.startswith(invoice_id)), None)

    if not invoice:
        print("❌ Factura no encontrada")
        return

    if pay.check_payment(invoice.id):
        print(f"✅ Pagada! TXID: {invoice.txid}")
    else:
        print(f"⏳ Pendiente. Dirección: {invoice.address}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python simple_demo.py create <amount> <desc> | check <invoice_id>")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "create" and len(sys.argv) >= 4:
        create(float(sys.argv[2]), " ".join(sys.argv[3:]))
    elif cmd == "check" and len(sys.argv) >= 3:
        check(sys.argv[2])
    else:
        print("Argumentos inválidos")