"""Tests básicos para bch_pay_client."""

import pytest
import tempfile
import os
from pathlib import Path

from bch_pay_client import BCHPay, Invoice, BCHPayError


@pytest.fixture
def temp_storage():
    """Crea storage temporal para tests."""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    yield path
    os.unlink(path)


def test_create_invoice(temp_storage):
    pay = BCHPay(storage_path=temp_storage, network="testnet")
    invoice = pay.create_invoice(amount=0.01, description="Test invoice")

    assert invoice.amount == 0.01
    assert invoice.description == "Test invoice"
    assert invoice.address.startswith(("bitcoincash:", "bchtest:"))
    assert invoice.id is not None
    assert invoice.paid is False


def test_invalid_amount(temp_storage):
    pay = BCHPay(storage_path=temp_storage)
    with pytest.raises(BCHPayError):
        pay.create_invoice(amount=0, description="Invalid")


def test_get_invoice(temp_storage):
    pay = BCHPay(storage_path=temp_storage)
    invoice = pay.create_invoice(amount=0.05, description="Test")

    retrieved = pay.get_invoice(invoice.id)
    assert retrieved is not None
    assert retrieved.id == invoice.id
    assert retrieved.amount == 0.05


def test_list_invoices(temp_storage):
    pay = BCHPay(storage_path=temp_storage)

    # Crear varias facturas
    for i in range(5):
        pay.create_invoice(amount=i * 0.01, description=f"Invoice {i}")

    invoices = pay.list_invoices(limit=3)
    assert len(invoices) <= 3
    # Deben estar ordenadas por fecha descendente
    times = [inv.created_at for inv in invoices]
    assert times == sorted(times, reverse=True)


def test_total_earned(temp_storage):
    pay = BCHPay(storage_path=temp_storage)

    inv1 = pay.create_invoice(amount=0.1, description="A")
    inv2 = pay.create_invoice(amount=0.2, description="B")

    # En modo demo, after 5s se marcan como pagadas automáticamente
    import time
    time.sleep(6)

    assert pay.check_payment(inv1.id)
    assert pay.check_payment(inv2.id)

    total = pay.total_earned()
    assert total == pytest.approx(0.3)


def test_metadata(temp_storage):
    pay = BCHPay(storage_path=temp_storage)
    metadata = {"user_id": "123", "order": "xyz"}
    invoice = pay.create_invoice(
        amount=0.01,
        description="With metadata",
        metadata=metadata
    )

    retrieved = pay.get_invoice(invoice.id)
    assert retrieved.metadata == metadata


def test_generate_qr(temp_storage):
    pay = BCHPay(storage_path=temp_storage)

    try:
        import qrcode  # noqa
        invoice = pay.create_invoice(amount=0.01, description="QR test")
        qr_bytes = pay.generate_qr(invoice.id, size=200)
        assert isinstance(qr_bytes, bytes)
        assert len(qr_bytes) > 0
    except ImportError:
        with pytest.raises(BCHPayError):
            pay.generate_qr("dummy-id")


def test_multiple_storages():
    """Verifica que diferentes storage paths son independientes."""
    fd1, path1 = tempfile.mkstemp(suffix=".json")
    fd2, path2 = tempfile.mkstemp(suffix=".json")
    os.close(fd1); os.close(fd2)

    try:
        pay1 = BCHPay(storage_path=path1)
        pay2 = BCHPay(storage_path=path2)

        inv1 = pay1.create_invoice(0.01, "Pay1")
        inv2 = pay2.create_invoice(0.02, "Pay2")

        # Cada storage debe tener solo su factura
        assert len(pay1.list_invoices()) == 1
        assert len(pay2.list_invoices()) == 1

        assert pay1.get_invoice(inv1.id) is not None
        assert pay2.get_invoice(inv2.id) is not None
        assert pay1.get_invoice(inv2.id) is None
        assert pay2.get_invoice(inv1.id) is None
    finally:
        os.unlink(path1)
        os.unlink(path2)


if __name__ == "__main__":
    pytest.main(["-v", __file__])