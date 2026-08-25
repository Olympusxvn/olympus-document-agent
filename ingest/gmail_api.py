from __future__ import annotations

from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ingest.credentials import gmail_credentials
from ingest.gmail_sync import GmailMessage, message_from_gmail_resource
from ingest.watch import build_watch_body
from store.cursors import MailboxCursorStore


class GmailApi:
    def __init__(self, service: Any | None = None, cursor: MailboxCursorStore | None = None) -> None:
        self._service = service
        self._cursor = cursor

    @property
    def service(self) -> Any:
        if self._service is None:
            self._service = build("gmail", "v1", credentials=gmail_credentials())
        return self._service

    def messages_since(self, email_address: str, history_id: str) -> list[GmailMessage]:
        del email_address
        start = None
        if self._cursor is not None:
            start = self._cursor.get_history_id()
        if start is None:
            if self._cursor is not None:
                self._cursor.set_history_id(history_id)
            return self.list_inbox_candidates("me")
        messages = self._history_added(start)
        if self._cursor is not None:
            self._cursor.set_history_id(history_id)
        return messages

    def list_inbox_candidates(self, email_address: str) -> list[GmailMessage]:
        del email_address
        listed = (
            self.service.users()
            .messages()
            .list(userId="me", labelIds=["INBOX"], maxResults=15)
            .execute()
        )
        out: list[GmailMessage] = []
        for stub in listed.get("messages") or []:
            resource = (
                self.service.users()
                .messages()
                .get(userId="me", id=stub["id"], format="full")
                .execute()
            )
            parsed = message_from_gmail_resource(resource)
            if parsed.attachment_ids:
                out.append(parsed)
        return out

    def renew_watch(self, topic_name: str) -> dict:
        body = build_watch_body(topic_name)
        response = self.service.users().watch(userId="me", body=body).execute()
        if self._cursor is not None and response.get("historyId"):
            existing = self._cursor.get_history_id()
            if existing is None:
                self._cursor.set_history_id(str(response["historyId"]))
        return response

    def _history_added(self, start_history_id: str) -> list[GmailMessage]:
        gmail_ids: list[str] = []
        page_token = None
        try:
            while True:
                kwargs: dict[str, Any] = {
                    "userId": "me",
                    "startHistoryId": start_history_id,
                    "historyTypes": ["messageAdded"],
                }
                if page_token:
                    kwargs["pageToken"] = page_token
                listed = self.service.users().history().list(**kwargs).execute()
                for event in listed.get("history") or []:
                    for added in event.get("messagesAdded") or []:
                        msg = added.get("message") or {}
                        if msg.get("id"):
                            gmail_ids.append(msg["id"])
                page_token = listed.get("nextPageToken")
                if not page_token:
                    break
        except HttpError as exc:
            if exc.resp.status == 404:
                return self.list_inbox_candidates("me")
            raise
        out: list[GmailMessage] = []
        seen: set[str] = set()
        for gmail_id in gmail_ids:
            if gmail_id in seen:
                continue
            seen.add(gmail_id)
            resource = (
                self.service.users()
                .messages()
                .get(userId="me", id=gmail_id, format="full")
                .execute()
            )
            parsed = message_from_gmail_resource(resource)
            if parsed.attachment_ids:
                out.append(parsed)
        return out
