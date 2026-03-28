# QA & Testing Guide

`bch-pay-client` incluye un agente de **QA automatizado** que ejecuta baterías de pruebas completas utilizando la metodología de 12 categorías basadas en la semilla de palabras: Rhythm, Feed, Desk, Glove, Attack, Sing, Blur, Pig, Pass, Runway, Cattle, Venture.

## Uso rápido

```bash
# Ejecutar suite completa con backend demo
python examples/agent_venture_qa.py

# Especificar backend y red
python examples/agent_venture_qa.py --backend paytaca --network testnet

# Generar reporte en JSON
python examples/agent_venture_qa.py --report json --output qa_results.json

# Reporte en Markdown (para GitHub/GitLab)
python examples/agent_venture_qa.py --report markdown --output qa_report.md
```

## Categorías de prueba

| Categoría | Enfoque | Ejemplos |
|-----------|---------|----------|
| **Rhythm** | Flujos de trabajo, secuencias normales | create → check → balance |
| **Feed** | Validación de entradas | amounts <=0, descripciones vacías |
| **Desk** | Interfaz CLI, paths personalizados | storage_path custom |
| **Glove** | Manejo de errores, excepciones | backend no disponible |
| **Attack** | Estrés, concurrencia | 20 invoices rápidas |
| **Sing** | Logging, formato de salida | list_invoices order |
| **Blur** |Entradas ambiguas, metadata rara | unicode, nested dicts |
| **Pig** | Cargas grandes, bulk ops | descripción de 10k chars |
| **Pass** | Caminos felices, éxito asegurado | invoice → 6s → pagada |
| **Runway** | Despliegue, serialización | JSON export |
| **Cattle** | Procesamiento por lotes | list + filter |
| **Venture** | Features experimentales | tokens, send_payment |

## Interpretación de resultados

```
[QA] ====================
[QA] INICIANDO QA SUITE: backend=demo, network=testnet
[QA] ====================
[QA] ✅ Rhythm/test_rhythm_workflow (45.2ms)
[QA] ❌ Feed/test_feed_invalid_amounts: BCHPayError: ... (1.1ms)
...
[QA] ====================
[QA] RESULTADOS: 15/16 pruebas pasaron
[QA] ====================
```

## Reportes

### Texto (default)
Cada línea muestra `[Categoría/NombreTest] STATUS (duration)` con mensaje de error si falla.

### JSON
```json
[
  {
    "category": "Feed",
    "name": "test_feed_invalid_amounts",
    "passed": false,
    "message": "BCHPayError: ...",
    "duration_ms": 1.1,
    "timestamp": "2026-03-28T12:30:00..."
  },
  ...
]
```

### Markdown
Tabla por categoría lista para GitHub/GitLab, útil para documentar詹姆斯.

## Integración en CI/CD

Agrega a tu GitHub Actions:

```yaml
- name: Run QA Suite
  run: |
    python -m pip install -e ".[all]"
    python examples/agent_venture_qa.py --report markdown --output qa_report.md
- name: Upload QA Report
  uses: actions/upload-artifact@v4
  with:
    name: qa-report
    path: qa_report.md
```

## Extending the QA Agent

Puedes agregar tus propias pruebas modificando `examples/agent_venture_qa.py`:

```python
def test_custom_feature(self):
    """Custom: Tu prueba personalizada."""
    pay = self.pay
    # ... tu lógica ...
    assert some_condition
```

Luego registra en `run_all_tests()`:

```python
tests.append(("Custom", self.test_custom_feature))
```

## Notas técnicas

- El QA Agent usa `BCHPay` normal, por lo que prueba el stack completo (backend + storage)
- Cada prueba es independiente y se ejecuta secuencialmente
- El storage es temporal (`/tmp/qa_test_*.json`) y se limpia automáticamente
- Para probar Paytaca backend real, asegúrate de tener `paytaca` instalado y wallet configurada
- Las pruebas de tokens requieren que el backend soporte `token_category` (Paytaca)

## Limitaciones

- **Demo backend**: las pruebas de token devuelven 0 (esperado)
- **Paytaca backend**: puede fallar si no hay nodos disponibles o CLI no instalado
- **Concurrencia**: las pruebas son secuenciales (no se prueba race conditions reales)

## Troubleshooting

### `RuntimeError: Paytaca CLI not found`
Instala paytaca-cli: `npm install -g paytaca-cli`

### Tests lentos
El test `Attack` crea 20 invoices. Considera reducirlo a 5 si solo quieres sanity check.

### No todas las pruebas aplican a todos backends
El QA Agent maneja excepciones. Si un backend no implementa `list_tokens`, la prueba `Venture` la marcará como PASS (skip) via try/except.

## Métricas objetivo

- **Meta**: 100% de pruebas pasando en todos los backends
- **Mínimo aceptable**: 80% en demo, 70% en paytaca (debido a dependencias externas)
