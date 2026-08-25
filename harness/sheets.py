from __future__ import annotations

from datetime import datetime, timezone

from extract.plan import InvoicePlan
from store.models import RunRecord, RunStatus


POSTED_COLUMNS = [
    "posted_at",
    "message_id",
    "invoice_number",
    "seller_mst",
    "invoice_date",
    "subtotal",
    "vat_amount",
    "total",
    "confidence",
]


def posted_row(plan: InvoicePlan, run: RunRecord, posted_at: str | None = None) -> list:
    stamp = posted_at or datetime.now(timezone.utc).isoformat()
    return [
        stamp,
        run.message_id,
        plan.invoice_number,
        plan.seller_mst,
        plan.invoice_date or "",
        plan.subtotal,
        plan.vat_amount,
        plan.total,
        plan.confidence,
    ]


class SheetsLedger:
    """Harness-only Sheets writer. Not registered on the ADK agent."""

    def __init__(
        self,
        spreadsheet_id: str,
        tab: str = "Posted",
        service=None,
    ) -> None:
        self.spreadsheet_id = spreadsheet_id
        self.tab = tab
        self._service = service

    @property
    def service(self):
        if self._service is None:
            from googleapiclient.discovery import build

            from ingest.credentials import gmail_credentials

            self._service = build("sheets", "v4", credentials=gmail_credentials())
        return self._service

    def append_posted(self, plan: InvoicePlan, run: RunRecord) -> str:
        if run.status == RunStatus.posted and run.sheet_row_id:
            return run.sheet_row_id
        body = {"values": [posted_row(plan, run)]}
        response = (
            self.service.spreadsheets()
            .values()
            .append(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.tab}!A1",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body=body,
            )
            .execute()
        )
        updates = response.get("updates") or {}
        return str(updates.get("updatedRange") or f"{self.tab}!A2")
