#!/usr/bin/env python3
"""
Agente Discord BCHPay - Bot autónomo

Este agente:
- Responde a comandos !invoice, !pay, !balance
- Crea facturas automáticamente
- Verifica pagos en tiempo real
- Funciona como microservicio Discord
"""

import os
import discord
from discord.ext import commands
from typing import Optional

from bch_pay_client import BCHPay, BCHPayError

# Configuración del bot
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PREFIX = os.getenv("BOT_PREFIX", "!")

# Inicializar BCHPay
pay = BCHPay(
    network=os.getenv("BCH_NETWORK", "testnet")
)

# Intents de Discord
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)


@bot.event
async def on_ready():
    print(f"🤖 Agente Discord BCHPay conectado como {bot.user}")
    print(f"📡 Red BCH: {pay.network}")
    print(f"💰 Total ganado: {pay.total_earned():.6f} BCH")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name=f"{pay.total_earned():.4f} BCH ganados"
    ))


@bot.command(name='invoice', aliases=['factura', 'pay'])
async def create_invoice_command(
    ctx,
    amount: float,
    *,
    description: str = "Servicio de IA"
):
    """
    Crea una factura de pago en BCH.

    Uso: !invoice <cantidad> [descripción]
    Ejemplo: !invoice 0.01 Consulta GPT-4
    """
    if amount <= 0:
        await ctx.send("❌ La cantidad debe ser mayor a 0 BCH")
        return

    try:
        invoice = pay.create_invoice(
            amount=amount,
            description=f"{ctx.author}: {description}",
            metadata={
                "user_id": str(ctx.author.id),
                "username": ctx.author.name,
                "channel_id": str(ctx.channel.id)
            }
        )

        embed = discord.Embed(
            title="📦 Factura BCH Creada",
            color=discord.Color.green(),
            description=f"Paga {amount} BCH por: {description}"
        )
        embed.add_field(name="🏷️ ID", value=f"`{invoice.id[:8]}...`", inline=False)
        embed.add_field(name="💳 Dirección", value=f"`{invoice.address}`", inline=False)
        embed.add_field(name="🔗 Pagar", value=f"[Click aquí]({pay.get_payment_url(invoice.id)})", inline=False)
        embed.set_footer(text=f"Creada por {ctx.author}")

        # Adjuntar QR como imagen (requiere qrcode instalado)
        try:
            qr_bytes = pay.generate_qr(invoice.id, size=400)
            file = discord.File(
                fp=__import__('io').BytesIO(qr_bytes),
                filename=f"qr_{invoice.id[:8]}.png"
            )
            embed.set_image(url=f"attachment://qr_{invoice.id[:8]}.png")
            await ctx.send(embed=embed, file=file)
        except ImportError:
            await ctx.send(embed=embed)

        # Enviar mensaje privado con detalles completos
        try:
            await ctx.author.send(
                f"📋 Factura #{invoice.id[:8]}\n"
                f"💵 Amount: {invoice.amount} BCH\n"
                f"🏷️ Desc: {invoice.description}\n"
                f"📍 Dirección: `{invoice.address}`\n"
                f"🔗 URL: {pay.get_payment_url(invoice.id)}\n\n"
                f"Comando para verificar: `!check {invoice.id[:8]}`"
            )
        except discord.Forbidden:
            pass  # DMs deshabilitados

    except BCHPayError as e:
        await ctx.send(f"❌ Error: {str(e)}")


@bot.command(name='check', aliases=['verificar', 'status'])
async def check_invoice_command(ctx, invoice_id: str):
    """
    Verifica el estado de pago de una factura.

    Uso: !check <invoice_id>
    """
    # Buscar por ID parcial
    all_invoices = pay.list_invoices(limit=100)
    invoice = next(
        (inv for inv in all_invoices if inv.id.startswith(invoice_id)),
        None
    )

    if not invoice:
        await ctx.send("❌ Factura no encontrada")
        return

    if pay.check_payment(invoice.id):
        embed = discord.Embed(
            title="✅ Pago Recibido",
            color=discord.Color.green(),
            description=f"Factura `{invoice.id[:8]}...` fue pagada"
        )
        embed.add_field(name="💰 Monto", value=f"{invoice.amount} BCH", inline=True)
        embed.add_field(name="🔗 TXID", value=f"`{invoice.txid[:16]}...`", inline=True)
        embed.add_field(name="⏰ Hora", value=f"<t:{int(invoice.paid_at)}:R>", inline=False)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="⏳ Pendiente",
            color=discord.Color.orange(),
            description=f"Factura `{invoice.id[:8]}...` aún no pagada"
        )
        embed.add_field(name="💵 Monto", value=f"{invoice.amount} BCH", inline=True)
        embed.add_field(name="📍 Dirección", value=f"`{invoice.address}`", inline=False)
        await ctx.send(embed=embed)


@bot.command(name='balance', aliases=['saldo', 'ganancias'])
async def balance_command(ctx):
    """Muestra el balance total ganado por este agente."""
    total = pay.total_earned()
    embed = discord.Embed(
        title="💰 Balance del Agente",
        color=discord.Color.gold(),
        description=f"**{total:.6f} BCH**\n≈ ${total * 50:.2f} USD*"
    )
    embed.set_footer(text="Tasa de cambio estimada: $50/BCH")
    await ctx.send(embed=embed)


@bot.command(name='invoices', aliases=['facturas'])
async def list_invoices_command(ctx, limit: int = 10):
    """Lista las últimas facturas."""
    invoices = pay.list_invoices(limit=limit)

    embed = discord.Embed(
        title=f"📜 Últimas {len(invoices)} facturas",
        color=discord.Color.blue()
    )

    for inv in invoices[:5]:
        status = "✅" if inv.paid else "⏳"
        embed.add_field(
            name=f"{status} {inv.id[:8]}...",
            value=f"{inv.amount} BCH | {inv.description[:30]}...",
            inline=False
        )

    await ctx.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    """Manejo de errores de comandos."""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Falta argumento: `{error.param.name}`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"❌ Argumento inválido: {error}")
    else:
        await ctx.send(f"❌ Error: {str(error)}")


# Ejecutar bot
if __name__ == "__main__":
    if not TOKEN:
        print("❌ DISCORD_BOT_TOKEN no configurado")
        exit(1)

    print("🤖 Iniciando Agente Discord BCHPay...")
    bot.run(TOKEN)