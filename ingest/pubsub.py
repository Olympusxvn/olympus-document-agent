from __future__ import annotations

import base64
import json
from dataclasses import dataclass


class PubSubDecodeError(ValueError):
    pass


@dataclass(frozen=True)
class GmailNotification:
    email_address: str
    history_id: str


def decode_gmail_notification(envelope: dict) -> GmailNotification:
    message = envelope.get("message") or {}
    data = message.get("data")
    if not data:
        raise PubSubDecodeError("missing message.data")
    try:
        raw = base64.b64decode(data)
        payload = json.loads(raw.decode("utf-8"))
    except (ValueError, json.JSONDecodeError) as exc:
        raise PubSubDecodeError("invalid message.data") from exc
    email = payload.get("emailAddress")
    history_id = payload.get("historyId")
    if not email or history_id is None:
        raise PubSubDecodeError("missing emailAddress or historyId")
    return GmailNotification(email_address=str(email), history_id=str(history_id))
