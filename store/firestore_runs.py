from __future__ import annotations

from google.cloud import firestore

from store.models import TERMINAL_STATUSES, RunRecord, RunStatus, firestore_doc_id
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
