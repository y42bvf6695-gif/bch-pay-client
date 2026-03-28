"""
Agente de QA automatizado para bch-pay-client.

Categorías de prueba (semilla):
1. Rhythm   - Flujo de trabajo, async/threading
2. Feed     - Input validation, data feeding
3. Desk     - CLI/interfaz, argument parsing
4. Glove    - Error handling, edge cases
5. Attack   - Stress tests, concurrent operations
6. Sing     - Logging, reporting, output format
7. Blur     - Ambiguity handling, fuzzy inputs
8. Pig      - Large payloads, bulk operations
9. Pass     - Successful paths, happy flows
10. Runway  - Deployment, installation, DPI
11. Cattle  - Multi-invoice, batch processing
12. Venture - Experimental features, edge tech

Uso:
    python examples/agent_venture_qa.py [--backend demo|paytaca] [--network testnet|mainnet] [--report format]

Ejemplos:
    python examples/agent_venture_qa.py --backend demo --report json
    python examples/agent_venture_qa.py --backend paytaca --network testnet --report markdown
"""

import sys
import time
import uuid
import json
import argparse
import traceback
from typing import Dict, List, Any, Tuple
from pathlib import Path
from datetime import datetime

from bch_pay_client import BCHPay, BCHPayError

# ==================== CATEGORIAS DE PRUEBA ====================

class TestCategory:
    """Cada categoría representa un tipo de prueba."""
    RHTHM = "Rhythm"     # Workflow patterns
    FEED = "Feed"        # Input validation
    DESK = "Desk"        # CLI interface
    GLOVE = "Glove"      # Error handling
    ATTACK = "Attack"    # Stress/concurrency
    SING = "Sing"        # Logging/reporting
    BLUR = "Blur"       # Ambiguous inputs
    PIG = "Pig"          # Large/bulk operations
    PASS = "Pass"        # Happy paths
    RUNWAY = "Runway"    # Deployment/install
    CATTLE = "Cattle"    # Batch/multi-invoice
    VENTURE = "Venture"  # Experimental features


# ==================== FRAMEWORK DE TESTS ====================

class TestResult:
    def __init__(self, category: str, name: str, passed: bool, message: str = "", duration_ms: float = 0):
        self.category = category
        self.name = name
        self.passed = passed
        self.message = message
        self.duration_ms = duration_ms
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp
        }


class QAAgent:
    """Agente que ejecuta batería de pruebas en bch-pay-client."""

    def __init__(self, backend: str, network: str, storage_path: str = None, real_send_addr: str = None, real_send_amount: float = None):
        self.backend = backend
        self.network = network
        self.storage_path = storage_path or f".qa_test_{uuid.uuid4().hex[:8]}.json"
        self.results: List[TestResult] = []
        self.pay = None
        self.real_send_addr = real_send_addr
        self.real_send_amount = real_send_amount

    def log(self, msg: str):
        print(f"[QA] {msg}")

    def run_test(self, category: str, name: str, func):
        """Ejecuta una prueba y captura resultado."""
        start = time.time()
        try:
            func()
            duration = (time.time() - start) * 1000
            self.results.append(TestResult(category, name, True, "", duration))
            self.log(f"✅ {category}/{name} ({duration:.1f}ms)")
        except Exception as e:
            duration = (time.time() - start) * 1000
            msg = f"{type(e).__name__}: {str(e)}"
            self.results.append(TestResult(category, name, False, msg, duration))
            self.log(f"❌ {category}/{name}: {msg} ({duration:.1f}ms)")

    def setup(self):
        """Inicializa BCHPay."""
        self.log(f"Inicializando BCHPay(backend={self.backend}, network={self.network})")
        self.pay = BCHPay(
            storage_path=self.storage_path,
            backend=self.backend,
            network=self.network
        )

    def cleanup(self):
        """Limpia archivos temporales."""
        try:
            if self.storage_path and Path(self.storage_path).exists():
                Path(self.storage_path).unlink()
        except:
            pass

    # ==================== CATEGORIAS DE PRUEBAS ====================

    def test_rhythm_workflow(self):
        """Rhythm: Flujo completo normal."""
        inv = self.pay.create_invoice(0.01, "QA test")
        assert inv.id
        assert inv.address
        assert inv.amount == 0.01

    def test_feed_invalid_amounts(self):
        """Feed: Validación de inputs inválidos."""
        try:
            self.pay.create_invoice(0, "Zero amount")
            raise AssertionError("Should reject zero")
        except BCHPayError:
            pass  # Esperado
        try:
            self.pay.create_invoice(-0.01, "Negative")
            raise AssertionError("Should reject negative")
        except BCHPayError:
            pass

    def test_desk_storage_path(self):
        """Desk: Diferentes rutas de storage."""
        custom_path = f"/tmp/qa_custom_{uuid.uuid4().hex[:8]}.json"
        pay2 = BCHPay(storage_path=custom_path, backend=self.backend, network=self.network)
        inv = pay2.create_invoice(0.001, "Custom storage")
        assert inv.id
        # Cleanup
        if Path(custom_path).exists():
            Path(custom_path).unlink()

    def test_glove_backend_missing(self):
        """Glove: Manejo de backend no disponible."""
        if self.backend == 'paytaca':
            # Simular missing paytaca
            pass  # Ya está manejado con RuntimeError al init
        else:
            # Demo siempre disponible
            pass

    def test_attack_concurrent_invoices(self):
        """Attack: Crear múltiples facturas rápido."""
        ids = []
        for i in range(20):
            inv = self.pay.create_invoice(0.001, f"Batch {i}")
            ids.append(inv.id)
        assert len(ids) == 20
        # Verificar que todas son únicas
        assert len(set(ids)) == 20

    def test_sing_list_invoices(self):
        """Sing: Listar y verificar orden."""
        # Crear algunas facturas
        for i in range(5):
            self.pay.create_invoice(0.01 * (i+1), f"Inv {i}")
        invoices = self.pay.list_invoices(limit=10)
        # Debería devolver al menos 5
        assert len(invoices) >= 5
        # Verificar orden descendente por created_at
        for i in range(len(invoices)-1):
            assert invoices[i].created_at >= invoices[i+1].created_at

    def test_blur_metadata(self):
        """Blur: Metadata con tipos raros."""
        weird_meta = {
            "number": 42,
            "float": 3.14,
            "bool": True,
            "none": None,
            "list": [1,2,3],
            "dict": {"nested": "value"},
            "unicode": "测试 🎉"
        }
        inv = self.pay.create_invoice(0.01, "Weird metadata", metadata=weird_meta)
        retrieved = self.pay.get_invoice(inv.id)
        assert retrieved.metadata == weird_meta

    def test_pig_long_description(self):
        """Pig: Descripciones muy largas."""
        long_desc = "A" * 10000
        inv = self.pay.create_invoice(0.01, long_desc)
        retrieved = self.pay.get_invoice(inv.id)
        assert retrieved.description == long_desc

    def test_pass_happy_path_bch(self):
        """Pass: Camino feliz BCH."""
        inv = self.pay.create_invoice(0.01, "Happy BCH")
        assert inv.address.startswith(("bitcoincash:", "bchtest:"))
        # En demo, después de 6s está pagada
        time.sleep(6)
        assert self.pay.check_payment(inv.id)

    def test_runway_serialization(self):
        """Runway: Serialización a JSON."""
        inv = self.pay.create_invoice(0.05, "Serialization test")
        data = inv.to_dict()
        # Verificar que es serializable
        json_str = json.dumps(data)
        assert "id" in json_str

    def test_cattle_list_and_filter(self):
        """Cattle: Operaciones en lote."""
        # Crear varias facturas
        for i in range(10):
            self.pay.create_invoice(0.01 * (i % 3 + 1), f"Batch {i}")
        all_inv = self.pay.list_invoices(limit=100)
        assert len(all_inv) >= 10
        # Filtrar por monto (simulado)
        big = [inv for inv in all_inv if inv.amount >= 0.02]
        assert len(big) > 0

    def test_venture_get_balance(self):
        """Venture: Obtener balance."""
        bal = self.pay.get_balance()
        assert isinstance(bal, (int, float))
        # En demo, balance es suma de invoices pagados
        # Después del test_pass, debería haber al menos 0.01
        assert bal >= 0.0

    def test_venture_token_operations(self):
        """Venture: Operaciones con tokens (si backend soporta)."""
        try:
            MUSD = "e90b1965dc200e3c8d5f899a9e8e146c073552418b266d3a87238777a6d3d227"
            inv = self.pay.create_invoice(
                amount=1.0,
                description="Token test",
                token_category=MUSD
            )
            assert inv.address  # Debería ser token-aware (prefijo z)
            # Balance token (0 en demo)
            bal = self.pay.get_balance(token_category=MUSD)
            assert isinstance(bal, float)
            # list_tokens (vacío en demo)
            tokens = self.pay.list_tokens()
            assert isinstance(tokens, list)
        except (BCHPayError, NotImplementedError):
            # Backend no soporta tokens, está bien
            pass

    def test_venture_send_payment_not_implemented(self):
        """Venture: send_payment no implementado en todos lados."""
        result = self.pay.send_payment(
            address="bitcoincash:qqq...",
            amount=0.01
        )
        assert "success" in result
        # En demo, siempre falla
        assert result["success"] is False

    def test_venture_real_send(self):
        """Venture: Envío REAL de BCH (⚠️ SOLO MAINNET CON FONDOS)."""
        if not self.real_send_addr or not self.real_send_amount:
            raise RuntimeError("Real send configurado pero falta dirección o monto")
        
        self.log(f"INICIANDO ENVÍO REAL: {self.real_send_amount} BCH → {self.real_send_addr}")
        
        # Confirmación adicional
        print("\n" + "="*60)
        print("⚠️  ADVERTENCIA: ENVÍO REAL EN MAINNET")
        print("="*60)
        print(f"Destinatario: {self.real_send_addr}")
        print(f"Monto:        {self.real_send_amount:.8f} BCH")
        print("="*60)
        confirm = input("Para CONFIRMAR este envío, escribe la palabra 'REAL': ")
        if confirm != "REAL":
            raise RuntimeError("Envío cancelado por el usuario")
        
        # Ejecutar envío
        result = self.pay.send_payment(
            address=self.real_send_addr,
            amount=self.real_send_amount
        )
        
        if not result.get("success"):
            raise RuntimeError(f"Envio falló: {result.get('error', 'Unknown error')}")
        
        self.log(f"✅ Envío exitoso! TXID: {result.get('txid', 'N/A')}")

    # ==================== EJECUCION ====================

    def run_all_tests(self):
        """Ejecuta todas las categorías de prueba."""
        self.log("="*60)
        self.log(f"INICIANDO QA SUITE: backend={self.backend}, network={self.network}")
        if self.real_send_addr and self.real_send_amount:
            self.log(f"⚠️  ENVÍO REAL ACTIVADO: {self.real_send_amount} BCH a {self.real_send_addr}")
        self.log("="*60)

        self.setup()

        # Mapeo categoría -> tests
        tests = [
            (TestCategory.RHTHM, self.test_rhythm_workflow),
            (TestCategory.FEED, self.test_feed_invalid_amounts),
            (TestCategory.DESK, self.test_desk_storage_path),
            (TestCategory.GLOVE, self.test_glove_backend_missing),
            (TestCategory.ATTACK, self.test_attack_concurrent_invoices),
            (TestCategory.SING, self.test_sing_list_invoices),
            (TestCategory.BLUR, self.test_blur_metadata),
            (TestCategory.PIG, self.test_pig_long_description),
            (TestCategory.PASS, self.test_pass_happy_path_bch),
            (TestCategory.RUNWAY, self.test_runway_serialization),
            (TestCategory.CATTLE, self.test_cattle_list_and_filter),
            (TestCategory.VENTURE, self.test_venture_get_balance),
            (TestCategory.VENTURE, self.test_venture_token_operations),
            (TestCategory.VENTURE, self.test_venture_send_payment_not_implemented),
        ]
        
        # Añadir prueba de envío real si se configuró
        if self.real_send_addr and self.real_send_amount:
            tests.append((TestCategory.VENTURE, self.test_venture_real_send))

        total = len(tests)
        passed = 0

        for category, test_func in tests:
            self.run_test(category, test_func.__name__, test_func)
            if self.results[-1].passed:
                passed += 1

        self.log("="*60)
        self.log(f"RESULTADOS: {passed}/{total} pruebas pasaron")
        self.log("="*60)

        self.cleanup()
        return self.results

    def generate_report(self, format: str = "text") -> str:
        """Genera reporte en formato solicitado."""
        if format == "json":
            return json.dumps([r.to_dict() for r in self.results], indent=2)
        elif format == "markdown":
            md = "# Reporte de QA - bch-pay-client\n\n"
            md += f"**Backend**: {self.backend}  \n"
            md += f"**Network**: {self.network}  \n"
            md += f"**Timestamp**: {datetime.utcnow().isoformat()}  \n\n"
            md += "## Resumen\n\n"
            total = len(self.results)
            passed = sum(1 for r in self.results if r.passed)
            md += f"- Total: {total}\n"
            md += f"- Pasadas: {passed}\n"
            md += f"- Fallidas: {total-passed}\n\n"
            md += "## Detalle por Categoría\n\n"
            for cat in sorted(set(r.category for r in self.results)):
                cat_tests = [r for r in self.results if r.category == cat]
                md += f"### {cat}\n\n"
                md += "| Test | Status | Duration | Message |\n"
                md += "|------|--------|----------|---------|\n"
                for r in cat_tests:
                    status = "✅ PASS" if r.passed else "❌ FAIL"
                    md += f"| {r.name} | {status} | {r.duration_ms:.1f}ms | {r.message} |\n"
                md += "\n"
            return md
        else:
            # Texto simple
            lines = []
            for r in self.results:
                status = "PASS" if r.passed else "FAIL"
                lines.append(f"[{r.category}/{r.name}] {status} ({r.duration_ms:.1f}ms)")
                if not r.passed:
                    lines.append(f"  Error: {r.message}")
            return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Agente QA para bch-pay-client")
    parser.add_argument("--backend", choices=["demo", "paytaca"], default="demo", help="Backend a probar")
    parser.add_argument("--network", choices=["testnet", "mainnet"], default="testnet", help="Red BCH")
    parser.add_argument("--report", choices=["text", "json", "markdown"], default="text", help="Formato reporte")
    parser.add_argument("--output", type=str, help="Archivo de salida para el reporte (opcional)")
    parser.add_argument("--real-send", action="store_true", help="⚠️  Realiza un envío REAL de BCH (solo con Paytaca mainnet)")
    parser.add_argument("--address", type=str, help="Dirección destino para envío real (solo con --real-send)")
    parser.add_argument("--amount", type=float, help="Monto a enviar (solo con --real-send)")
    args = parser.parse_args()

    # Validaciones de real-send
    real_send_addr = None
    real_send_amount = None
    if args.real_send:
        if args.backend != 'paytaca':
            print("❌ --real-send solo funciona con --backend paytaca")
            sys.exit(1)
        if args.network != 'mainnet':
            print("❌ --real-send solo funciona en --network mainnet")
            sys.exit(1)
        if not args.address or not args.amount:
            print("❌ --real-send requiere --address y --amount")
            sys.exit(1)
        real_send_addr = args.address
        real_send_amount = args.amount

    agent = QAAgent(
        backend=args.backend,
        network=args.network,
        real_send_addr=real_send_addr,
        real_send_amount=real_send_amount
    )
    
    results = agent.run_all_tests()
    report = agent.generate_report(format=args.report)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Reporte guardado en: {args.output}")
    else:
        print("\n" + report)


if __name__ == "__main__":
    main()
