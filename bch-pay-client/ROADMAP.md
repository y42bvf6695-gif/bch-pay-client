# BCHPay - Roadmap

## v0.1.x (Actual - Alpha)

### ✅ Completado
- [x] Cliente BCHPay base (core.py)
- [x] Almacenamiento local JSON
- [x] Generación de direcciones (modo testnet)
- [x] Verificación de pagos (simulada + hook para nodo real)
- [x] Generación de QR codes
- [x] Agente API REST (FastAPI)
- [x] Agente Discord (discord.py)
- [x] Agente Telegram (python-telegram-bot)
- [x] Agente CLI interactivo
- [x] Agentes de ejemplo: Finetuning, Dataset Marketplace, GPU Rental, Image Gen, LLM API
- [x] Sistema de badges SVG
- [x] pyproject.toml y setup.py alternativo
- [x] QUICKSTART.md

### 🔄 En progreso (v0.1.0)
- [ ] Tests unitarios (pytest) - 20% completado
- [ ] CI/CD (GitHub Actions) - config pendiente
- [ ] Automatización de entrega de badges via GitHub Actions
- [ ] Documentación completa de API (OpenAPI/Swagger)
- [ ] Traducción de docs al español

## v0.2.x (Beta - Q2 2026)

### Objetivos
- [ ] **Integración真实 con nodo BCH** (lib `bchd` o `bitcoinlib`)
- [ ] **Wallet multi-firma** opcional para mayor seguridad
- [ ] **Plugin para LangChain** - `bch-payment` como herramienta nativa
- [ ] **Plugin para OpenWebUI/LocalAI**
- [ ] **Marketplace de agentes**: directorio de agentes BCHPay
- [ ] **Dashboard web**: monitoreo de facturas, ingresos, métricas
- [ ] **Webhooks mejorados**: eventos custom, retry automático
- [ ] **Soporte para Lightning Network BCH** (si se activa)

### Experimentos
- [ ] Agente Autonomous AI (auto-recompra de servicios)
- [ ] DAO de gobernanza para el repo
- [ ] Badge NFT en SmartBCH

## v0.3.x ( Producción - Q3 2026 )

### Objetivos
- [ ] **Mainnet listo**: auditoría de seguridad
- [ ] **Diccionario de precios dinámico** (feed de precios BCH/USD)
- [ ] **Multi-wallet soporte**: Badger, Electron Cash, etc.
- [ ] **Rate limiting avanzado** por usuario/IP
- [ ] **Multi-idioma**: docs EN/ES, errors i18n
- [ ] **CLI en Rust/Go** para alto rendimiento
- [ ] **Docker images oficiales**
- [ ] **Helm chart** para Kubernetes
- [ ] **SDK para otros lenguajes**: JavaScript/TypeScript, Go, Rust

### Integraciones externas
- [ ] HuggingFace Spaces - botón "Pay with BCH"
- [ ] Replicate - plugin de pago
- [ ] Modal - marketplace de GPU + BCH
- [ ] OpenAI Store - payment gateway alternativa

## Post-v0.3 (Futuro)

- **Sistema de reputación**: karma BCH por pagos puntuales
- **Préstamos flash**: préstamos contra未来 ingresos
- **Staking de BCH**: holders stakean BCH para respaldar agentes
- **Cross-chain**: pagos en otras cripto convertidos a BCH
- **Mobile SDK**: iOS/Android para apps nativas

---

## Cómo priorizamos

1. **Usabilidad**: que cualquier desarrollador pueda integrar en <10 min
2. **Seguridad**: no perder fondos de usuarios
3. **Autonomía**: agentes que funcionan sin intervención
4. **Comunidad**: más developers usando BCH = más valor

¿Quieres priorizar algo específico? Abre un issue y etiqueta `enhancement`.