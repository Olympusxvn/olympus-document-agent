from __future__ import annotations

from google.cloud import firestore

CURSOR_COLLECTION = "mailbox_cursors"
CURSOR_DOC = "gmail"


class MailboxCursorStore:
    def __init__(self, client: firestore.Client | None = None) -> None:
        self._db = client or firestore.Client()
        self._ref = self._db.collection(CURSOR_COLLECTION).document(CURSOR_DOC)

    def get_history_id(self) -> str | None:
        snap = self._ref.get()
        if not snap.exists:
            return None
        data = snap.to_dict() or {}
        value = data.get("history_id")
        return str(value) if value is not None else None

    def set_history_id(self, history_id: str) -> None:
        self._ref.set({"history_id": str(history_id)}, merge=True)
