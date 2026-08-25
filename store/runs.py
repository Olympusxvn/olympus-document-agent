from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from store.models import (
    INVOICE_OCCUPIED_STATUSES,
    TERMINAL_STATUSES,
    RunRecord,
    RunStatus,
    firestore_doc_id,
)


@dataclass(frozen=True)
class CreateReceivedResult:
    record: RunRecord
    created: bool
    skipped_terminal: bool = False


class RunStorePort(Protocol):
    def get(self, message_id: str) -> RunRecord | None: ...

    def create_received(self, record: RunRecord) -> CreateReceivedResult: ...

    def save(self, record: RunRecord) -> RunRecord: ...

    def posted_identities(self) -> set[tuple[str, str]]: ...

    def list_recent(self, limit: int = 50) -> list[RunRecord]: ...


class MemoryRunStore:
    """In-memory RunStore for tests. FirestoreRunStore matches this surface."""

    def __init__(self) -> None:
        self._docs: dict[str, RunRecord] = {}

    def get(self, message_id: str) -> RunRecord | None:
        return self._docs.get(firestore_doc_id(message_id))

    def create_received(self, record: RunRecord) -> CreateReceivedResult:
        key = firestore_doc_id(record.message_id)
        existing = self._docs.get(key)
        if existing and existing.status in TERMINAL_STATUSES:
            return CreateReceivedResult(
                record=existing, created=False, skipped_terminal=True
            )
        if existing:
            return CreateReceivedResult(record=existing, created=False)
        stored = record.model_copy(update={"status": RunStatus.received})
        self._docs[key] = stored
        return CreateReceivedResult(record=stored, created=True)

    def save(self, record: RunRecord) -> RunRecord:
        self._docs[firestore_doc_id(record.message_id)] = record
        return record

    def posted_identities(self) -> set[tuple[str, str]]:
        found: set[tuple[str, str]] = set()
        for rec in self._docs.values():
            if rec.status in INVOICE_OCCUPIED_STATUSES and rec.seller_mst and rec.invoice_number:
                found.add((rec.seller_mst, rec.invoice_number))
        return found

    def list_recent(self, limit: int = 50) -> list[RunRecord]:
        records = list(self._docs.values())
        records.sort(key=lambda rec: rec.received_at, reverse=True)
        return records[:limit]
