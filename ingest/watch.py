WATCH_RENEW_DAYS = 1

def build_watch_body(topic_name: str) -> dict:
    return {
        "topicName": topic_name,
        "labelIds": ["INBOX"],
        "labelFilterBehavior": "INCLUDE",
    }
