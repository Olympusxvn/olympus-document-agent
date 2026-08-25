from extract.plan import InvoicePlan, plan_from_mapping
from gates.evaluate import evaluate_gates


def _plan(**kwargs) -> InvoicePlan:
    base = dict(
        invoice_number="HD-1",
        seller_mst="0101243150",
        subtotal=100000,
        vat_amount=10000,
        total=110000,
        confidence=0.9,
    )
    base.update(kwargs)
    return plan_from_mapping(base)


def test_schema_fail_missing_invoice_number():
    result = evaluate_gates(_plan(invoice_number=""))
    assert result.passed is False
    assert "schema" in result.failures


def test_math_fail():
    result = evaluate_gates(_plan(total=999999))
    assert result.passed is False
    assert "math" in result.failures


def test_math_pass_within_one_dong():
    result = evaluate_gates(_plan(total=110001))
    assert result.passed is True


def test_confidence_fail():
    result = evaluate_gates(_plan(confidence=0.4), confidence_threshold=0.75)
    assert result.passed is False
    assert "confidence" in result.failures


def test_duplicate_invoice_after_posted():
    result = evaluate_gates(
        _plan(),
        posted_identities={("0101243150", "HD-1")},
    )
    assert result.passed is False
    assert "duplicate_invoice" in result.failures


def test_all_gates_pass():
    result = evaluate_gates(_plan())
    assert result.passed is True
    assert result.failures == []
