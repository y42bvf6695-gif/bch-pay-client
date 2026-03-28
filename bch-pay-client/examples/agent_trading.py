"""
Agente experto en trading de Bitcoin Cash (BCH).

Este agente analiza el mercado de BCH y proporciona:
- Señales de trading basadas en indicadores técnicos
- Recomendaciones de compra/venta/espera
- Análisis de tendencia y soporte/resistencia
- Alertas de momentum

⚠️  ADVERTENCIA: Este agente es solo para fines educativos.
No es asesoramiento financiero. El trading conlleva riesgos significativos.
Solo arriesga lo que estés dispuesto a perder.
"""

import time
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class Signal(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"


@dataclass
class MarketData:
    """Datos del mercado BCH."""
    price: float
    volume_24h: float
    high_24h: float
    low_24h: float
    timestamp: datetime


@dataclass
class TradingSignal:
    """Señal de trading generada."""
    signal: Signal
    confidence: float  # 0.0 a 1.0
    reason: str
    price: float
    indicators: Dict[str, float]
    timestamp: datetime


class BCHTradingExpert:
    """Agente experto en análisis de trading de BCH."""

    # APIs públicas (sin API key)
    COINGECKO_API = "https://api.coingecko.com/api/v3"
    BCH_PRICE_ID = "bitcoin-cash"

    def __init__(self, simulation_mode: bool = True):
        self.simulation_mode = simulation_mode
        self.price_history: List[Tuple[datetime, float]] = []
        self.indicators_cache: Dict[str, float] = {}

    def fetch_current_price(self) -> MarketData:
        """Obtiene precio actual de BCH desde CoinGecko."""
        if not HAS_REQUESTS:
            raise RuntimeError("requests library required. Install with: pip install requests")

        url = f"{self.COINGECKO_API}/coins/{self.BCH_PRICE_ID}"
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "false",
            "developer_data": "false",
            "sparkline": "false"
        }

        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()["market_data"]

        return MarketData(
            price=data["current_price"]["usd"],
            volume_24h=data["total_volume"]["usd"],
            high_24h=data["high_24h"]["usd"],
            low_24h=data["low_24h"]["usd"],
            timestamp=datetime.utcnow()
        )

    def calculate_rsi(self, period: int = 14) -> float:
        """Calcula RSI (Relative Strength Index)."""
        if len(self.price_history) < period + 1:
            return 50.0  # Valor neutral por defecto

        prices = [p[1] for p in self.price_history[-period-1:]]
        gains = []
        losses = []
        for i in range(1, len(prices)):
            diff = prices[i] - prices[i-1]
            if diff > 0:
                gains.append(diff)
            else:
                losses.append(abs(diff))

        avg_gain = sum(gains) / period if gains else 0
        avg_loss = sum(losses) / period if losses else 0.0001  # Evitar división por cero

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 2)

    def calculate_macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
        """Calcula MACD (Moving Average Convergence Divergence)."""
        prices = [p[1] for p in self.price_history]
        if len(prices) < slow + signal:
            return 0.0, 0.0, 0.0

        # EMAs simples
        ema_fast = self._ema(prices, fast)
        ema_slow = self._ema(prices, slow)
        macd_line = ema_fast - ema_slow

        # Signal line = EMA de MACD
        macd_history = []
        for i in range(slow, len(prices)):
            e_fast = self._ema(prices[:i+1], fast)
            e_slow = self._ema(prices[:i+1], slow)
            macd_history.append(e_fast - e_slow)

        signal_line = self._ema(macd_history[-signal:], signal) if len(macd_history) >= signal else 0
        histogram = macd_line - signal_line

        return round(macd_line, 4), round(signal_line, 4), round(histogram, 4)

    def _ema(self, prices: List[float], period: int) -> float:
        """Calcula Exponential Moving Average."""
        if len(prices) < period:
            return sum(prices) / len(prices)
        multiplier = 2 / (period + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        return ema

    def calculate_bollinger_bands(self, period: int = 20, std_dev: float = 2.0) -> Tuple[float, float, float]:
        """Calcula Bollinger Bands."""
        prices = [p[1] for p in self.price_history[-period:]]
        if len(prices) < period:
            mean = prices[-1] if prices else 0
            return mean, mean, mean

        mean = sum(prices) / period
        variance = sum((p - mean) ** 2 for p in prices) / period
        std = variance ** 0.5

        upper = mean + (std_dev * std)
        lower = mean - (std_dev * std)

        return round(mean, 2), round(upper, 2), round(lower, 2)

    def update_price_history(self, price: float):
        """Añade precio actual al historial."""
        self.price_history.append((datetime.utcnow(), price))
        # Mantener solo últimos 100 datos
        if len(self.price_history) > 100:
            self.price_history = self.price_history[-100:]

    def generate_signal(self, market_data: MarketData) -> TradingSignal:
        """Genera señal de trading basada en múltiples indicadores."""
        self.update_price_history(market_data.price)

        # Calcular indicadores
        rsi = self.calculate_rsi()
        macd, signal_line, histogram = self.calculate_macd()
        bb_ma, bb_upper, bb_lower = self.calculate_bollinger_bands()

        indicators = {
            "rsi": rsi,
            "macd": macd,
            "macd_signal": signal_line,
            "macd_hist": histogram,
            "bb_upper": bb_upper,
            "bb_lower": bb_lower,
            "bb_width": bb_upper - bb_lower
        }

        # Lógica de trading (estrategia simple)
        reasons = []
        signal_strength = 0.0

        # RSI
        if rsi < 30:
            reasons.append(f"RSI oversold ({rsi})")
            signal_strength += 0.3
        elif rsi > 70:
            reasons.append(f"RSI overbought ({rsi})")
            signal_strength -= 0.3

        # MACD
        if histogram > 0 and macd > signal_line:
            reasons.append("MACD bullish crossover")
            signal_strength += 0.3
        elif histogram < 0 and macd < signal_line:
            reasons.append("MACD bearish crossover")
            signal_strength -= 0.3

        # Bollinger Bands
        if market_data.price <= bb_lower:
            reasons.append(f"Price at Bollinger lower band (${market_data.price:.2f})")
            signal_strength += 0.2
        elif market_data.price >= bb_upper:
            reasons.append(f"Price at Bollinger upper band (${market_data.price:.2f})")
            signal_strength -= 0.2

        # Determinar señal final
        final_signal = Signal.HOLD
        if signal_strength >= 0.5:
            final_signal = Signal.STRONG_BUY if signal_strength > 0.7 else Signal.BUY
        elif signal_strength <= -0.5:
            final_signal = Signal.STRONG_SELL if signal_strength < -0.7 else Signal.SELL

        confidence = min(abs(signal_strength) * 2, 1.0)

        return TradingSignal(
            signal=final_signal,
            confidence=round(confidence, 2),
            reason="; ".join(reasons) if reasons else "No clear signal, wait",
            price=market_data.price,
            indicators=indicators,
            timestamp=datetime.utcnow()
        )

    def get_recommendation(self, signal: TradingSignal) -> str:
        """Convierte señal a recomendación legible."""
        emoji_map = {
            Signal.STRONG_BUY: "🔥🔥",
            Signal.BUY: "🟢",
            Signal.HOLD: "⚪",
            Signal.SELL: "🔴",
            Signal.STRONG_SELL: "🔥🔥"
        }

        action_map = {
            Signal.STRONG_BUY: "COMPRA FUERTE",
            Signal.BUY: "COMPRAR",
            Signal.HOLD: "MANTENER/ESPERAR",
            Signal.SELL: "VENDER",
            Signal.STRONG_SELL: "VENTA FUERTE"
        }

        return f"""
{emoji_map[signal.signal]} **{action_map[signal.signal]}** BCH/USD

💰 **Precio actual**: ${signal.price:.2f}
🎯 **Confianza**: {signal.confidence * 100:.0f}%
📊 **Análisis**: {signal.reason}

**Indicadores**:
• RSI: {signal.indicators['rsi']:.1f}
• MACD: {signal.indicators['macd']:.4f}
• BB Width: ${signal.indicators['bb_width']:.2f}

⚠️  **Recuerda**: Esto es solo análisis. Investiga por tu cuenta.
""".strip()

    def run_analysis(self, report_format: str = "text") -> str:
        """Ejecuta análisis completo y devuelve reporte."""
        try:
            market = self.fetch_current_price()
            signal = self.generate_signal(market)

            if report_format == "json":
                return json.dumps({
                    "timestamp": signal.timestamp.isoformat(),
                    "price": signal.price,
                    "signal": signal.signal.value,
                    "confidence": signal.confidence,
                    "reason": signal.reason,
                    "indicators": signal.indicators
                }, indent=2)
            else:
                return self.get_recommendation(signal)

        except Exception as e:
            return f"❌ Error obteniendo datos: {str(e)}"


def main():
    parser = argparse.ArgumentParser(description="Agente experto en trading de BCH")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Formato de salida")
    parser.add_argument("--simulation", action="store_true", help="Modo simulación (usa datos ficticios)")
    parser.add_argument("--watch", action="store_true", help="Modo vigilancia continua (cada 60s)")
    args = parser.parse_args()

    expert = BCHTradingExpert(simulation_mode=args.simulation)

    if args.watch:
        print("🔄 Modo vigilancia activado (Ctrl+C para detener)...")
        try:
            while True:
                report = expert.run_analysis(args.format)
                print(f"\n[{datetime.utcnow().strftime('%H:%M:%S')}]")
                print(report)
                time.sleep(60)
        except KeyboardInterrupt:
            print("\nVigilancia detenida.")
    else:
        report = expert.run_analysis(args.format)
        print(report)


if __name__ == "__main__":
    main()
