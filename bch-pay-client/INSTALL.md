# Instalación y despliegue de BCHPay

## Requisitos

- Python 3.9+
- Git (opcional)

## Método 1: Poetry (Recomendado)

```bash
git clone https://github.com/y42bvf6695-gif/bch-pay-client.git
cd bch-pay-client

poetry install --all-extras  # instala todas las dependencias
poetry shell  # activa venv
```

## Método 2: pip + venv

```bash
git clone https://github.com/y42bvf6695-gif/bch-pay-client.git
cd bch-pay-client
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -e ".[all]"  # con todos los extras
```

## Método 3: Docker (Próximamente)

```bash
docker pull bchia/bch-pay-client:latest
docker run -p 8000:8000 bchia/bch-pay-client agent_api
```

---

## Configuración inicial

```bash
# 1. Copiar variables de entorno
cp .env.example .env

# 2. (Opcional) Editar .env
#    - BCH_NETWORK=testnet (default) o mainnet
#    - DISCORD_BOT_TOKEN=... si usarás Discord
#    - TELEGRAM_BOT_TOKEN=... si usarás Telegram

# 3. Crear directorio de storage (opcional, por defecto ~/.bch_pay.json)
mkdir -p /data
chmod 700 /data
```

---

## Probar la instalación

```bash
# CLI interactive
bchpay-cli

# O ejecutar script directo
python examples/agent_cli.py

# API REST
python examples/agent_api.py
# Abre http://localhost:8000/docs

# Agente híbrido (API + bots si tokens configurados)
python examples/agent_hybrid.py
```

---

## Configurar bots (opcional)

### Discord Bot

1. Crear app en https://discord.com/developers/applications
2. Bot tab → Reset Token → copiar a `.env`: `DISCORD_BOT_TOKEN=...`
3. OAuth2 → URL Generator → scopes: `bot`, permissions: `Send Messages`, `Embed Links`
4. Invitar a tu server
5. Run: `DISCORD_BOT_TOKEN=tu-token python examples/agent_discord.py`

### Telegram Bot

1. Buscar `@BotFather` en Telegram
2. `/newbot` → seguir pasos → obtener token
3. Copiar a `.env`: `TELEGRAM_BOT_TOKEN=...`
4. Run: `TELEGRAM_BOT_TOKEN=tu-token python examples/agent_telegram.py`
5. Buscar tu bot en Telegram y `/start`

---

## Production deployment

### Systemd service

```ini
# /etc/systemd/system/bchpay-agent.service
[Unit]
Description=BCHPay Agent API
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/opt/bchpay-agent
Environment="BCH_NETWORK=mainnet"
Environment="BCH_STORAGE_PATH=/data/bch_pay.json"
ExecStart=/opt/bchpay-agent/venv/bin/python /opt/bchpay-agent/examples/agent_api.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable bchpay-agent
sudo systemctl start bchpay-agent
sudo journalctl -u bchpay-agent -f  # logs
```

---

### Docker Compose

```yaml
version: '3.8'
services:
  bchpay-api:
    image: bchia/bch-pay-client:latest
    command: python examples/agent_api.py
    ports:
      - "8000:8000"
    volumes:
      - ./data:/data
      - ./.env:/app/.env:ro
    environment:
      - BCH_NETWORK=${BCH_NETWORK:-testnet}
      - BCH_STORAGE_PATH=/data/bch_pay.json
    restart: unless-stopped
```

---

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bchpay-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: bchpay
  template:
    metadata:
      labels:
        app: bchpay
    spec:
      containers:
      - name: api
        image: bchia/bch-pay-client:latest
        command: ["python", "examples/agent_api.py"]
        ports:
        - containerPort: 8000
        env:
        - name: BCH_NETWORK
          value: "testnet"
        volumeMounts:
        - name: storage
          mountPath: /data
      volumes:
      - name: storage
        persistentVolumeClaim:
          claimName: bchpay-pvc
```

---

## Mainnet checklist

⚠️ **Solo para producción con BCH real**:

- [ ] Usar `BCH_NETWORK=mainnet`
- [ ] Configurar `bch_node_url` con tu nodo BCH propio (no usar nodos públicos)
- [ ] Habilitar firewall (solo puertos necesarios: 8000, 8332/443 si nodo local)
- [ ] HTTPS obligatorio (con nginx/Traefik reverse proxy)
- [ ] Backup automático de storage cada hora
- [ ] Limitar `POST /invoices` a usuarios autenticados (API key/JWT)
- [ ] Rate limiting (ej: 10 invoices por minuto por IP)
- [ ] Alertas en Discord/Telegram para facturas >0.1 BCH
- [ ] Retirar fondos a cold wallet regularmente
- [ ] Monitorear gastos de memoria de storage JSON (crece lineal)

---

## Backup & restore

### Backup manual

```bash
tar -czf backup_$(date +%F).tar.gz ~/.bch_pay.json
# En mainnet, también backup de wallet.keys si usas wallet integrada
```

### Restore

```bash
cp backup_2026-03-28.tar.gz .
tar -xzf backup_*.tar.gz
chmod 600 ~/.bch_pay.json
```

---

## Actualizar

```bash
git pull origin main
poetry install  # o pip install -e .
systemctl restart bchpay-agent  # si usas systemd
```

---

## Logs

```bash
# journalctl (systemd)
sudo journalctl -u bchpay-agent -f

# Docker
docker logs -f bchpay-agent

# Directo
tail -f ~/.bch_pay.log
```

---

## Soporte

¿Problemas? Revisa [troubleshooting](docs/troubleshooting.md) o abre issue.

**¡Listo! Tu agente ya puede cobrar en BCH. 🚀**