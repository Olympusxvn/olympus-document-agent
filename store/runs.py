from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from store.models import TERMINAL_STATUSES, RunRecord, RunStatus, firestore_doc_id


@dataclass(frozen=True)
class CreateReceivedResult:
    record: RunRecord
    created: bool
    skipped_terminal: bool = False


class RunStorePort(Protocol):
    def get(self, message_id: str) -> RunRecord | None: ...

    def create_received(self, record: RunRecord) -> CreateReceivedResult: ...


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
