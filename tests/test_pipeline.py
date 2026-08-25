from extract.plan import InvoicePlan
from pipeline.process import apply_plan, attachment_mime, process_received_runs
from store.models import RunRecord, RunStatus
from store.runs import MemoryRunStore


class FakeExtractor:
    def __init__(self, plan: InvoicePlan) -> None:
        self.plan = plan
        self.calls = 0

    def extract(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> InvoicePlan:
        del image_bytes, mime_type
        self.calls += 1
        return self.plan


class FakeAttachmentGmail:
    def __init__(self, blob: bytes) -> None:
        self.blob = blob
        self.downloads: list[tuple[str, str]] = []

    def download_attachment(self, gmail_id: str, attachment_id: str) -> bytes:
        self.downloads.append((gmail_id, attachment_id))
        return self.blob


def _valid_plan(**kwargs) -> InvoicePlan:
    base = dict(
        invoice_number="HD-1",
        seller_mst="0101243150",
        subtotal=100,
        vat_amount=10,
        total=110,
        confidence=0.9,
    )
    base.update(kwargs)
    return InvoicePlan.model_validate(base)


def test_apply_plan_validated_when_gates_pass():
    store = MemoryRunStore()
    rec = RunRecord(message_id="<a@b>")
    store.create_received(rec)
    out = apply_plan(store, rec, _valid_plan())
    assert out.status == RunStatus.validated
    assert out.gate_failures == []


def test_apply_plan_needs_review_on_math():
    store = MemoryRunStore()
    rec = RunRecord(message_id="<c@d>")
    store.create_received(rec)
    out = apply_plan(store, rec, _valid_plan(total=1))
    assert out.status == RunStatus.needs_review
    assert "math" in out.gate_failures


def test_apply_plan_skipped_duplicate_invoice():
    store = MemoryRunStore()
    first = RunRecord(
        message_id="<old@x>",
        status=RunStatus.posted,
        seller_mst="0101243150",
        invoice_number="HD-1",
    )
    store.save(first)
    rec = RunRecord(message_id="<new@x>")
    store.create_received(rec)
    out = apply_plan(store, rec, _valid_plan())
    assert out.status == RunStatus.skipped_duplicate


def test_apply_plan_skipped_duplicate_after_validated():
    store = MemoryRunStore()
    first = RunRecord(
        message_id="<old-v@x>",
        status=RunStatus.validated,
        seller_mst="0101243150",
        invoice_number="HD-1",
    )
    store.save(first)
    rec = RunRecord(message_id="<new-v@x>")
    store.create_received(rec)
    out = apply_plan(store, rec, _valid_plan())
    assert out.status == RunStatus.skipped_duplicate


def test_process_received_runs_extracts_and_validates():
    store = MemoryRunStore()
    rec = RunRecord(
        message_id="<img@x>",
        gmail_id="g1",
        attachment_ids=["att1"],
    )
    created = store.create_received(rec)
    gmail = FakeAttachmentGmail(b"%PDF-1.4 fake")
    extractor = FakeExtractor(_valid_plan())
    out = process_received_runs([created], gmail, store, extractor)
    assert len(out) == 1
    assert out[0].status == RunStatus.validated
    assert extractor.calls >= 1
    assert gmail.downloads == [("g1", "att1")]
    assert attachment_mime(b"%PDF-1.4") == "application/pdf"


def test_process_received_extract_error_needs_review():
    store = MemoryRunStore()
    rec = RunRecord(message_id="<bad@x>", gmail_id="g2", attachment_ids=["att2"])
    created = store.create_received(rec)

    class Boom:
        def download_attachment(self, gmail_id: str, attachment_id: str) -> bytes:
            raise RuntimeError("gmail down")

    out = process_received_runs([created], Boom(), store, FakeExtractor(_valid_plan()))
    assert out[0].status == RunStatus.needs_review
    assert out[0].gate_failures == ["extract_error"]
