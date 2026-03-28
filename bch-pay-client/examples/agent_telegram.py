#!/usr/bin/env python3
"""
Agente Telegram BCHPay - Bot autónomo

Este agente:
- Procesa /invoice, /check, /balance
- Crea facturas on-demand
- Verifica pagos automáticamente
- Funciona como microservicio Telegram
"""

import os
import asyncio
from typing import Optional

from bch_pay_client import BCHPay, BCHPayError

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application,
        CommandHandler,
        CallbackQueryHandler,
        ContextTypes,
    )
except ImportError:
    print("❌ Instala python-telegram-bot: pip install python-telegram-bot")
    exit(1)


# Configuración
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
pay = BCHPay(network=os.getenv("BCH_NETWORK", "testnet"))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mensaje de bienvenida."""
    user = update.effective_user
    welcome_text = (
        f"👋 ¡Hola {user.first_name}!\n\n"
        "Soy un agente autónomo que procesa pagos en Bitcoin Cash.\n\n"
        "Comandos disponibles:\n"
        "/invoice <amount> <desc> - Crear factura\n"
        "/check <id> - Verificar pago\n"
        "/balance - Ver balance total\n"
        "/invoices - Ver últimas facturas\n"
        "/help - Este mensaje"
    )
    await update.message.reply_text(welcome_text)


async def invoice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Crea una factura: /invoice <amount> <description>"""
    if len(context.args) < 1:
        await update.message.reply_text(
            "💡 Uso: /invoice <cantidad> [descripción]\n"
            "Ejemplo: /invoice 0.01 Consulta GPT-4"
        )
        return

    try:
        amount = float(context.args[0])
        if amount <= 0:
            await update.message.reply_text("❌ La cantidad debe ser > 0")
            return
    except ValueError:
        await update.message.reply_text("❌ Cantidad inválida")
        return

    description = " ".join(context.args[1:]) if len(context.args) > 1 else "Pago IA"

    try:
        invoice = pay.create_invoice(
            amount=amount,
            description=f"@{update.effective_user.username}: {description}",
            metadata={
                "user_id": str(update.effective_user.id),
                "username": update.effective_user.username or "",
            }
        )

        keyboard = [
            [InlineKeyboardButton("🔗 Ver en explorador", url=pay.get_payment_url(invoice.id))],
            [InlineKeyboardButton("✅ Verificar", callback_data=f"check_{invoice.id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = (
            f"📦 *Factura Creada*\n\n"
            f"💰 *Monto:* `{invoice.amount} BCH`\n"
            f"📝 *Descripción:* {invoice.description}\n"
            f"🏷️ *ID:* `{invoice.id[:12]}...`\n"
            f"📍 *Dirección:* `{invoice.address}`\n\n"
            f"Usa /check {invoice.id[:8]} para verificar."
        )

        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

        # Intentar enviar QR si hay qrcode instalado
        try:
            qr_bytes = pay.generate_qr(invoice.id, size=300)
            await update.message.reply_photo(
                photo=qr_bytes,
                caption=f"QR para pagar {invoice.amount} BCH"
            )
        except Exception:
            pass  # qrcode no instalado, ok

    except BCHPayError as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verifica estado de pago: /check <invoice_id>"""
    if len(context.args) < 1:
        await update.message.reply_text("💡 Uso: /check <invoice_id>")
        return

    invoice_id = context.args[0]

    # Buscar factura por ID parcial
    all_invoices = pay.list_invoices(limit=100)
    invoice = next(
        (inv for inv in all_invoices if inv.id.startswith(invoice_id)),
        None
    )

    if not invoice:
        await update.message.reply_text("❌ Factura no encontrada")
        return

    if pay.check_payment(invoice.id):
        text = (
            "✅ *PAGO RECIBIDO*\n\n"
            f"💰 Monto: {invoice.amount} BCH\n"
            f"🔗 TXID: `{invoice.txid}`\n"
            f"⏰ Confirmado: <t:{int(invoice.paid_at)}:R>"
        )
        await update.message.reply_text(text, parse_mode="Markdown")
    else:
        text = (
            "⏳ *PENDIENTE*\n\n"
            f"💰 Monto: {invoice.amount} BCH\n"
            f"📍 Dirección: `{invoice.address}`\n"
            f"🔗 URL: {pay.get_payment_url(invoice.id)}"
        )
        await update.message.reply_text(text, parse_mode="Markdown")


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra balance total."""
    total = pay.total_earned()
    text = (
        "💰 *Balance del Agente*\n\n"
        f"`{total:.6f}` BCH\n"
        f"≈ `${total * 50:.2f}` USD*"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def invoices_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista últimas facturas."""
    limit = 10
    try:
        if len(context.args) > 0:
            limit = min(int(context.args[0]), 50)
    except ValueError:
        pass

    invoices = pay.list_invoices(limit=limit)

    if not invoices:
        await update.message.reply_text("📜 No hay facturas aún.")
        return

    text = f"📜 *Últimas {len(invoices)} facturas:*\n\n"
    for i, inv in enumerate(invoices[:10], 1):
        status = "✅" if inv.paid else "⏳"
        text += (
            f"{i}. {status} `{inv.id[:8]}`\n"
            f"   {inv.amount} BCH - {inv.description[:40]}\n"
        )

    await update.message.reply_text(text, parse_mode="Markdown")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja clicks en botones inline."""
    query = update.callback_query
    await query.answer()

    if query.data.startswith("check_"):
        invoice_id = query.data[6:]  # remover "check_"
        invoice = pay.get_invoice(invoice_id)

        if not invoice:
            await query.edit_message_text("❌ Factura no encontrada")
            return

        if pay.check_payment(invoice.id):
            await query.edit_message_text(
                f"✅ *Factura pagada*\n"
                f"Monto: {invoice.amount} BCH\n"
                f"TXID: `{invoice.txid[:16]}...`",
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                f"⏳ *Factura pendiente*\n"
                f"Monto: {invoice.amount} BCH\n"
                f"Dirección: `{invoice.address}`",
                parse_mode="Markdown"
            )


def main():
    """Inicia el bot de Telegram."""
    if not TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN no configurado")
        exit(1)

    print("🤖 Iniciando Agente Telegram BCHPay...")
    print(f"📡 Red BCH: {pay.network}")
    print(f"💰 Balance: {pay.total_earned():.6f} BCH")

    application = Application.builder().token(TOKEN).build()

    # Handlers
    application.add_handler(commands := [
        ("start", start),
        ("help", start),
        ("invoice", invoice_command),
        ("check", check_command),
        ("balance", balance_command),
        ("invoices", invoices_command)
    ])
    for cmd, handler in commands:
        application.add_handler(CommandHandler(cmd, handler))

    application.add_handler(CallbackQueryHandler(button_callback))

    # Ejecutar
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()