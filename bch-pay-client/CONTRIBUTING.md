# Contribuir a BCHPay

¡Gracias por tu interés! Este proyecto busca impulsar la economía de agentes autónomos con Bitcoin Cash.

## 🛠️ Cómo contribuir

### Bug reports y feature requests

1. Busca issues existentes antes de crear uno nuevo
2. Usa las plantillas de issue cuando estén disponibles
3. Incluye: descripción clara, pasos para reproducir, entorno (OS, Python version)

### Pull Requests

1. **Fork** el repo
2. **Clona** tu fork
3. **Crea una branch**: `git checkout -b feature/nueva-funcionalidad`
4. **Commit** tus cambios: `git commit -m "Add: nueva funcionalidad"`
5. **Push**: `git push origin feature/nueva-funcionalidad`
6. **Abre un Pull Request** describiendo:
   - Qué hace el cambio
   - Por qué es necesario
   - Cómo probarlo

### Convenciones de código

- Usa type hints donde sea posible
- Documenta funciones/clases con docstrings (formato Google)
- Sigue PEP 8
- Tests para código nuevo (mínimo)

### Estructura del proyecto

```
bch-pay-client/
├── bch_pay_client/     # Librería principal
│   ├── __init__.py
│   ├── core.py         # Cliente BCHPay
│   └── exceptions.py   # Excepciones personalizadas
├── examples/           # Agentes de ejemplo (Ejecutables)
│   ├── agent_api.py
│   ├── agent_discord.py
│   ├── agent_telegram.py
│   ├── agent_cli.py
│   ├── agent_hybrid.py
│   ├── agent_finetune.py
│   ├── agent_dataset_marketplace.py
│   ├── agent_gpu_rental.py
│   ├── agent_compute_rental.py
│   ├── agent_image_gen.py
│   └── agent_llm_api.py
├── docs/               # Documentación
├── tests/              # Tests unitarios
├── README.md
├── QUICKSTART.md
├── pyproject.toml      # Poetry
└── setup.py            # Pip alternativo
```

### Agregar un nuevo agente de ejemplo

1. Crea el archivo en `examples/agent_nuevo.py`
2. Sigue el patrón: imports, inicialización BCHPay, funciones principales, `if __name__ == "__main__":`
3. Documenta el uso con comentarios y docstrings
4. Añade a la [lista en README.md](README.md#agentes-preexistentes)
5. Opcional: crear badge para el agente en `badges/`

### Badges de contribución

Los contributors ganan badges automáticas:

| Badge | Cómo obtener |
|-------|--------------|
| **Pionero BCH‑IA** | Primer PR mergeado |
| **Integrador BCH** | Publica agente usando `bch-pay-client` |
| **Escritor Técnico** | 5+ PRs en docs/ o PRs que mejoren significativamente README/QUICKSTART |
| **Community Hero** | Ayuda activa en issues, Discord, redes sociales |

Badges están en `/badges/` como SVG. ¡Úsalas en tu README!

### Entorno de desarrollo

```bash
# Clonar y entorno virtual
git clone https://github.com/y42bvf6695-gif/bch-pay-client.git
cd bch-pay-client
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -e ".[all]"  # o [web], [telegram], [discord]

# Ejecutar tests (pendientes de crear)
pytest tests/
```

### Pautas de diseño

- **Simplicidad**: 5 líneas de código para integración
- **Sinvendor lock-in**: abstracciones claras para cambiar wallet/nodo
- **Modo demo**: debe funcionar sin wallet real (simulación)
- **Agentes autónomos**: ejemplos deben poder ejecutarse independientes
- **Documentación bilingual**: inglés y español

### Normas de comunidad

- Sé respetuoso y constructivo
- No spam ni autopromoción excesiva
- Ayuda a newcomers
- Las decisiones técnicas se discuten en issues/PRs

### Roadmap

Mira [ROADMAP.md](ROADMAP.md) para ver lo que viene.

---

¿Necesitas ayuda? Abre un issue con la etiqueta `question`.

**¡Vamos a construir la economía de agentes BCH! 💪**