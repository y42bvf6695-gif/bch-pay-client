# Send Mainnet Guide

`examples/send_mainnet.py` es un script seguro para enviar Bitcoin Cash (BCH) en mainnet usando Paytaca backend.

## Prerrequisitos

1. **Node.js 20+** instalado: https://nodejs.org
2. **paytaca-cli** instalado globalmente:
   ```bash
   npm install -g paytaca-cli
   ```
3. **Wallet Paytaca creada** en mainnet:
   ```bash
   paytaca wallet create
   # (elige "mainnet" cuando pregunte)
   ```
   **Guarda tu seedphrase en un lugar seguro y privado.**
4. **Fondos en la wallet**:
   - Comprueba tu balance: `paytaca balance`
   - Si está vacío, necesitas obtener BCH de un exchange o faucet (mainnet)

## Uso

```bash
# Enviar 0.00242019 BCH a una dirección
python examples/send_mainnet.py --amount 0.00242019 --address bitcoincash:qz8983kqe0pwccwg3urj462mlzrm02q4vc3z22j9w4

# Modo simulación (no envía, solo verifica configuración)
python examples/send_mainnet.py --amount 0.00242019 --address bitcoincash:qz... --dry-run

# Modo verbose (detalles extra)
python examples/send_mainnet.py --amount 0.00242019 --address bitcoincash:qz... --verbose
```

## Flujo de seguridad

1. **Validación**: Verifica que la dirección sea válida (prefijo `bitcoincash:`)
2. **Confirmación interactiva**: Pide escribir `SI` explícitamente
3. **Ejecución**: Llama a `BCHPay.send_payment()` con Paytaca backend
4. **Resultado**: Muestra TXID y enlace al explorer

## Ejemplo de output exitoso

```
============================================================
ENVÍO BCH EN MAINNET
============================================================
destinatario: bitcoincash:qz8983kqe0pwccwg3urj462mlzrm02q4vc3z22j9w4
monto:        0.00242019 BCH
dry-run:      False
============================================================
¿CONFIRMAS este envío? (escribe 'SI' para continuar): SI
🔄 Inicializando BCHPay(backend='paytaca', network='mainnet')...
🔄 Ejecutando send_payment()...
✅ ¡ENVÍO EXITOSO!
   TXID: 1234567890abcdef...
   Puedes ver la transacción en: https://explorer.bitcoin.com/bch/tx/1234567890abcdef...
============================================================
```

## Consideraciones importantes

### Monto y fees
- El monto se envía **exactamente** como especificas
- Paytaca calcula y paga automáticamente la fee de red (~$0.01-0.05)
- Asegúrate de tener balance suficiente: `balance >= amount + fee`

### Direcciones
- **Mainnet**: direcciones empiezan con `bitcoincash:` o `q` (compressed)
- **Testnet**: empiezan con `bchtest:` o `bchtest:z` (token-aware)
- Envía solo a direcciones compatibles con BCH (no Bitcoin BTC)

### Irreversibilidad
- Las transacciones BCH **no se pueden revertir**
- Verifica la dirección 2 veces antes de confirmar
- No envíes a direcciones desconocidas o no verificadas

### Troubleshooting

#### `Paytaca CLI not found`
```bash
npm install -g paytaca-cli
# Verifica: paytaca --version
```

#### `Wallet not created` o `No funds`
```bash
paytaca wallet create  # crea wallet en mainnet
paytaca balance        # verifica balance
```

Si no tienes BCH en mainnet:
- Compra en exchange (Coinbase, Kraken, etc.) y retira a tu dirección Paytaca
- O usa un servicio de custodia

#### `Invalid address`
La dirección debe ser CashAddress (Bitcoin Cash). No uses direcciones Legacy (`1...`) o Bech32 (`bc1...`).

#### `Transaction failed` o `insufficient balance`
- Balance insuficiente (recuerda incluir fee)
- Paytaca CLI issues (reinicia: `paytaca wallet unlock`)

## Seguridad

**NUNCA**:
- Compartas tu seedphrase por email/chat
- Guardes semillas en código fuente o repositorios públicos
- Uses este script en máquinas compartidas sin desbloquear wallet

**RECOMENDACIONES**:
- Usa una wallet dedicada solo para testing/automation
- Mantén small balances en wallets de agentes
- Considera hardware wallet para grandes cantidades

## Integración con QA Agent

El `agent_venture_qa.py` incluye pruebas de `send_payment` en modo demo (simulado). Para probar en mainnet:

```bash
# Primero, asegúrate de tener Paytaca configurado y fondos
python examples/send_mainnet.py --amount 0.0001 --address bitcoincash:your_test_address_here --dry-run

# Si todo OK, quita --dry-run y confirma
python examples/send_mainnet.py --amount 0.0001 --address bitcoincash:your_test_address_here
```

---

¿Preguntas? Abre un issue o consulta la [documentación de Paytaca](paytaca.md).
