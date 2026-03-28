![Pionero BCH-IA](https://raw.githubusercontent.com/y42bvf6695-gif/bch-pay-client/main/badges/pionero-bch-ia.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PyPI version](https://badge.fury.io/py/bch-pay-client.svg)](https://badge.fury.io/py/bch-pay-client)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

# bch-pay-client

Librería Python minimalista para aceptar pagos en Bitcoin Cash (BCH) en agentes de IA, bots y servicios automatizados.

**¿Por qué?** Los agentes de IA necesitan una forma nativa de monetizar sus servicios. BCH ofrece fees casi cero y pagos globales instantáneos.

```text
💡 Integración: 5 líneas de código
💰 Sin intermediarios, sin comisiones de plataforma
🌐 Compatible con cualquier framework (FastAPI, Flask, Discord.py, Telegram)
🤖 Agentes preconstruidos listos para ejecutar
🛡️ Modo demo para pruebas sin wallet real
⚙️ Backends intercambiables: demo, paytaca, watchtower
```

## 🚀 Quickstart

### Instalación

```bash
pip install bch-pay-client

# Con soporte para QR y web frameworks
pip install bch-pay-client[all]

# Desarrollo (también funciona con poetry)
git clone https://github.com/y42bvf6695-gif/bch-pay-client.git
cd bch-pay-client
pip install -e ".[all]"
```

### Tu primer agente que cobra

```python
from bch_pay_client import BCHPay

pay = BCHPay(network="testnet")  # mainnet en producción

# 1. Crear factura
invoice = pay.create_invoice(
    amount=0.01,  # 0.01 BCH (~$0.50)
    description="Consulta GPT-4: 1000 tokens"
)

# 2. Enviar dirección al usuario
print(f"📍 Paga a: {invoice.address}")
print(f"🔗 {pay.get_payment_url(invoice.id)}")

# 3. Verificar pago
if pay.check_payment(invoice.id):
    print("✅ ¡Pagado! Entregando resultado de IA...")
```

¡Eso es! 5 líneas. Ahora tu agente puede cobrar en BCH.

---

## 🎯 Casos de uso

| Agente | Precio sugerido | Uso típico |
|--------|----------------|------------|
| **LLM API** | $0.002-0.03 / 1K tokens | API similar a OpenAI pero con pagos por uso |
| **Fine-tuning** | 0.1-1 BCH / modelo | Ajustar modelos personalizados |
| **Dataset Marketplace** | Variable | Vender datasets curados |
| **GPU/CPU Rental** | 0.001-0.05 BCH / hora | Alquiler de recursos de cómputo |
| **Image Generation** | 0.001-0.005 BCH / imagen | Stable Diffusion, DALL-E, etc. |
| **Compute Rental** | Por tokens/s | Cómputo genérico (inferencia, transcodificación) |
| **Stablecoin (MUSD) Payments** | $X.XX USD | Precios estables en dólares sin bancos |

**Todos los agentes soportan BCH nativo y CashTokens (MUSD, SLP tokens)**

---

## 🤖 Agentes preconstruidos

Incluimos agentes funcionando en `/examples/`:

| Agente | Descripción | Ejecutar |
|--------|-------------|----------|
| **API REST** | Servidor FastAPI con endpoints `/invoices`, `/check`, `/balance` | `python examples/agent_api.py` |
| **Discord Bot** | Comandos `!invoice <amount>`, `!check <id>` | `DISCORD_BOT_TOKEN=... python examples/agent_discord.py` |
| **Telegram Bot** | Comandos `/invoice`, `/check` | `TELEGRAM_BOT_TOKEN=... python examples/agent_telegram.py` |
| **CLI** | Interfaz de línea de comandos interactiva | `python examples/agent_cli.py` o `python -m bch_pay_client.examples.agent_cli` |
| **Hybrid** | API + Discord + Telegram simultáneo | `python examples/agent_hybrid.py` |
| **Fine-tuning** | Servicio de fine-tuning pagado | `python examples/agent_finetune.py` |
| **Dataset Marketplace** | Venta de datasets | `python examples/agent_dataset_marketplace.py` |
| **GPU Rental** | Alquiler de GPUs por horas | `python examples/agent_gpu_rental.py` |
| **Compute Rental** | Alquiler de cómputo por tokens/s | `python examples/agent_compute_rental.py` |
| **Image Generation** | Generación de imágenes por pago | `python examples/agent_image_gen.py` |
| **LLM API** | API compatible OpenAI con balance prepago | `python examples/agent_llm_api.py` |
| **Stablecoin (MUSD)** | Pagos en USD estables via CashToken | `python examples/agent_token_demo.py` |

Todos los agentes son **autónomos**: pueden ejecutarse como servicios independientes, gestionando sus propios wallets, facturas y verificación de pagos.

> 💡 **Consejo**: Empieza con `agent_api.py` o `agent_cli.py` para entender el flujo, luego adapta a tu caso.

---

## 📚 Documentación

- [Quickstart](docs/quickstart.md) - Guía detallada paso a paso
- [API Reference](docs/api.md) - Referencia completa de BCHPay class
- [Integration Guides](docs/) - FastAPI, Discord, Telegram, Webhooks
- [CashToken Support](docs/tokens.md) - Guía completa de tokens (MUSD, SLP)
- [Troubleshooting](docs/troubleshooting.md) - Soluciones comunes
- [Contributing](CONTRIBUTING.md) - Cómo contribuir, badges, code of conduct
- [Roadmap](ROADMAP.md) - Lo que viene

---

## 🔧 Configuración avanzada

### Nodo BCH real (mainnet)

```python
pay = BCHPay(
    network="mainnet",
    bch_node_url="https://jsonrpc.your-bch-node.com",
    explorer_url="https://explorer.bitcoin.com/bch"
)
```

Consulta our [guide](docs/mainnet-setup.md) para configurar un nodo o usar servicios como Bitcoin.com API.

### Webhooks (notificaciones automáticas)

```python
invoice = pay.create_invoice(
    amount=0.01,
    description="Pago",
    metadata={"user_id": "123"},
    callback_url="https://tu-servidor.com/webhook/payment"
)
# Recibirás POST cuando el pago se confirme
```

### Multi-wallet

```python
# Los fondos se acumulan en el storage local
total_earned = pay.total_earned()
print(f"💰 Has ganado: {total_earned} BCH")
```

---

## 🔌 Backends de Producción

Por defecto, `bch-pay-client` usa el **backend demo** (simulación automática). Para pagos reales en mainnet o chipnet, selecciona un backend de producción:

### Paytaca Backend (Experimental)

**Ventajas:** Sin nodo propio, wallet segura en keychain, soporte CashTokens.

**⚠️ Estado Experimental:** Este backend es unwrapper alrededor de `paytaca-cli` y requiere que la CLI soporte salida JSON (actualmente en desarrollo). No se recomienda para producción hasta que se estabilice.

**Requisitos:**
- Node.js 20+
- `npm install -g paytaca-cli`
- Wallet creada: `paytaca wallet create` (o `import`)

**Uso:**

```python
from bch_pay_client import BCHPay

pay = BCHPay(
    backend='paytaca',
    network='testnet',  # o 'mainnet'
    paytaca_cli='paytaca'  # opcional, ruta personalizada
)
```

**Variables de entorno:**
- `BCH_BACKEND=paytaca` - Fuerza uso de Paytaca
- `PAYTACA_CLI=/ruta/personalizada/paytaca`

**Nota:** Si `paytaca` no está instalado, `BCHPay()` auto-selecciona el backend `demo`. Para producción estable, se recomienda esperar al backend `watchtower` (API directa) o integrar tu propio nodo BCH.

### Watchtower Backend (próximamente)

Backend directo vía API REST (sin Node.js). Usará `watchtower-cash-py` o httpx.

### Paytaca Integration

For detailed setup guide, see [docs/paytaca.md](docs/paytaca.md).

```python
from bch_pay_client import BCHPay

pay = BCHPay(backend='paytaca', network='testnet')
```

**Note:** Paytaca backend is experimental. Requires Node.js 20+ and `paytaca-cli`. See documentation for limitations.

---

## 🧪 Tests

```bash
# Tests unitarios
pytest tests/

# Linting
ruff check bch_pay_client/
black --check bch_pay_client/
```

---

## 🚀 Deployment & Automation

### Publicar nueva versión

1. **Actualizar versión** en `pyproject.toml` (ej: `0.1.1` o `0.2.0-beta`)
2. **Commit y tag:**
   ```bash
   git add .
   git commit -m "Release v0.1.1"
   git tag -a v0.1.1 -m "Release v0.1.1"
   git push origin main --tags
   ```
3. **GitHub Actions** automáticamente:
   - Build del paquete
   - Publica en PyPI
   - Crea GitHub Release

### Configurar PyPI auto-deploy (una sola vez)

1. Ve a https://pypi.org/manage/account/token/
2. Crea API token con scope `Entire account`
3. En GitHub repo → Settings → Secrets and variables → Actions
4. Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: pega el token (empieza con `pypi-`)
5. Guardar

Ahora cada tag `v*` se publica automáticamente.

---

## 🤝 Contribuir

¡Contribuciones bienvenidas! Lee [CONTRIBUTING.md](CONTRIBUTING.md).

**Tabla de contribuidores:**

| Contributor | Badge | PRs | Tipo |
|-------------|-------|-----|------|
| @tun编 | ![Pionero](https://raw.githubusercontent.com/y42bvf6695-gif/bch-pay-client/main/badges/pionero-bch-ia.svg) | 1 | Librería base |

> ¿Quieres aparecer aquí? Haz tu primer PR!

---

## 📜 Licencia

MIT - ver [LICENSE](LICENSE) detalles.

---

## 💬 Contacto

- **Issues**: [GitHub Issues](https://github.com/y42bvf6695-gif/bch-pay-client/issues)
- **Discord**: `#bch-pay-client` en [Discord BCH](https://discord.gg/bch)
- **Twitter**: [@bch_ia](https://twitter.com/bch_ia)

---

**Construyendo la economía de agentes autónomos con Bitcoin Cash. 🚀**

> *"Payments should be as programmable as the agents themselves."*