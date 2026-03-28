# Paytaca Integration Guide

## Overview

The `PaytacaBackend` integrates `bch-pay-client` with the Paytaca CLI wallet, enabling real Bitcoin Cash payments without running your own node.

**Status:** ⚠️ **Experimental** - Requires Paytaca CLI with stable JSON output. Use for testing on chipnet first.

## Requirements

- **Node.js 20+** (https://nodejs.org)
- **paytaca-cli** installed globally:
  ```bash
  npm install -g paytaca-cli
  ```
- A Paytaca wallet (create or import):
  ```bash
  paytaca wallet create --chipnet  # for testnet
  # or
  paytaca wallet import
  ```

## Installation

1. Install Node.js 20+
2. Install paytaca-cli globally:
   ```bash
   npm install -g paytaca-cli
   ```
3. Verify installation:
   ```bash
   paytaca --version
   # Should print version info
   ```

## Quick Start

```python
from bch_pay_client import BCHPay

# Use Paytaca backend (auto-detects if paytaca is in PATH)
pay = BCHPay(backend='paytaca', network='testnet')

# Or force it with env var:
# import os; os.environ['BCH_BACKEND'] = 'paytaca'

# Create invoice
invoice = pay.create_invoice(
    amount=0.01,
    description="AI consultation: 1000 tokens"
)

print(f"Pay to: {invoice.address}")
print(f"Check URL: {pay.get_payment_url(invoice.id)}")

# Check payment
if pay.check_payment(invoice.id):
    print("✅ Payment received!")
```

## How It Works

- **Address Generation**: Calls `paytaca receive --no-qr --index N` to derive unique receiving addresses from your HD wallet.
- **Payment Verification**: Calls `paytaca history --json` and scans for incoming transactions to your invoice addresses.
- **Balance Query**: Calls `paytaca balance` and parses the BCH amount.
- **Sending**: Uses `paytaca send` (BCH) or `paytaca token send` (CashTokens).

### Address Index Management

Each invoice gets a unique address index (0, 1, 2, ...). This allows you to monitor many addresses without reusing them, improving privacy.

The invoice metadata stores the `address_index` used for later lookup in history.

## Limitations & Caveats

- **Subprocess overhead**: Each operation spawns a Node.js process. Latency ~100-300ms.
- **JSON output assumption**: This backend expects `paytaca history --json` to output parseable JSON. The Paytaca CLI may need `--json` flag support (check your version).
- **No real-time notifications**: Unlike Watchtower webhooks, you must poll `check_payment()` periodically.
- **Token support**: Basic token sending works, but token balance/history may be limited.
- **Error handling**: Network failures or CLI crashes raise exceptions. Wrap calls in try/except.

## Environment Variables

| Variable | Effect |
|----------|--------|
| `BCH_BACKEND=paytaca` | Forces Paytaca backend even if not auto-detected |
| `PAYTACA_CLI=/custom/path/paytaca` | Override path to paytaca executable |
| `BCH_NETWORK=chipnet` | Alias for `network='testnet'` |

## Production Recommendations

For production, consider:

1. **Watchtower Direct API** (coming soon): Use HTTP API directly without CLI overhead.
2. **Self-hosted Watchtower**: Run your own Watchtower.cash instance for full control.
3. **BCH Node RPC**: Use `bch_node_url` with a custom backend for maximum reliability.

## Troubleshooting

### `RuntimeError: Paytaca CLI not found`
- Ensure Node.js 20+ is installed: `node --version`
- Install paytaca-cli globally: `npm install -g paytaca-cli`
- Ensure the executable is in your PATH: `which paytaca`

### `Failed to get address` / `Could not parse address`
- The Paytaca CLI output format may have changed.
- Check your version: `paytaca --version`
- Update: `npm update -g paytaca-cli`
- The expected output line is: `Address: <bitcoincash:...>`

### `history --json` returns non-JSON
- Paytaca CLI may not support `--json` flag yet.
- As a workaround, you may need to parse human-readable output (not recommended).
- Consider filing an issue with Paytaca to add proper JSON output mode.

### Payments not detected
- Ensure you're on the same network (`chipnet` vs `mainnet`).
- Verify the wallet has received the payment manually: `paytaca history`.
- Check that the address index used hasn't been reused elsewhere.

## Security Notes

- The Paytaca wallet seed is stored in your OS keychain (macOS Keychain, GNOME Keyring, KWallet, or Windows Credential Manager). Never log or expose this.
- `bch-pay-client` never sees your seed; it only invokes `paytaca` CLI.
- Use a dedicated wallet for your AI agent, not your personal wallet.
- On production servers, restrict filesystem permissions and environment variables.

## Future Work

- Implement `WatchtowerBackend` using `watchtower-cash-py` for direct HTTP API (no Node.js required).
- Add real-time WebSocket listener for instant payment notifications.
- Support multi-wallet (different Paytaca wallet profiles).
