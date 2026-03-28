# Changelog

All notable changes to bch-pay-client will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of bch-pay-client
- Core BCHPay class with JSON storage
- Demo mode with simulated payment verification
- QR code generation (optional)
- Webhook support with background processing

### Agents
- API REST (FastAPI) - full OpenAPI docs
- Discord bot (discord.py) with interactive buttons
- Telegram bot (python-telegram-bot) with inline keyboards
- CLI interactive
- Hybrid agent (API + Discord + Telegram)
- Fine-tuning as a Service agent
- Dataset Marketplace agent
- GPU Rental agent
- Compute Rental agent
- Image Generation agent
- LLM API with prepaid balance

### Docs
- Quickstart guide (5 min)
- Full API reference
- Integration guides: FastAPI, Discord, Telegram
- Webhooks guide
- Troubleshooting guide
- Contributing guidelines
- Security policy
- Roadmap
- Code of Conduct

### DevOps
- Poetry pyproject.toml
- setup.py alternative
- requirements.txt
- Dockerfile + docker-compose.yml
- GitHub Actions CI (test + build + lint)
- Issue templates (bug report, feature request)
- PR template
- Install guide (systemd, K8s)

### Badges
- 4 contributor badges (SVG)

## [0.1.0] - Planned - 2026-Q2

### Added
- Real BCH node integration (mainnet support)
- Multi-wallet support (Badger, Electron Cash)
- Rate limiting middleware
- Dashboard web UI
- More comprehensive tests
- PyPI publication
- Official Docker images

### Changed
- Storage backend options (SQLite, PostgreSQL)

[Unreleased]: https://github.com/y42bvf6695-gif/bch-pay-client/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/y42bvf6695-gif/bch-pay-client/releases/tag/v0.1.0