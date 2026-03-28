# Integración con Telegram

Guía para crear un bot Telegram que procesa pagos en BCH.

## Instalación

```bash
pip install bch-pay-client[telegram] python-telegram-bot
```

## Bot mínimo

```python
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from bch_pay_client import BCHPay

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
pay = BCHPay()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot BCHPay - Paga y recibe servicios de IA\n\n"
        "Comandos:\n"
        "/invoice <amount> <desc> - Crear factura\n"
        "/check <id> - Verificar pago\n"
        "/balance - Ver balance total\n"
        "/invoices - Listar facturas"
    )

async def invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Uso: /invoice <amount> [descripción]")
        return

    try:
        amount = float(context.args[0])
        desc = " ".join(context.args[1:]) or "Pago IA"
    except ValueError:
        await update.message.reply_text("❌ Monto inválido")
        return

    invoice = pay.create_invoice(
        amount=amount,
        description=f"@{update.effective_user.username}: {desc}",
        metadata={"user_id": str(update.effective_user.id)}
    )

    keyboard = [
        [InlineKeyboardButton("🔗 Pagar", url=pay.get_payment_url(invoice.id))],
        [InlineKeyboardButton("✅ Verificar", callback_data=f"check_{invoice.id}")]
    ]

    await update.message.reply_text(
        f"📦 Factura creada\n"
        f"💰 {invoice.amount} BCH\n"
        f"📍 Dir: `{invoice.address}`\n"
        f"ID: `{invoice.id[:12]}...`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Uso: /check <invoice_id>")
        return

    invoice_id = context.args[0]
    invoices = pay.list_invoices(limit=100)
    invoice = next((i for i in invoices if i.id.startswith(invoice_id)), None)

    if not invoice:
        await update.message.reply_text("❌ No encontrada")
        return

    if pay.check_payment(invoice.id):
        await update.message.reply_text(
            f"✅ **Pagada**\n"
            f"Monto: {invoice.amount} BCH\n"
            f"TXID: `{invoice.txid[:16]}...`",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"⏳ **Pendiente**\n"
            f"Dir: `{invoice.address}`",
            parse_mode="Markdown"
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("check_"):
        invoice_id = query.data[6:]
        invoice = pay.get_invoice(invoice_id)

        if invoice and pay.check_payment(invoice.id):
            await query.edit_message_text("✅ Factura pagada!")
        else:
            await query.edit_message_text("⏳ Aún pendiente")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("invoice", invoice))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 Bot Telegram iniciado...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
```

## Features

### QR en mensaje

```python
async def invoice(update, context):
    # ... crear invoice
    qr_bytes = pay.generate_qr(invoice.id)
    await update.message.reply_photo(
        photo=qr_bytes,
        caption=f"QR para pagar {invoice.amount} BCH"
    )
```

### Facturas recurrentes (subscriptions)

```python
from datetime import datetime, timedelta

async def subscription(update, context):
    # Crear factura con metadata mensual
    invoice = pay.create_invoice(
        amount=0.05,
        description="Suscripción mensual Premium",
        metadata={
            "user_id": str(update.effective_user.id),
            "type": "subscription",
            "period": "monthly"
        }
    )
    # Guardar en DB y renovar cada mes
```

### Admin commands

```python
from telegram.ext import filters

@admin_only
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = pay.total_earned()
    await update.message.reply_text(f"💰 Balance: {total:.6f} BCH")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Enviar mensaje a todos los users que han pagado
    paid_users = set()
    for inv in pay.list_invoices(limit=500):
        if inv.paid and inv.metadata:
            paid_users.add(inv.metadata.get("user_id"))

    for user_id in paid_users:
        try:
            await context.bot.send_message(
                chat_id=int(user_id),
                text="📢 Noticia importante..."
            )
        except:
            pass  # user bloqueó bot
```

---

## Variables de entorno

```bash
export TELEGRAM_BOT_TOKEN="123:ABC"
export BCH_NETWORK="testnet"  # o mainnet
```

---

## Despliegue

```bash
# Como servicio systemd
[Service]
ExecStart=/opt/bchbot/venv/bin/python /opt/bchbot/agent_telegram.py
Environment="TELEGRAM_BOT_TOKEN=tu-token"
Restart=always
```

O usa `screen`/`tmux`:

```bash
screen -S bchbot
python agent_telegram.py
# Ctrl+A, D para detacher
screen -r bchbot  # reattach
```

---

Best practices:
- Limita `/invoice` a usuarios verificados si BCH real
- Logs de todas las transacciones
- Backup diario de `~/.bch_pay.json`
- Notifica admin en pagos grandes (>0.1 BCH)
- Rate limiting: max 5 invoices/hora por user

Para soporte: [GitHub Issues](https://github.com/y42bvf6695-gif/bch-pay-client/issues)