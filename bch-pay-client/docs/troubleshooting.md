# Troubleshooting

## Errores comunes

### `ModuleNotFoundError: No module named 'bch_pay_client'`

```bash
pip install -e .
# o
pip install bch-pay-client
```

Si usas Poetry:

```bash
poetry install
```

---

### `ImportError: cannot import name 'BCHPay'`

Asegúrate que estás importando desde el paquete correcto:

```python
# ✅ Correcto
from bch_pay_client import BCHPay

# ❌ Incorrecto
from bch_pay_client.core import BCHPay  # (aunque funcione, usa la API pública)
```

---

### `BCHPayError: Installa 'qrcode' y 'pillow'`

```bash
pip install qrcode pillow
# o con extras
pip install bch-pay-client[qr]
```

---

### `Facturas no se persisten entre ejecuciones`

Verifica que el archivo de storage exista y sea escribible:

```python
pay = BCHPay(storage_path="/ruta/valida/bch_pay.json")
```

Por defecto usa `~/.bch_pay.json`. Asegura permisos:

```bash
touch ~/.bch_pay.json
chmod 600 ~/.bch_pay.json
```

---

### `check_payment() siempre retorna False`

Modo demo: facturas se marcan como pagadas automáticamente después de **5 segundos**.

Si pruebas inmediatamente, está pendiente. Espera o usa `time.sleep(6)`.

Para verificación real en mainnet:

```python
pay = BCHPay(
    network="mainnet",
    bch_node_url="URL_DE_TU_NODO_JSONRPC"
)
```

Y implementa `_check_payment_real()` en `core.py`.

---

### `BCH address inválida`

El cliente genera direcciones de testnet por defecto (`bchtest:`). Para mainnet necesita wallet real.

**Demo/testing ok**: Direcciones testnet válidas (`bchtest:qz...`).

**Mainnet**: Debes conectar a wallet real (Bitcoin.com Electron, Badger, etc.) y modificar `_generate_address()`.

---

### `Esperando verificación real, pero nodo no responde`

Si configuraste `bch_node_url`, verifica:

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"method":"getblockcount","params":[]}' \
  https://tu-nodo.bch
```

Asegura que:
- Nodo está sincronizado
- Usuario RPC tiene permisos
- No firewall bloquea puerto 8332/443

---

### `El agente Discord no responde a comandos`

Verifica:

```bash
# 1. Token correcto
echo $DISCORD_BOT_TOKEN | wc -c  # debe ser >0

# 2. Intents habilitados (message_content=True)
# En https://discord.com/developers/appplications

# 3. Bot invitado al server
# Usa la OAuth2 URL con `bot` y `applications.commands` scopes

# 4. run sin errores al iniciar
python examples/agent_discord.py
```

Logs:

```bash
python examples/agent_discord.py 2>&1 | tee discord.log
```

---

### `Telegram bot: "Forbidden: bot was blocked by the user"`

El usuario bloqueó el bot. No puedes enviarle mensajes. Solo puede iniciar conversación.

---

### `No recuerdo pagos anteriores`

Las facturas se guardan localmente. Si borraste `~/.bch_pay.json`, pierdes historial.

**Backup:**

```bash
cp ~/.bch_pay.json ~/backups/bch_pay_$(date +%F).json
```

---

### `FastAPI: 422 Unprocessable Entity`

Validation error. Revisa tipos:

```bash
curl -X POST http://localhost:8000/invoices \
  -H "Content-Type: application/json" \
  -d '{"amount": 0.01, "description": "Test"}'
```

`amount` debe ser float, `description` string.

---

### `Agent API no inicia: Address already in use`

Puerto 8000 ocupado. Cambia:

```bash
export BCHPAY_PORT=8080
python examples/agent_api.py
```

---

## Debugging

### Habilitar logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Inspeccionar almacenamiento

```bash
cat ~/.bch_pay.json | jq
```

### Ver webhooks recibidos

Si usas API, revisa logs de tu endpoint. El agente envía logs a stdout:

```bash
python examples/agent_api.py | grep -i webhook
```

---

## Preguntas frecuentes

**¿Puedo usar mainnet?** Sí, pero configura tu propio nodo BCH. No confíes en nodos públicos para producción.

**¿Cómo recupero fondos si pierdo el storage?** Los fondos están en las direcciones BCH que generaste. Necesitas las private keys. **Demo/testnet**: seguro. **Mainnet**: usa wallet real exportable.

**¿Hay límite de cantidad de facturas?** No. El storage JSON puede crecer. Considera migrar a PostgreSQL/SQLite para alta escala.

**¿Puedo modificar una factura ya creada?** No. Las facturas son inmutables. Crea una nueva.

**¿Qué pasa si el usuario paga de más?** Se registra el monto exacto pagado. No hay cambio. Considera crear manualmente devolución si es necesario.

---

¿Tu problema no está aquí? Abre un issue con:
- Versión (`pip show bch-pay-client`)
- Python version (`python --version`)
- Logs relevantes
- Pasos para reproducir

**Happy debugging! 🔧**