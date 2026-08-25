from __future__ import annotations

from ingest.gmail_sync import GmailPort
from store.models import RunRecord
from store.runs import CreateReceivedResult, RunStorePort


def ingest_messages(
    email_address: str,
    history_id: str,
    gmail: GmailPort,
    store: RunStorePort,
) -> list[CreateReceivedResult]:
    messages = gmail.messages_since(email_address, history_id)
    results: list[CreateReceivedResult] = []
    for msg in messages:
        record = RunRecord(
            message_id=msg.message_id,
            gmail_id=msg.gmail_id,
            history_id=history_id,
            email_address=email_address,
            attachment_ids=list(msg.attachment_ids),
        )
        results.append(store.create_received(record))
    return results


def ingest_poll(email_address: str, gmail: GmailPort, store: RunStorePort) -> list[CreateReceivedResult]:
    messages = gmail.list_inbox_candidates(email_address)
    results: list[CreateReceivedResult] = []
    for msg in messages:
        record = RunRecord(
            message_id=msg.message_id,
            gmail_id=msg.gmail_id,
            email_address=email_address,
            attachment_ids=list(msg.attachment_ids),
        )
        results.append(store.create_received(record))
    return results
