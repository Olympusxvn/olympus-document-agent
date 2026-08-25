from extract.gemini import extract_with_one_retry
from extract.plan import InvoicePlan


class SequenceExtractor:
    def __init__(self, plans: list[InvoicePlan]) -> None:
        self.plans = plans
        self.calls = 0

    def extract(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> InvoicePlan:
        del image_bytes, mime_type
        plan = self.plans[min(self.calls, len(self.plans) - 1)]
        self.calls += 1
        return plan


def test_extract_retries_once_when_schema_empty():
    extractor = SequenceExtractor(
        [
            InvoicePlan(),
            InvoicePlan(
                invoice_number="HD-9",
                seller_mst="0101243150",
                subtotal=10,
                vat_amount=1,
                total=11,
                confidence=0.8,
            ),
        ]
    )
    plan = extract_with_one_retry(extractor, b"img")
    assert extractor.calls == 2
    assert plan.invoice_number == "HD-9"


def test_extract_does_not_retry_when_schema_ok():
    extractor = SequenceExtractor(
        [
            InvoicePlan(
                invoice_number="HD-1",
                seller_mst="0101243150",
                confidence=0.9,
            )
        ]
    )
    plan = extract_with_one_retry(extractor, b"img")
    assert extractor.calls == 1
    assert plan.invoice_number == "HD-1"
