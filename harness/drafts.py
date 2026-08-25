from __future__ import annotations

import base64
import json
import os
from email.mime.text import MIMEText

from extract.plan import InvoicePlan
from store.models import RunRecord

# Harness-only. Forbidden: Gmail users.messages send.


def review_draft_body(plan: InvoicePlan, run: RunRecord, gate_failures: list[str]) -> str:
    permalink = ""
    if run.gmail_id:
        permalink = f"https://mail.google.com/mail/u/0/#all/{run.gmail_id}"
    snapshot = plan.model_dump()
    lines = [
        "Olympus VAT Agent — Needs review",
        "",
        f"Message-ID: {run.message_id}",
        f"Failed gates: {', '.join(gate_failures) or '(none)'}",
        f"Gmail: {permalink or '(no gmail_id)'}",
        "",
        "Plan snapshot:",
        json.dumps(snapshot, ensure_ascii=False, indent=2),
        "",
        "The harness did not append Google Sheets. The agent never sends mail.",
    ]
    return "\n".join(lines)


class GmailReviewDrafts:
    """Creates operator drafts. Forbidden: messages.send."""

    def __init__(self, service=None, operator: str | None = None) -> None:
        self._service = service
        self._operator = operator

    @property
    def service(self):
        if self._service is None:
            from googleapiclient.discovery import build

            from ingest.credentials import gmail_credentials

            self._service = build("gmail", "v1", credentials=gmail_credentials())
        return self._service

    def create_review_draft(
        self, plan: InvoicePlan, run: RunRecord, gate_failures: list[str]
    ) -> str:
        operator = (
            self._operator
            or (os.environ.get("GMAIL_OPERATOR") or "").strip()
            or (os.environ.get("GMAIL_ADDRESS") or "").strip()
            or "me"
        )
        subject = (
            f"[Olympus VAT] Needs review: {plan.invoice_number or run.message_id}"
        )
        message = MIMEText(review_draft_body(plan, run, gate_failures), _charset="utf-8")
        message["to"] = operator
        message["subject"] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        created = (
            self.service.users()
            .drafts()
            .create(userId="me", body={"message": {"raw": raw}})
            .execute()
        )
        return str(created.get("id") or "")
