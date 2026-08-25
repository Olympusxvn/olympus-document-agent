from enum import StrEnum

from pydantic import BaseModel, Field


class RunStatus(StrEnum):
    received = "received"
    extracting = "extracting"
    validating = "validating"
    posted = "posted"
    needs_review = "needs_review"
    skipped_duplicate = "skipped_duplicate"


TERMINAL_STATUSES = frozenset(
    {RunStatus.posted, RunStatus.needs_review, RunStatus.skipped_duplicate}
)


class RunRecord(BaseModel):
    message_id: str
    gmail_id: str | None = None
    history_id: str | None = None
    email_address: str | None = None
    status: RunStatus = RunStatus.received
    attachment_ids: list[str] = Field(default_factory=list)
    sheet_row_id: str | None = None
    draft_id: str | None = None


def firestore_doc_id(message_id: str) -> str:
    cleaned = message_id.strip().strip("<>")
    return cleaned.replace("/", "_")[:1500]
