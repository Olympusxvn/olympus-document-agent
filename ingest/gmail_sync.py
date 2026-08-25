from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class GmailMessage:
    gmail_id: str
    message_id: str
    attachment_ids: list[str] = field(default_factory=list)


class GmailPort(Protocol):
    def messages_since(self, email_address: str, history_id: str) -> list[GmailMessage]:
        ...

    def list_inbox_candidates(self, email_address: str) -> list[GmailMessage]:
        ...


def rfc_message_id_from_headers(
    headers: list[dict], *, gmail_id: str | None = None
) -> str:
    for header in headers:
        if header.get("name", "").lower() == "message-id":
            value = (header.get("value") or "").strip()
            if value:
                return value
    if gmail_id:
        return gmail_id
    raise ValueError("no Message-ID header and no gmail_id fallback")


def attachment_ids_from_payload(payload: dict | None) -> list[str]:
    if not payload:
        return []
    found: list[str] = []
    body = payload.get("body") or {}
    if payload.get("filename") and body.get("attachmentId"):
        found.append(body["attachmentId"])
    for part in payload.get("parts") or []:
        found.extend(attachment_ids_from_payload(part))
    seen: set[str] = set()
    unique: list[str] = []
    for item in found:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def message_from_gmail_resource(resource: dict) -> GmailMessage:
    gmail_id = resource["id"]
    payload = resource.get("payload") or {}
    headers = payload.get("headers") or []
    return GmailMessage(
        gmail_id=gmail_id,
        message_id=rfc_message_id_from_headers(headers, gmail_id=gmail_id),
        attachment_ids=attachment_ids_from_payload(payload),
    )
