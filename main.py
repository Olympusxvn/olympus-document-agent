from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Header, HTTPException, Request
from google.adk.cli.fast_api import get_fast_api_app

from ingest.gmail_api import GmailApi
from ingest.handler import ingest_messages, ingest_poll
from ingest.pubsub import PubSubDecodeError, decode_gmail_notification
from store.cursors import MailboxCursorStore
from store.firestore_runs import FirestoreRunStore

load_dotenv()

AGENT_DIR = str(Path(__file__).resolve().parent)
app = get_fast_api_app(agents_dir=AGENT_DIR, web=False)
app.title = "Olympus VAT Agent"


def _require_ingest_token(
    authorization: str | None = None, x_ingest_token: str | None = None
) -> None:
    expected = os.environ.get("INGEST_TOKEN")
    if not expected:
        return
    token = x_ingest_token
    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
    if token != expected:
        raise HTTPException(status_code=401, detail="invalid ingest token")


def _gmail() -> GmailApi:
    return GmailApi(cursor=MailboxCursorStore())


def _store() -> FirestoreRunStore:
    return FirestoreRunStore()


@app.get("/health")
def health() -> dict[str, str | int]:
    return {"status": "ok", "phase": 1}


@app.post("/pubsub")
async def pubsub_push(request: Request) -> dict:
    try:
        envelope = await request.json()
        note = decode_gmail_notification(envelope)
    except PubSubDecodeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    results = ingest_messages(note.email_address, note.history_id, _gmail(), _store())
    return {
        "ok": True,
        "created": sum(1 for item in results if item.created),
        "skipped_terminal": sum(1 for item in results if item.skipped_terminal),
    }


@app.post("/internal/poll")
def internal_poll(
    authorization: str | None = Header(default=None),
    x_ingest_token: str | None = Header(default=None),
) -> dict:
    _require_ingest_token(authorization, x_ingest_token)
    email = os.environ.get("GMAIL_ADDRESS", "me")
    results = ingest_poll(email, _gmail(), _store())
    return {"ok": True, "created": sum(1 for item in results if item.created)}


@app.post("/internal/watch-renew")
def internal_watch_renew(
    authorization: str | None = Header(default=None),
    x_ingest_token: str | None = Header(default=None),
) -> dict:
    _require_ingest_token(authorization, x_ingest_token)
    topic = os.environ["GMAIL_PUBSUB_TOPIC"]
    response = _gmail().renew_watch(topic)
    return {"ok": True, "watch": response}
