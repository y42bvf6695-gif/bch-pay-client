# Dockerfile oficial para bch-pay-client
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
COPY pyproject.toml .

# Instalar dependencias Python
RUN pip install --no-cache-dir -e ".[all]"

# Copiar código fuente
COPY bch_pay_client /app/bch_pay_client
COPY examples /app/examples
COPY docs /app/docs
COPY README.md QUICKSTART.md CONTRIBUTING.md LICENSE ./

# Directorio de datos
VOLUME ["/data"]

# Variables de entorno por defecto
ENV BCH_NETWORK=testnet \
    BCH_STORAGE_PATH=/data/bch_pay.json \
    BCHPAY_HOST=0.0.0.0 \
    BCHPAY_PORT=8000 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando por defecto (API REST)
CMD ["python", "examples/agent_api.py"]