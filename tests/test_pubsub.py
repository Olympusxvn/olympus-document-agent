import base64
import json

import pytest

from ingest.pubsub import PubSubDecodeError, decode_gmail_notification


def test_decode_gmail_push_payload():
    inner = {"emailAddress": "vat@example.com", "historyId": "98765"}
    envelope = {
        "message": {
            "data": base64.b64encode(json.dumps(inner).encode()).decode(),
            "messageId": "pubsub-1",
        }
    }
    note = decode_gmail_notification(envelope)
    assert note.email_address == "vat@example.com"
    assert note.history_id == "98765"


def test_decode_rejects_missing_data():
    with pytest.raises(PubSubDecodeError):
        decode_gmail_notification({"message": {}})
