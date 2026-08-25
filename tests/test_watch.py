from ingest.watch import WATCH_RENEW_DAYS, build_watch_body


def test_watch_body_includes_topic_and_inbox():
    body = build_watch_body("projects/demo/topics/gmail-vat")
    assert body["topicName"] == "projects/demo/topics/gmail-vat"
    assert body["labelIds"] == ["INBOX"]
    assert body["labelFilterBehavior"] == "INCLUDE"


def test_watch_renew_window_is_under_seven_days():
    assert WATCH_RENEW_DAYS == 1
    assert WATCH_RENEW_DAYS < 7
