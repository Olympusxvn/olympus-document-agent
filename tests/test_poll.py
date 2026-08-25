from ingest.gmail_sync import GmailMessage
from ingest.handler import ingest_poll
from store.runs import MemoryRunStore


class FakeGmail:
    def messages_since(self, email_address: str, history_id: str):
        raise AssertionError("poll must not use history sync")

    def list_inbox_candidates(self, email_address: str):
        assert email_address == "vat@x.com"
        return [
            GmailMessage(gmail_id="z", message_id="<p@q>", attachment_ids=["a.pdf"])
        ]


def test_poll_creates_received():
    store = MemoryRunStore()
    results = ingest_poll("vat@x.com", FakeGmail(), store)
    assert results[0].created is True
    assert store.get("<p@q>").attachment_ids == ["a.pdf"]
