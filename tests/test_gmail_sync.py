from ingest.gmail_sync import GmailMessage, message_from_gmail_resource, rfc_message_id_from_headers


def test_rfc_message_id_from_headers():
    headers = [
        {"name": "From", "value": "a@b.com"},
        {"name": "Message-ID", "value": "<x@y.com>"},
    ]
    assert rfc_message_id_from_headers(headers) == "<x@y.com>"


def test_rfc_message_id_falls_back_to_gmail_id():
    assert rfc_message_id_from_headers([], gmail_id="g-99") == "g-99"


def test_gmail_message_dataclass():
    msg = GmailMessage(gmail_id="1", message_id="<a>", attachment_ids=["p"], sender="a@b.com")
    assert msg.attachment_ids == ["p"]
    assert msg.sender == "a@b.com"


def test_message_from_gmail_resource_reads_from_header():
    parsed = message_from_gmail_resource(
        {
            "id": "g1",
            "payload": {
                "headers": [
                    {"name": "From", "value": "seller@example.com"},
                    {"name": "Message-ID", "value": "<inv@mail>"},
                ],
                "filename": "invoice.jpg",
                "body": {"attachmentId": "att-1"},
            },
        }
    )
    assert parsed.message_id == "<inv@mail>"
    assert parsed.sender == "seller@example.com"
    assert parsed.attachment_ids == ["att-1"]

