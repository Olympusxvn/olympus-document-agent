from extract.plan import InvoicePlan
from harness.drafts import review_draft_body
from harness.sheets import SheetsLedger, posted_row
from pipeline.process import apply_plan, process_received_runs
from store.models import RunRecord, RunStatus
from store.runs import MemoryRunStore


class FakeLedger:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str]] = []

    def append_posted(self, plan: InvoicePlan, run: RunRecord) -> str:
        if run.sheet_row_id:
            return run.sheet_row_id
        token = f"Posted!A{len(self.rows) + 2}"
        self.rows.append((plan.invoice_number, run.message_id))
        return token


class FakeDrafts:
    def __init__(self) -> None:
        self.created: list[list[str]] = []

    def create_review_draft(
        self, plan: InvoicePlan, run: RunRecord, gate_failures: list[str]
    ) -> str:
        self.created.append(list(gate_failures))
        return f"draft-{len(self.created)}"


class BoomLedger:
    def append_posted(self, plan: InvoicePlan, run: RunRecord) -> str:
        raise RuntimeError("sheets down")


def _valid_plan(**kwargs) -> InvoicePlan:
    base = dict(
        invoice_number="HD-1",
        seller_mst="0101243150",
        invoice_date="2026-08-01",
        subtotal=100,
        vat_amount=10,
        total=110,
        confidence=0.9,
    )
    base.update(kwargs)
    return InvoicePlan.model_validate(base)


def test_posted_row_column_order():
    rec = RunRecord(message_id="<a@b>")
    row = posted_row(_valid_plan(), rec, posted_at="2026-08-25T00:00:00+00:00")
    assert row[0] == "2026-08-25T00:00:00+00:00"
    assert row[1] == "<a@b>"
    assert row[2] == "HD-1"
    assert row[3] == "0101243150"
    assert row[4] == "2026-08-01"
    assert row[5] == 100
    assert row[6] == 10
    assert row[7] == 110
    assert row[8] == 0.9


def test_apply_plan_posted_when_ledger_present():
    store = MemoryRunStore()
    rec = RunRecord(message_id="<pass@x>")
    store.create_received(rec)
    ledger = FakeLedger()
    drafts = FakeDrafts()
    out = apply_plan(store, rec, _valid_plan(), ledger=ledger, drafts=drafts)
    assert out.status == RunStatus.posted
    assert out.sheet_row_id == "Posted!A2"
    assert ledger.rows == [("HD-1", "<pass@x>")]
    assert drafts.created == []


def test_apply_plan_math_fail_draft_no_sheet():
    store = MemoryRunStore()
    rec = RunRecord(message_id="<fail@x>", gmail_id="g99")
    store.create_received(rec)
    ledger = FakeLedger()
    drafts = FakeDrafts()
    out = apply_plan(
        store, rec, _valid_plan(total=1), ledger=ledger, drafts=drafts
    )
    assert out.status == RunStatus.needs_review
    assert out.sheet_row_id is None
    assert ledger.rows == []
    assert out.draft_id == "draft-1"
    assert "math" in drafts.created[0]


def test_apply_plan_duplicate_no_sheet_no_draft():
    store = MemoryRunStore()
    store.save(
        RunRecord(
            message_id="<old@x>",
            status=RunStatus.posted,
            seller_mst="0101243150",
            invoice_number="HD-1",
            sheet_row_id="Posted!A2",
        )
    )
    rec = RunRecord(message_id="<dup@x>")
    store.create_received(rec)
    ledger = FakeLedger()
    drafts = FakeDrafts()
    out = apply_plan(store, rec, _valid_plan(), ledger=ledger, drafts=drafts)
    assert out.status == RunStatus.skipped_duplicate
    assert ledger.rows == []
    assert drafts.created == []


def test_append_posted_idempotent_when_already_posted():
    ledger = SheetsLedger(spreadsheet_id="sheet", service=object())
    rec = RunRecord(
        message_id="<a@b>",
        status=RunStatus.posted,
        sheet_row_id="Posted!A9",
    )
    assert ledger.append_posted(_valid_plan(), rec) == "Posted!A9"


def test_sheets_error_becomes_needs_review_draft():
    store = MemoryRunStore()
    rec = RunRecord(message_id="<err@x>")
    store.create_received(rec)
    drafts = FakeDrafts()
    out = apply_plan(
        store, rec, _valid_plan(), ledger=BoomLedger(), drafts=drafts
    )
    assert out.status == RunStatus.needs_review
    assert "sheets_error" in out.gate_failures
    assert drafts.created


def test_draft_body_lists_gates_and_permalink():
    rec = RunRecord(message_id="<m@x>", gmail_id="abc123")
    body = review_draft_body(_valid_plan(), rec, ["math"])
    assert "math" in body
    assert "abc123" in body
    assert "messages.send" not in body


def test_drafts_module_never_calls_messages_send():
    from pathlib import Path

    text = Path("harness/drafts.py").read_text(encoding="utf-8")
    assert "messages().send" not in text
    assert "users().messages().send" not in text
    assert ".drafts()" in text


def test_process_received_posts_when_ledger_wired():
    store = MemoryRunStore()
    rec = RunRecord(message_id="<img@x>", gmail_id="g1", attachment_ids=["att1"])
    created = store.create_received(rec)
    ledger = FakeLedger()

    class Extractor:
        def extract(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> InvoicePlan:
            return _valid_plan()

    class Gmail:
        def download_attachment(self, gmail_id: str, attachment_id: str) -> bytes:
            return b"%PDF-1.4"

    out = process_received_runs(
        [created], Gmail(), store, Extractor(), ledger=ledger, drafts=FakeDrafts()
    )
    assert out[0].status == RunStatus.posted
    assert ledger.rows
