from ingest.handler import ingest_messages
from ingest.gmail_sync import GmailMessage
from store.models import RunRecord, RunStatus
from store.runs import MemoryRunStore


class FakeGmail:
    def __init__(self, messages: list[GmailMessage]) -> None:
        self.messages = messages
        self.calls: list[tuple[str, str]] = []

    def messages_since(self, email_address: str, history_id: str) -> list[GmailMessage]:
        self.calls.append((email_address, history_id))
        return self.messages


def test_ingest_creates_received_run():
    store = MemoryRunStore()
    gmail = FakeGmail(
        [
            GmailMessage(
                gmail_id="abc",
                message_id="<inv@mail>",
                attachment_ids=["att1"],
            )
        ]
    )
    results = ingest_messages("vat@x.com", "42", gmail, store)
    assert len(results) == 1
    assert results[0].created is True
    run = store.get("<inv@mail>")
    assert run is not None
    assert run.status == RunStatus.received
    assert run.attachment_ids == ["att1"]
    assert gmail.calls == [("vat@x.com", "42")]


def test_ingest_skips_when_already_posted():
    store = MemoryRunStore()
    store.create_received(RunRecord(message_id="<inv@mail>"))
    existing = store.get("<inv@mail>")
    assert existing is not None
    store._docs[list(store._docs.keys())[0]] = existing.model_copy(
        update={"status": RunStatus.posted}
    )
    gmail = FakeGmail(
        [GmailMessage(gmail_id="abc", message_id="<inv@mail>", attachment_ids=[])]
    )
    results = ingest_messages("vat@x.com", "99", gmail, store)
    assert results[0].skipped_terminal is True
    assert store.get("<inv@mail>").status == RunStatus.posted
