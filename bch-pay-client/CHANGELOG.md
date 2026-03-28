# Changelog

All notable changes to bch-pay-client will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Modular backend system** - Pluggable architecture for payment backends
  - `DemoBackend`: simulated payments (auto-approve after 5s)
  - `PaytacaBackend`: integration with Paytaca CLI (experimental)
  - Auto-detection: uses Paytaca if installed, falls back to demo
- Backend selection via `BCHPay(backend='demo'|'paytaca')`
- Backwards compatible: retains `bch_node_url` and `explorer_url` parameters
- Local invoice caching works across all backends
- `bch_pay_client.backends` module with abstract `BCHBackend` interface
- Enhanced documentation: backend selection guide, Paytaca setup

### Changed
- Core refactored to delegate to backend implementations
- Default behavior unchanged for existing users (demo mode)
- Invoice storage remains in `~/.bch_pay.json` (or custom path)

### Docs
- README updated with backend section
- Clarified Paytaca backend experimental status

---

## [0.1.0] - 2026-03-28

### Added
- Core `BCHPay` class with JSON storage
- Demo mode with simulated payment verification (auto-approve)
- QR code generation (optional `qrcode` + `pillow`)
- Webhook support with background processing (FastAPI agent)
- 12 pre-built autonomous agents:
  - REST API (FastAPI)
  - Discord bot (discord.py)
  - Telegram bot (python-telegram-bot)
  - CLI interactive
  - Hybrid (API + bots)
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

[Unreleased]: https://github.com/y42bvf6695-gif/bch-pay-client/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/y42bvf6695-gif/bch-pay-client/releases/tag/v0.1.0
