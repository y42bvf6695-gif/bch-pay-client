# Instalación rápida de BCHPay

## 5 minutos para tu primer agente que cobra en BCH

### 1. Instalación

```bash
cd bch-pay-client
pip install -e .
```

O con extras:

```bash
pip install -e ".[all]"  # Todas las dependencias
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env si necesitas cambiar red o tokens de bots
```

### 3. Probar con CLI

```bash
python examples/agent_cli.py
```

O instalar como comando:

```bash
pip install -e .
bchpay-cli create 0.01 "Prueba de pago"
```

### 4. Crear tu primer agente

```python
from bch_pay_client import BCHPay

pay = BCHPay()  # Usa testnet por defecto

# Crear factura
invoice = pay.create_invoice(
    amount=0.01,
    description="Consulta de IA"
)

print(f"Dirección: {invoice.address}")
print(f"URL de pago: {pay.get_payment_url(invoice.id)}")

# Verificar (simula después de 5s en modo demo)
if pay.check_payment(invoice.id):
    print("¡Pagado! Entregando resultado...")
```

### 5. Ejecutar agentes preconstruidos

#### API REST (Recomendado para empezar)

```bash
# Terminal 1: Iniciar API
python examples/agent_api.py

# Abre http://localhost:8000/docs para ver endpoints interactivos
# POST /invoices con JSON: {"amount": 0.01, "description": "Test"}
```

#### Bot Discord

```bash
export DISCORD_BOT_TOKEN="tu-token"
python examples/agent_discord.py
# En Discord: !invoice 0.01 "Consulta GPT-4"
```

#### Bot Telegram

```bash
export TELEGRAM_BOT_TOKEN="tu-token"
python examples/agent_telegram.py
# En Telegram: /invoice 0.01 Consulta
```

#### Agente híbrido (todo en uno)

```bash
python examples/agent_hybrid.py
# Inicia API + Discord (si token) + Telegram (si token)
```

### 6. Usar en tu proyecto

```python
from bch_pay_client import BCHPay

pay = BCHPay(
    network="testnet",
    storage_path="./my_wallet.json"
)

# En tu endpoint de FastAPI/Flask/Discord command/etc.
@app.post("/consult")
def consult(prompt: str):
    invoice = pay.create_invoice(
        amount=0.002,
        description=f"Consulta: {prompt[:50]}"
    )
    return {
        "invoice_id": invoice.id,
        "address": invoice.address,
        "qr_code": pay.generate_qr(invoice.id)  # bytes PNG
    }
```

### 7. Verificación real (producción)

Para verificar transacciones reales en mainnet, configura un nodo BCH:

```python
pay = BCHPay(
    network="mainnet",
    bch_node_url="https://jsonrpc.your-bch-node.com"
)
```

O usa la API de Bitcoin.com:
```python
import requests

def get_transaction(txid):
    resp = requests.get(f"https://rest.bitcoin.com/v2/tx/{txid}")
    return resp.json()
```

### 8. Próximos pasos

- **Integra en tu agente de IA**: añade facturas a tus endpoints
- **Automatiza**: usa webhooks para desbloquear contenido tras pago
- **Comparte**: publica tu agente y pide ❤️ en GitHub
- **Contribuye**: añade nuevos agentes de ejemplo a `/examples`

---

¿Problemas? Revisa `docs/troubleshooting.md` o abre un issue.

**¿Listo para ganar BCH con tu agente? 🚀**