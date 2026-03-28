# BCH Trading Advisor

Agente experto en análisis técnico de Bitcoin Cash con bot de Telegram integrado.

## 📊 Características

- **Análisis en tiempo real** usando indicadores técnicos profesionales
- **Señales de trading**: BUY / SELL / HOLD con nivel de confianza
- **Vigilancia automática**: actualizaciones periódicas en Telegram
- **Sin API keys**: datos de mercado gratuitos desde CoinGecko
- **Open source**: puedes modificar la estrategia

## 📈 Indicadores utilizados

- **RSI (Relative Strength Index)**: Detecta sobrecompra/sobreventa
- **MACD (Moving Average Convergence Divergence)**: Momentum y tendencia
- **Bollinger Bands**: Volatilidad y puntos de reversal potenciales

La estrategia combina estos indicadores para generar señales:

| Condición | Puntos | Dirección |
|-----------|--------|-----------|
| RSI < 30 (oversold) | +0.3 | Bullish |
| RSI > 70 (overbought) | -0.3 | Bearish |
| MACD histogram > 0 (bullish crossover) | +0.3 | Bullish |
| MACD histogram < 0 (bearish crossover) | -0.3 | Bearish |
| Price ≤ Bollinger lower band | +0.2 | Bullish |
| Price ≥ Bollinger upper band | -0.2 | Bearish |

**Señal final**:
- ≥ +0.5 → BUY / STRONG_BUY (≥0.7)
- ≤ -0.5 → SELL / STRONG_SELL (≤-0.7)
- Otro → HOLD

## 🚀 Instalación

```bash
# Instalar dependencias
pip install requests python-telegram-bot

# O con extras
pip install bch-pay-client[trading]
```

## 📋 Uso

### 1. Agente de trading standalone (consola)

```bash
# Análisis único
python examples/agent_trading.py

# Formato JSON para scripts
python examples/agent_trading.py --format json

# Modo vigilancia (cada 60 segundos)
python examples/agent_trading.py --watch

# Modo simulación (sin API requests)
python examples/agent_trading.py --simulation
```

**Ejemplo de output**:

```
🟢 **COMPRAR** BCH/USD

💰 Precio actual: $412.34
🎯 Confianza: 65%
📊 Análisis: RSI oversold (28); MACD bullish crossover; Price at Bollinger lower band ($398.12)

**Indicadores**:
• RSI: 28.1
• MACD: 0.0042
• BB Width: $8.50
```

### 2. Bot de Telegram

```bash
# 1. Crear bot en BotFather (https://t.me/botfather)
#    - Obtén tu token

# 2. Ejecutar el bot
TELEGRAM_BOT_TOKEN="123:ABC" python examples/agent_telegram_trading.py
```

**Comandos disponibles**:

| Comando | Descripción |
|---------|-------------|
| `/start` | Mensaje de bienvenida |
| `/price` | Precio actual de BCH |
| `/analyze` | Análisis técnico completo |
| `/signal` | Señal de trading resumida |
| `/watch` | Activar vigilancia automática (cada 5 min) |
| `/stop` | Detener vigilancia |
| `/help` | Esta ayuda |

### 3. Integración en tu propio código

```python
from agent_trading import BCHTradingExpert

# Crear experto
expert = BCHTradingExpert()

# Obtener datos y señal
market = expert.fetch_current_price()
signal = expert.generate_signal(market)

print(f"Señal: {signal.signal.value}")
print(f"Confianza: {signal.confidence * 100}%")
print(f"Razón: {signal.reason}")

# Recomendación formateada
print(expert.get_recommendation(signal))
```

## ⚠️ Advertencias importantes

1. **No es asesoramiento financiero** – Solo es un análisis técnico automatizado.
2. **Riesgo alto** – El trading de criptomonedas es extremadamente volátil.
3. **Solo arriesga lo que puedas perder** – Nunca inviertas dinero necesario.
4. **Haz tu propia investigación (DYOR)** – Verifica señales manualmente.
5. **No confíes ciegamente** – Los indicadores fallan en mercados laterales.

## 🔧 Personalización

Puedes modificar la estrategia en `examples/agent_trading.py`:

```python
# Cambiar parámetros de indicadores
rsi_period = 10  # más sensible
macd_fast = 10   # más rápido

# Ajustar pesos de la estrategia
signal_strength += 0.4  # dar más peso a RSI
signal_strength -= 0.2  # restar peso a Bollinger

# Añadir nuevos indicadores (SMA, Stochastic, etc.)
sma_50 = self._ema(prices, 50)
sma_200 = self._ema(prices, 200)
if sma_50 > sma_200:
    signal_strength += 0.2  # Golden cross
```

## 🐛 Troubleshooting

### `ModuleNotFoundError: No module named 'telegram'`
Instala: `pip install python-telegram-bot`

### `requests.exceptions.RequestException` al obtener precio
- Verifica tu conexión a internet
- CoinGecko puede estar rate limiting (espera unos minutos)
- Considera usar una API alternativa

### Bot no responde en Telegram
- Verifica que el token sea correcto
- Asegúrate de que el bot esté corriendo (no detenido)
- Revisa logs de error

## 📚 Recursos de trading

- **RSI**: >70 sobrecompra, <30 sobreventa
- **MACD**: Línea azul (MACD) cruzando sobre roja (signal) → bullish
- **Bollinger Bands**: Precio tocando bandas exteriores → posible reversal

## 🔜 Futuras mejoras

- Soporte para múltiples exchanges (precio más preciso)
- Notificaciones push (Telegram, Discord, Email)
- Backtesting automatizado con datos históricos
- Integración con BCHPay para ejecución automática de órdenes (con configuración de risk management)
- Indicadores adicionales: SMA, EMA, Stochastic, Volume Profile
- Alertas de momentum y volumen inusual
