"""
Bot de Telegram para trading advisor de Bitcoin Cash.

Uso:
    TELEGRAM_BOT_TOKEN=<token> python examples/agent_telegram_trading.py

Comandos:
    /price - Precio actual de BCH
    /analyze - Análisis técnico completo
    /signal - Señal de trading (BUY/SELL/HOLD)
    /watch - Activar vigilancia automática (cada 5 min)
    /stop - Detener vigilancia
    /help - Esta ayuda
"""

import os
import sys
import asyncio
import argparse
from datetime import datetime
from typing import Dict, Set

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, ContextTypes
    from telegram.error import TelegramError
    HAS_TELEGRAM = True
except ImportError:
    HAS_TELEGRAM = False

from agent_trading import BCHTradingExpert, Signal


class TradingBot:
    """Bot de Telegram que usa el agente de trading."""

    def __init__(self, token: str):
        self.token = token
        self.watching_chats: Set[int] = set()  # Chat IDs en modo vigilancia
        self.application = Application.builder().token(token).build()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mensaje de bienvenida."""
        welcome = """
🚀 **BCH Trading Advisor Bot**

Agente experto en análisis de Bitcoin Cash.

📊 **Comandos disponibles**:
/price - Precio actual BCH
/analyze - Análisis técnico completo
/signal - Señal de trading (BUY/SELL/HOLD)
/watch - Vigilancia automática cada 5 min
/stop - Detener vigilancia
/help - Esta ayuda

⚠️  **Advertencia**: Solo es asesoramiento informativo.
No es asesoramiento financiero. Invierte con cuidado.
"""
        await update.message.reply_text(welcome, parse_mode="Markdown")

    async def price(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra precio actual de BCH."""
        try:
            expert = BCHTradingExpert()
            report = expert.run_analysis("text")
            # Extraer solo el precio del reporte
            await update.message.reply_text(f"💰 {report.splitlines()[1]}", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def analyze(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Análisis técnico completo."""
        try:
            expert = BCHTradingExpert()
            report = expert.run_analysis("text")
            await update.message.reply_text(report, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def signal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Señal de trading resumida."""
        try:
            expert = BCHTradingExpert()
            market = expert.fetch_current_price()
            signal_obj = expert.generate_signal(market)

            emoji = "🟢" if signal_obj.signal in (Signal.BUY, Signal.STRONG_BUY) else "🔴" if signal_obj.signal in (Signal.SELL, Signal.STRONG_SELL) else "⚪"
            action = signal_obj.signal.value.replace("_", " ").title()

            msg = f"""
{emoji} **SEÑAL BCH/USD**

📈 Acción recomendada: **{action}**
🎯 Confianza: {signal_obj.confidence * 100:.0f}%
💵 Precio: ${signal_obj.price:.2f}

💡 Razón: {signal_obj.reason}
"""
            await update.message.reply_text(msg, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def watch(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Activa vigilancia automática."""
        chat_id = update.effective_chat.id
        self.watching_chats.add(chat_id)
        await update.message.reply_text(
            "✅ Vigilancia activada. Te enviaré actualizaciones cada 5 minutos.\n"
            "Usa /stop para detener."
        )

    async def stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Detiene la vigilancia."""
        chat_id = update.effective_chat.id
        if chat_id in self.watching_chats:
            self.watching_chats.remove(chat_id)
            await update.message.reply_text("🛑 Vigilancia detenida.")
        else:
            await update.message.reply_text("No estabas en modo vigilancia.")

    async def send_watch_updates(self):
        """Tarea de fondo que envía actualizaciones a los chats en vigilancia."""
        while True:
            await asyncio.sleep(300)  # 5 minutos
            if not self.watching_chats:
                continue

            try:
                expert = BCHTradingExpert()
                report = expert.run_analysis("text")
                for chat_id in self.watching_chats:
                    try:
                        await self.application.bot.send_message(
                            chat_id=chat_id,
                            text=f"🔔 **Actualización BCH**\n{report}",
                            parse_mode="Markdown"
                        )
                    except TelegramError as e:
                        print(f"Failed to send to {chat_id}: {e}")
                        self.watching_chats.discard(chat_id)  # Remove invalid chat
            except Exception as e:
                print(f"Error en vigilancia: {e}")

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja errores."""
        print(f"Error: {context.error}")
        if update and update.effective_message:
            await update.effective_message.reply_text("❌ Ha ocurrido un error.")

    def run(self):
        """Inicia el bot."""
        print("🤖 Iniciando BCH Trading Advisor Bot...")

        # Registrar handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("price", self.price))
        self.application.add_handler(CommandHandler("analyze", self.analyze))
        self.application.add_handler(CommandHandler("signal", self.signal))
        self.application.add_handler(CommandHandler("watch", self.watch))
        self.application.add_handler(CommandHandler("stop", self.stop))
        self.application.add_error_handler(self.error_handler)

        # Tarea de fondo para vigilancia
        self.application.job_queue.run_once(lambda ctx: asyncio.create_task(self.send_watch_updates()), 5)

        print("✅ Bot corriendo. Presiona Ctrl+C para detener.")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    if not HAS_TELEGRAM:
        print("❌ python-telegram-bot no instalado. Ejecuta:")
        print("   pip install python-telegram-bot")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Bot de Telegram para trading de BCH")
    parser.add_argument("--token", type=str, help="Token del bot (o usa env TELEGRAM_BOT_TOKEN)")
    args = parser.parse_args()

    token = args.token or os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ Debes proporcionar --token o configurar TELEGRAM_BOT_TOKEN")
        print("Ejemplo: TELEGRAM_BOT_TOKEN=123:ABC python examples/agent_telegram_trading.py")
        sys.exit(1)

    bot = TradingBot(token)
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido.")


if __name__ == "__main__":
    main()
