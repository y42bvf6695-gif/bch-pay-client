# Changelog

All notable changes to bch-pay-client will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Full CashToken support (MUSD, SLP tokens)
  - `BCHPay.create_invoice(token_category=...)` for token invoices
  - `BCHPay.get_balance(token_category=...)` for token balances
  - `BCHPay.list_tokens()` to enumerate wallet tokens
  - `BCHPay.send_payment(token_category=...)` for token transfers
  - `PaytacaBackend` token operations: `list_tokens()`, token-aware receive
- New example: `examples/agent_token_demo.py` (BCH + MUSD demo)
- New documentation: `docs/tokens.md` - complete CashToken guide
- PaytacaBackend: token_history with `--token` flag support
- Enhanced invoice storage: `token_category` field for token invoices

### Changed
- `BCHPay.get_balance()` now accepts optional `token_category` parameter
- Backend interface updated for token support (all backends)
- DemoBackend supports token_category argument (no-op, but compatible)

### Docs
- README: added Stablecoin (MUSD) agent row in agents table
- README: added CashToken Support link in documentation section
- README: updated agents table linking to token demo
- README: added token support note in agents description
- CHANGELOG reorganized with separate entries for 0.2.0 and 0.2.1

---

## [0.2.1-alpha] - Upcoming

### Added
- Modular backend infrastructure
- Paytaca CLI backend (experimental)
- Backend auto-detection
- Support for CashTokens (fungible tokens)
- Token operations: create_invoice with token_category, get_balance(token_category), list_tokens, send_payment with token_category
- New demo agent: agent_token_demo.py
- Comprehensive token documentation (docs/tokens.md)

---

## [0.2.0-alpha] - 2026-03-28

### Added
- Modular backend system (DemoBackend, PaytacaBackend)
- Auto-detect Paytaca CLI if installed
- Backend abstraction layer in `bch_pay_client.backends`
- `BCHPay(backend='demo'|'paytaca')` configuration
- Backwards compatibility with `bch_node_url`, `explorer_url`
- Local invoice caching across backends

### Docs
- Paytaca integration guide (docs/paytaca.md)
- README backend selection section

---

## [0.1.0] - 2026-03-28

### Added
- Core `BCHPay` class with JSON storage
- Demo mode with simulated payment verification (auto-approve after 5s)
- QR code generation (optional `qrcode` + `pillow`)
- Webhook support with background processing (FastAPI agent)
- 12 pre-built autonomous agents:
  - REST API (FastAPI)
  - Discord bot (discord.py)
  - Telegram bot (python-telegram-bot)
  - CLI interactive
  - Hybrid (API + Discord + Telegram)
  - Fine-tuning as a Service
  - Dataset Marketplace
  - GPU Rental
  - Compute Rental
  - Image Generation
  - LLM API (OpenAI-compatible)
- Quickstart guide (5 min integration)
- Full API reference
- Integration guides: FastAPI, Discord, Telegram, Webhooks
- Troubleshooting guide
- Contributing guidelines, Security policy, Roadmap, Code of Conduct
- DevOps: Poetry, setup.py, Docker, GitHub Actions CI, issue/PR templates
- Badges: Pionero BCH-IA badge (SVG)
- PyPI publication: `bch-pay-client` (v0.1.0-alpha)
- Auto-deploy GitHub Actions workflow on tag push

### Future (Roadmap)
- Real BCH node integration
- Watchtower backend (direct API)
- Multi-wallet support
- Rate limiting
- Dashboard web UI
- Official Docker images

[Unreleased]: https://github.com/y42bvf6695-gif/bch-pay-client/compare/v0.2.1-alpha...HEAD
[0.2.1-alpha]: https://github.com/y42bvf6695-gif/bch-pay-client/compare/v0.2.0-alpha...HEAD
[0.2.0-alpha]: https://github.com/y42bvf6695-gif/bch-pay-client/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/y42bvf6695-gif/bch-pay-client/releases/tag/v0.1.0
