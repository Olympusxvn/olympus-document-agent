from store.models import RunRecord, TERMINAL_STATUSES
from store.runs import MemoryRunStore


def test_create_received_new_message():
    store = MemoryRunStore()
    result = store.create_received(
        RunRecord(message_id="<a@b.com>", gmail_id="g1", history_id="1")
    )
    assert result.created is True
    assert result.record.status == "received"
    assert store.get("<a@b.com>") is not None


def test_create_received_does_not_clobber_posted():
    store = MemoryRunStore()
    store.create_received(RunRecord(message_id="id-1"))
    posted = store.get("id-1")
    assert posted is not None
    store._docs[list(store._docs.keys())[0]] = posted.model_copy(
        update={"status": "posted"}
    )
    result = store.create_received(RunRecord(message_id="id-1"))
    assert result.created is False
    assert result.skipped_terminal is True
    assert result.record.status == "posted"
    assert "posted" in {s.value for s in TERMINAL_STATUSES}


def test_list_recent_orders_newest_first():
    store = MemoryRunStore()
    store.create_received(RunRecord(message_id="old", received_at="2026-01-01T00:00:00+00:00"))
    store.create_received(RunRecord(message_id="new", received_at="2026-08-25T00:00:00+00:00"))
    listed = store.list_recent(10)
    assert [item.message_id for item in listed] == ["new", "old"]
