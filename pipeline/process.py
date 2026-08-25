from __future__ import annotations

from typing import Protocol

from extract.plan import InvoicePlan
from gates.evaluate import evaluate_gates
from store.models import RunRecord, RunStatus
from store.runs import CreateReceivedResult, RunStorePort


class PlanExtractor(Protocol):
    def extract(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> InvoicePlan: ...


class LedgerPort(Protocol):
    def append_posted(self, plan: InvoicePlan, run: RunRecord) -> str: ...


class DraftPort(Protocol):
    def create_review_draft(
        self, plan: InvoicePlan, run: RunRecord, gate_failures: list[str]
    ) -> str: ...


def attachment_mime(data: bytes) -> str:
    if data.startswith(b"%PDF"):
        return "application/pdf"
    if data.startswith(b"\x89PNG"):
        return "image/png"
    return "image/jpeg"


def apply_plan(
    store: RunStorePort,
    record: RunRecord,
    plan: InvoicePlan,
    ledger: LedgerPort | None = None,
    drafts: DraftPort | None = None,
) -> RunRecord:
    posted = store.posted_identities()
    result = evaluate_gates(plan, posted_identities=posted)
    status: RunStatus
    sheet_row_id = record.sheet_row_id
    draft_id = record.draft_id
    failures = list(result.failures)

    if "duplicate_invoice" in result.failures:
        status = RunStatus.skipped_duplicate
    elif result.passed:
        if ledger is not None:
            try:
                sheet_row_id = ledger.append_posted(plan, record)
                status = RunStatus.posted
            except Exception:
                status = RunStatus.needs_review
                failures.append("sheets_error")
                if drafts is not None:
                    try:
                        draft_id = drafts.create_review_draft(plan, record, failures)
                    except Exception:
                        pass
        else:
            status = RunStatus.validated
    else:
        status = RunStatus.needs_review
        if drafts is not None:
            try:
                draft_id = drafts.create_review_draft(plan, record, failures)
            except Exception:
                pass

    updated = record.model_copy(
        update={
            "status": status,
            "plan": plan.model_dump(),
            "gate_failures": failures,
            "seller_mst": plan.seller_mst,
            "invoice_number": plan.invoice_number,
            "sheet_row_id": sheet_row_id,
            "draft_id": draft_id,
        }
    )
    return store.save(updated)


def extract_and_gate(
    store: RunStorePort,
    record: RunRecord,
    image_bytes: bytes,
    extractor: PlanExtractor,
    mime_type: str = "image/jpeg",
    ledger: LedgerPort | None = None,
    drafts: DraftPort | None = None,
) -> RunRecord:
    from extract.gemini import extract_with_one_retry

    extracting = record.model_copy(update={"status": RunStatus.extracting})
    store.save(extracting)
    validating = extracting.model_copy(update={"status": RunStatus.validating})
    store.save(validating)
    plan = extract_with_one_retry(extractor, image_bytes, mime_type)
    return apply_plan(store, validating, plan, ledger=ledger, drafts=drafts)


def process_received_runs(
    results: list[CreateReceivedResult],
    gmail,
    store: RunStorePort,
    extractor: PlanExtractor,
    ledger: LedgerPort | None = None,
    drafts: DraftPort | None = None,
) -> list[RunRecord]:
    processed: list[RunRecord] = []
    for item in results:
        rec = item.record
        if rec.status != RunStatus.received:
            continue
        if not rec.gmail_id or not rec.attachment_ids:
            continue
        try:
            raw = gmail.download_attachment(rec.gmail_id, rec.attachment_ids[0])
            mime = attachment_mime(raw)
            processed.append(
                extract_and_gate(
                    store, rec, raw, extractor, mime, ledger=ledger, drafts=drafts
                )
            )
        except Exception:
            failures = ["extract_error"]
            draft_id = None
            if drafts is not None:
                try:
                    draft_id = drafts.create_review_draft(InvoicePlan(), rec, failures)
                except Exception:
                    pass
            processed.append(
                store.save(
                    rec.model_copy(
                        update={
                            "status": RunStatus.needs_review,
                            "gate_failures": failures,
                            "draft_id": draft_id,
                        }
                    )
                )
            )
    return processed
