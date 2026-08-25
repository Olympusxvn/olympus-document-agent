from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from google.adk.cli.fast_api import get_fast_api_app

from extract.gemini import GeminiPlanExtractor
from harness.drafts import GmailReviewDrafts
from harness.sheets import SheetsLedger
from ingest.gmail_api import GmailApi
from ingest.handler import ingest_messages, ingest_poll
from ingest.pubsub import PubSubDecodeError, decode_gmail_notification
from pipeline.process import process_received_runs
from store.cursors import MailboxCursorStore
from store.firestore_runs import FirestoreRunStore

load_dotenv()

AGENT_DIR = str(Path(__file__).resolve().parent)
app = get_fast_api_app(agents_dir=AGENT_DIR, web=False)
app.title = "Olympus VAT Agent"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


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


def _extractor() -> GeminiPlanExtractor:
    return GeminiPlanExtractor()


def _ledger() -> SheetsLedger | None:
    spreadsheet_id = (os.environ.get("SHEETS_SPREADSHEET_ID") or "").strip()
    if not spreadsheet_id:
        return None
    tab = (os.environ.get("SHEETS_POSTED_TAB") or "Posted").strip() or "Posted"
    return SheetsLedger(spreadsheet_id=spreadsheet_id, tab=tab)


def _drafts() -> GmailReviewDrafts:
    return GmailReviewDrafts()


@app.get("/health")
def health() -> dict[str, str | int | bool]:
    return {
        "status": "ok",
        "phase": 3,
        "sheets_configured": bool((os.environ.get("SHEETS_SPREADSHEET_ID") or "").strip()),
    }


@app.get("/runs")
def list_runs() -> dict:
    records = _store().list_recent(50)
    return {"phase": 3, "runs": [item.model_dump() for item in records]}


@app.post("/pubsub")
async def pubsub_push(request: Request) -> dict:
    try:
        envelope = await request.json()
        note = decode_gmail_notification(envelope)
    except PubSubDecodeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    gmail = _gmail()
    store = _store()
    results = ingest_messages(note.email_address, note.history_id, gmail, store)
    processed = process_received_runs(
        results, gmail, store, _extractor(), ledger=_ledger(), drafts=_drafts()
    )
    return {
        "ok": True,
        "created": sum(1 for item in results if item.created),
        "skipped_terminal": sum(1 for item in results if item.skipped_terminal),
        "gated": len(processed),
    }


@app.post("/internal/poll")
def internal_poll(
    authorization: str | None = Header(default=None),
    x_ingest_token: str | None = Header(default=None),
) -> dict:
    _require_ingest_token(authorization, x_ingest_token)
    email = os.environ.get("GMAIL_ADDRESS", "me")
    gmail = _gmail()
    store = _store()
    results = ingest_poll(email, gmail, store)
    processed = process_received_runs(
        results, gmail, store, _extractor(), ledger=_ledger(), drafts=_drafts()
    )
    return {
        "ok": True,
        "created": sum(1 for item in results if item.created),
        "gated": len(processed),
    }


@app.post("/internal/watch-renew")
def internal_watch_renew(
    authorization: str | None = Header(default=None),
    x_ingest_token: str | None = Header(default=None),
) -> dict:
    _require_ingest_token(authorization, x_ingest_token)
    topic = os.environ["GMAIL_PUBSUB_TOPIC"]
    response = _gmail().renew_watch(topic)
    return {"ok": True, "watch": response}
