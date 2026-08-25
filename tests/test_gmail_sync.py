from ingest.gmail_sync import GmailMessage, rfc_message_id_from_headers


def test_rfc_message_id_from_headers():
    headers = [
        {"name": "From", "value": "a@b.com"},
        {"name": "Message-ID", "value": "<x@y.com>"},
    ]
    assert rfc_message_id_from_headers(headers) == "<x@y.com>"


def test_rfc_message_id_falls_back_to_gmail_id():
    assert rfc_message_id_from_headers([], gmail_id="g-99") == "g-99"


def test_gmail_message_dataclass():
    msg = GmailMessage(gmail_id="1", message_id="<a>", attachment_ids=["p"])
    assert msg.attachment_ids == ["p"]
