"""
Ejemplo: Agente que acepta pagos en BCH y MUSD (CashToken)

Este agente demuestra cómo usar bch-pay-client con Bitcoin Cash nativo
y MUSD (un stablecoin en BCH CashToken).

Requisitos:
- pip install bch-pay-client
- Para pagos reales: Node.js + paytaca-cli instalado

Uso:
    python examples/agent_token_demo.py
"""

from bch_pay_client import BCHPay
import time

# MUSD CashToken category ID en mainnet/chipnet
MUSD_CATEGORY = "e90b1965dc200e3c8d5f899a9e8e146c073552418b266d3a87238777a6d3d227"


def demo_bch_payments():
    """Demo de pagos en BCH nativo."""
    print("=== DEMO PAGOS BCH ===")
    pay = BCHPay(network='testnet')  # Usa demo mode por defecto

    # Crear factura de 0.01 BCH (~$0.50)
    invoice = pay.create_invoice(
        amount=0.01,
        description="Consulta IA: 1000 tokens"
    )
    print(f"Factura BCH creada: {invoice.id}")
    print(f"  Dirección: {invoice.address}")
    print(f"  Monto: {invoice.amount} BCH")

    # Simular espera de pago (en demo, se aprueba después de 6 segundos)
    print("  Esperando pago...")
    time.sleep(6)

    if pay.check_payment(invoice.id):
        print("  ✅ Pago recibido! Entregando resultado...")
    else:
        print("  ❌ No se recibió pago")

    print(f"Balance BCH: {pay.get_balance():.6f} BCH")
    print()


def demo_musd_payments():
    """Demo de pagos en MUSD CashToken."""
    print("=== DEMO PAGOS MUSD (CashToken) ===")
    pay = BCHPay(network='testnet')

    # Crear factura en MUSD (stablecoin, ej: $1.00 = 1 MUSD)
    invoice = pay.create_invoice(
        amount=1.0,  # 1 MUSD (~$1.00)
        description="Suscripción mensual",
        token_category=MUSD_CATEGORY
    )
    print(f"Factura MUSD creada: {invoice.id}")
    print(f"  Dirección token: {invoice.address}")
    print(f"  Monto: {invoice.amount} MUSD")

    # Verificar pago
    print("  Esperando pago en MUSD...")
    time.sleep(6)

    if pay.check_payment(invoice.id):
        print("  ✅ Pago MUSD recibido!")
    else:
        print("  ❌ No se recibió pago MUSD")

    # Consultar balance de MUSD
    musd_balance = pay.get_balance(token_category=MUSD_CATEGORY)
    print(f"Balance MUSD: {musd_balance:.2f} MUSD")
    print()


def list_available_tokens():
    """Lista los tokens disponibles en el wallet (Paytaca backend)."""
    print("=== TOKENS DISPONIBLES ===")
    pay = BCHPay(network='testnet')

    tokens = pay.list_tokens()
    if tokens:
        print(f"{'Symbol':<10} {'Name':<20} {'Balance':<15} {'Category':<20}")
        print("-" * 70)
        for t in tokens:
            print(f"{t['symbol']:<10} {t['name']:<20} {t['balance']:<15.2f} {t['category'][:20]:<20}")
    else:
        print("No se encontraron tokens (o backend no soporta list_tokens)")
        print("Para ver tokens reales, usa backend='paytaca' con wallet que tenga MUSD")
    print()


def send_tokens_example():
    """Ejemplo de cómo enviar MUSD a otro usuario."""
    print("=== ENVÍO DE MUSD ===")
    pay = BCHPay(network='testnet', backend='demo')  # Cambiar a 'paytaca' para real

    # Enviar 5 MUSD a una dirección destino
    recipient = "bchtest:zpp...example..."  # Dirección token-aware (z-prefix)
    result = pay.send_payment(
        address=recipient,
        amount=5.0,
        token_category=MUSD_CATEGORY
    )

    if result['success']:
        print(f"✅ Enviados 5 MUSD a {recipient}")
        print(f"  TXID: {result.get('txid', 'N/A')}")
    else:
        print(f"❌ Error enviando: {result.get('error')}")
    print()


if __name__ == "__main__":
    print("bch-pay-client: BCH + MUSD Demo")
    print("=" * 50)
    print()

    demo_bch_payments()
    demo_musd_payments()
    list_available_tokens()
    # send_tokens_example()  # Descomentar con backend real

    print("¡Listo! Para usar MUSD real:")
    print("1. Instala Paytaca CLI: npm install -g paytaca-cli")
    print("2. Crea/importa wallet: paytaca wallet create --chipnet")
    print("3. Obtén MUSD de un faucet o exchange")
    print("4. Usa backend='paytaca' en BCHPay()")
