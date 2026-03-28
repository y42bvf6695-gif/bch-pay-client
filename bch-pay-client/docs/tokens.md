# CashToken Support (MUSD, SLPs, NFTs)

`bch-pay-client` soporta **CashTokens** (fungible tokens y NFTs) en BCH, incluyendo MUSD y otros stablecoins.

## Quick Example

```python
from bch_pay_client import BCHPay

# MUSD token category ID (mainnet/chipnet)
MUSD_CATEGORY = "e90b1965dc200e3c8d5f899a9e8e146c073552418b266d3a87238777a6d3d227"

pay = BCHPay(backend='paytaca', network='testnet')

# 1. Crear invoice en MUSD
invoice = pay.create_invoice(
    amount=1.0,  # 1 MUSD ≈ $1.00
    description="Suscripción mensual",
    token_category=MUSD_CATEGORY
)

print(f"Paga {invoice.amount} MUSD a: {invoice.address}")

# 2. Verificar pago
if pay.check_payment(invoice.id):
    print("✅ MUSD recibido!")

# 3. Consultar balance de MUSD
balance = pay.get_balance(token_category=MUSD_CATEGORY)
print(f"Tienes {balance} MUSD")

# 4. Enviar MUSD a alguien
result = pay.send_payment(
    address="bchtest:z...",
    amount=0.5,
    token_category=MUSD_CATEGORY
)
```

---

## ¿Qué son CashTokens?

Bitcoin Cash soporta tokens nativos (similar a ERC-20) con:
- **Fungible tokens**: MUSD, tokens de proyectos, etc.
- **NFTs**: tokens no-fungibles (bajo CashTokens estándar)
- Fees bajos ($0.001-0.01), confirmaciones rápidas (~10s)

MUSD es un stablecoin dollar-pegged en BCH. Su categoría (category ID) es única y constante:

```
MUSD Category: e90b1965dc200e3c8d5f899a9e8e146c073552418b266d3a87238777a6d3d227
```

---

## API de Tokens

### BCHPay.create_invoice(amount, description, token_category=None)

Crea una factura para BCH (por defecto) o un token específico.

- `token_category`: ID de categoría del token (64 hex chars, sin prefijo)
- La dirección generada será **token-aware** (prefijo `z` en testnet/mainnet)

### BCHPay.get_balance(token_category=None)

- Sin argumento → devuelve balance BCH
- Con `token_category` → devuelve balance de ese token

### BCHPay.check_payment(invoice_id)

Funciona igual para BCH y tokens. Detecta automáticamente si la invoice es de token y escanea el historial correspondiente.

### BCHPay.send_payment(address, amount, token_category=None)

Envía BCH (por defecto) o token.

- Para tokens, el `address` debe ser **token-aware** (prefijo `z:` o `bitcoincash:`)
- `token_category` es Required para enviar tokens

### BCHPay.list_tokens()

Devuelve lista de tokens en la wallet (solo backends que lo soportan, ej: Paytaca).

Cada token dict incluye:
```python
{
    "category": "e90b...",      # hex category
    "symbol": "MUSD",
    "name": "Metal USD",
    "decimals": 8,
    "balance": 123.45           # unidades (considerando decimals)
}
```

---

## Backends compatibles

| Backend | BCH | Tokens | list_tokens() | send_token |
|---------|-----|--------|---------------|------------|
| Demo | ✅ (simulado) | ✅ (simulado) | ✅ (empty) | ❌ (not impl) |
| Paytaca CLI | ✅ | ✅ | ✅ | ✅ |
| Watchtower (próx) | ✅ | ✅ | ✅ | ✅ |

---

## Token-aware addresses

Los tokens **no** se envían a direcciones BCH normales (`bitcoincash:...`). Requieren direcciones **token-aware** (con prefijo `z` en testnet/mainnet):

- BCH normal: `bitcoincash:...`
- Token-aware: `bchtest:z...` (testnet) o `bitcoincash:z...` (mainnet)

Paytaca CLI y este backend se encargan de generar/derivar las direcciones correctas cuando especificas `token_category`.

---

## MUSD específicamente

MUSD es el stablecoin principal de BCH. Se usa así:

```python
from bch_pay_client import BCHPay

pay = BCHPay(backend='paytaca', network='mainnet')

# Invoice por $5.00 USD
inv = pay.create_invoice(
    amount=5.0,  # 5 MUSD = $5.00
    description="Coffee subscription",
    token_category="e90b1965dc200e3c8d5f899a9e8e146c073552418b266d3a87238777a6d3d227"
)

# Verificar balance MUSD
musd = pay.get_balance(
    token_category="e90b1965dc200e3c8d5f899a9e8e146c073552418b266d3a87238777a6d3d227"
)
print(f"Tienes {musd} MUSD")
```

---

## Limitaciones (Demo backend)

- Demo mode **no simula tokens reales**: `get_balance(token_category)` devuelve 0
- Demo mode `list_tokens()` devuelve `[]`
- Demo mode `send_payment` con tokens falla
- Para probar tokens, usa `backend='paytaca'` con wallet que tenga tokens

---

## Posibles errores

### "Token address required"
- Estás enviando un token a una dirección BCH normal.
- Usa dirección token-aware (z-prefix). Paytaca genera automáticamente la correcta al crear invoice.

### "Paytaca error: ... token not found"
- La wallet no tiene ese token, o el `token_category` es incorrecto.
- Verifica el category ID (MUSD = `e90b1965...`)

### Balance 0 pero debería haber tokens
- Asegúrate de usar `token_category` correcto.
- En Paytaca CLI, verifica: `paytaca token list`

---

## Precios en USD vs BCH

Con MUSD puedes precios en dólares estables:

```python
def price_in_musd(usd_cents):
    """Convierte centavos de USD a MUSD (asume 1 MUSD = $1)."""
    return usd_cents / 100.0

invoice = pay.create_invoice(
    amount=price_in_musd(49),  # $0.49
    description="AI chat 50 msgs",
    token_category=MUSD_CATEGORY
)
```

---

## NFT Support (WIP)

Los NFTs también son CashTokens pero con `capability` minting/mutable. Actualmente no soportados en la API (solo fungibles). Futuro: `BCHPay.create_nft_invoice()` y `BCHPay.send_nft()`.

---

## Watchtower Backend (próximamente)

El backend Watchtower directo (sin CLI) ofrecerá:
- Sin Node.js requerido
- Webhooks para pagos de tokens
- Más rápido (HTTP directo)
- Soporte completo NFTs

---

¿Preguntas? Abre un issue o consulta la [Guía Paytaca](paytaca.md).
