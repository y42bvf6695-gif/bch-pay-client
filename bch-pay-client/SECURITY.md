# Security Policy

## Supported Versions

| Version | Supported          |
|---------|-------------------|
| 0.1.x   | ✅ Active development |
| < 0.1   | ⚠️ No security fixes |

## Reporting a Vulnerability

**DO NOT** open a public GitHub issue for security vulnerabilities.

Instead, please report to:

- Email: security@bch-ia.org (encrypted with PGP if possible)
- Or create a private security advisory on GitHub: https://github.com/bch-ia/bch-pay-client/security

Include:
- Detailed description
- Steps to reproduce
- Potential impact
- Your PGP key for encrypted communication

## Security Considerations

### Mainnet Deployments

- **Never** use public BCH nodes for mainnet in production. Run your own full node.
- **Always** use HTTPS for APIs and webhooks.
- **Never** commit `.env` files with real tokens or storage containing real funds.
- **Backup** storage files regularly; they contain invoice history and can be used for accounting.
- **Rotate** API keys if exposed.
- **Rate limit** all public endpoints to prevent abuse.

### Demo/Testnet

- Testnet funds have no real value, but still protect your development environment.
- Testnet addresses start with `bchtest:`.

### SmartBCH (if using)

- Same security principles apply.
- Be aware of contract risks if integrating with smart contracts.

### Private Keys

**bch-pay-client does NOT handle private keys.** It generates addresses but cannot spend. For mainnet, you must connect to a wallet that holds private keys (Badger, Electron Cash, etc.) to actually receive payments.

If you implement wallet integration:
- Never log private keys
- Use environment variables or secret managers
- Rotate keys if compromise suspected

---

## Best Practices

1. **Minimal privileges**: Bot tokens should have only necessary permissions
2. **Input validation**: All amounts must be validated (float > 0)
3. **Idempotency**: Design webhooks to process same `invoice_id` multiple times safely
4. **Logging**: Log all payment events with structured JSON
5. **Monitoring**: Alert on:
   - High-value invoices (>1 BCH)
   - Failed payment verifications
   - Storage corruption or full disk
   - Unusual API usage patterns

6. **Updates**: Subscribe to GitHub security advisories for this repo.

---

## Known Issues

None at this time. Report responsibly.

---

**Security is a process, not a feature.** Help us improve!