from __future__ import annotations

from google.cloud import firestore

from store.models import (
    INVOICE_OCCUPIED_STATUSES,
    TERMINAL_STATUSES,
    RunRecord,
    RunStatus,
    firestore_doc_id,
)
from store.runs import CreateReceivedResult


class FirestoreRunStore:
    def __init__(self, client: firestore.Client | None = None, collection: str = "runs") -> None:
        self._db = client or firestore.Client()
        self._col = self._db.collection(collection)

    def get(self, message_id: str) -> RunRecord | None:
        snap = self._col.document(firestore_doc_id(message_id)).get()
        if not snap.exists:
            return None
        return RunRecord.model_validate(snap.to_dict())

    def create_received(self, record: RunRecord) -> CreateReceivedResult:
        doc_ref = self._col.document(firestore_doc_id(record.message_id))

        @firestore.transactional
        def _txn(transaction: firestore.Transaction) -> CreateReceivedResult:
            snap = doc_ref.get(transaction=transaction)
            if snap.exists:
                existing = RunRecord.model_validate(snap.to_dict())
                if existing.status in TERMINAL_STATUSES:
                    return CreateReceivedResult(
                        record=existing, created=False, skipped_terminal=True
                    )
                return CreateReceivedResult(record=existing, created=False)
            stored = record.model_copy(update={"status": RunStatus.received})
            transaction.set(doc_ref, stored.model_dump())
            return CreateReceivedResult(record=stored, created=True)

        return _txn(self._db.transaction())

    def save(self, record: RunRecord) -> RunRecord:
        self._col.document(firestore_doc_id(record.message_id)).set(record.model_dump())
        return record

    def posted_identities(self) -> set[tuple[str, str]]:
        found: set[tuple[str, str]] = set()
        for status in INVOICE_OCCUPIED_STATUSES:
            for snap in self._col.where("status", "==", status.value).stream():
                rec = RunRecord.model_validate(snap.to_dict())
                if rec.seller_mst and rec.invoice_number:
                    found.add((rec.seller_mst, rec.invoice_number))
        return found

    def list_recent(self, limit: int = 50) -> list[RunRecord]:
        query = self._col.order_by(
            "received_at", direction=firestore.Query.DESCENDING
        ).limit(limit)
        records: list[RunRecord] = []
        for snap in query.stream():
            records.append(RunRecord.model_validate(snap.to_dict()))
        return records
