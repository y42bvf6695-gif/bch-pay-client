# Integración con Discord.py

Guía para crear un bot Discord que cobra en BCH.

## Instalación

```bash
pip install bch-pay-client[discord] discord.py
```

## Bot mínimo

```python
import discord
from discord.ext import commands
from bch_pay_client import BCHPay

TOKEN = "TU_DISCORD_BOT_TOKEN"
pay = BCHPay()

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"🤖 Bot online como {bot.user}")

@bot.command(name='invoice')
async def invoice(ctx, amount: float, *, description: str = "Servicio IA"):
    if amount <= 0:
        await ctx.send("❌ Monto debe ser > 0")
        return

    invoice = pay.create_invoice(
        amount=amount,
        description=f"{ctx.author}: {description}",
        metadata={"user_id": str(ctx.author.id)}
    )

    embed = discord.Embed(
        title="📦 Factura BCH",
        color=discord.Color.green()
    )
    embed.add_field(name="💰 Monto", value=f"{invoice.amount} BCH")
    embed.add_field(name="📍 Dirección", value=f"`{invoice.address}`", inline=False)
    embed.add_field(name="🔗 Pagar", value=f"[Click aquí]({pay.get_payment_url(invoice.id)})")
    embed.set_footer(text=f"Creada por {ctx.author}")

    await ctx.send(embed=embed)

    # QR
    try:
        qr_bytes = pay.generate_qr(invoice.id)
        file = discord.File(
            fp=__import__('io').BytesIO(qr_bytes),
            filename=f"qr_{invoice.id[:8]}.png"
        )
        await ctx.send(file=file)
    except Exception:
        pass  # qrcode no instalado

@bot.command(name='check')
async def check(ctx, invoice_id: str):
    all_invoices = pay.list_invoices(limit=100)
    invoice = next((i for i in all_invoices if i.id.startswith(invoice_id)), None)

    if not invoice:
        await ctx.send("❌ Factura no encontrada")
        return

    if pay.check_payment(invoice.id):
        await ctx.send(
            f"✅ **Pagada**\nMonto: {invoice.amount} BCH\nTXID: `{invoice.txid[:16]}...`"
        )
    else:
        await ctx.send(
            f"⏳ **Pendiente**\nMonto: {invoice.amount} BCH\nDirección: `{invoice.address}`"
        )

@bot.command(name='balance')
async def balance(ctx):
    total = pay.total_earned()
    await ctx.send(f"💰 Balance total: **{total:.6f} BCH**")

bot.run(TOKEN)
```

## Comandos avanzados

### Listar facturas

```python
@bot.command(name='invoices')
async def invoices(ctx, limit: int = 10):
    invoices = pay.list_invoices(limit)
    embed = discord.Embed(title=f"📜 Últimas facturas", color=discord.Color.blue())

    for inv in invoices[:5]:
        status = "✅" if inv.paid else "⏳"
        embed.add_field(
            name=f"{status} {inv.id[:8]}...",
            value=f"{inv.amount} BCH | {inv.description[:30]}",
            inline=False
        )

    await ctx.send(embed=embed)
```

### Botón interactivo

```python
from discord.ui import Button, View

class CheckButton(Button):
    def __init__(self, invoice_id: str):
        super().__init__(label="✅ Verificar", style=discord.ButtonStyle.green)
        self.invoice_id = invoice_id

    async def callback(self, interaction: discord.Interaction):
        invoice = pay.get_invoice(self.invoice_id)
        if invoice and pay.check_payment(invoice.id):
            await interaction.response.send_message("✅ ¡Pagada!")
        else:
            await interaction.response.send_message("⏳ Pendiente")

@bot.command()
async def paybutton(ctx, amount: float):
    invoice = pay.create_invoice(amount, "Servicio premium")
    view = View()
    view.add_item(CheckButton(invoice.id))
    await ctx.send(f"Factura: {invoice.id}\nDirección: `{invoice.address}`", view=view)
```

### Roles automáticos tras pago

```python
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Si el usuario pagó, dar rol
    user_invoices = [
        i for i in pay.list_invoices(limit=100)
        if i.metadata.get("user_id") == str(message.author.id) and i.paid
    ]

    if user_invoices and "Premium" not in [r.name for r in message.author.roles]:
        guild = message.guild
        role = discord.utils.get(guild.roles, name="Premium")
        if role:
            await message.author.add_roles(role)
            await message.channel.send(f"🎉 {message.author.mention} ha obtenido rol Premium!")

    await bot.process_commands(message)
```

## Restricciones por canal

```python
ALLOWED_CHANNELS = [123456789012345678]  # IDs de canal

@bot.command()
@commands.has_permissions(administrator=True)
async def allowchannel(ctx, channel: discord.TextChannel = None):
    ALLOWED_CHANNELS.append(channel.id)
    await ctx.send(f"✅ Canal {channel.mention} habilitado para pagos")

@bot.check
async def global_check(ctx):
    if ctx.channel.id not in ALLOWED_CHANNELS:
        await ctx.send("❌ Pagos no permitidos en este canal")
        return False
    return True
```

## Persistencia

El bot guarda facturas en `~/.bch_pay.json` por defecto. Para persistencia en server:

```python
pay = BCHPay(storage_path="/data/bch_pay.json")
```

Asegúrate que el directorio `/data` existe y es escribible.

---

## Despliegue

```bash
# systemd service
[Unit]
Description=Discord BCH Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/opt/bchbot
Environment="DISCORD_BOT_TOKEN=tu-token"
Environment="BCH_NETWORK=testnet"
ExecStart=/opt/bchbot/venv/bin/python /opt/bchbot/agent_discord.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

---

Notas:
- Usa `mainnet` solo con BCH real y pruebas exhaustivas
- Considera rate limiting por usuario (ej: `!invoice` max 10/hora)
- Implementa logging estructurado para auditoría