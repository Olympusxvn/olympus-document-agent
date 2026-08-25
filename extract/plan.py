from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class InvoicePlan(BaseModel):
    invoice_number: str = ""
    seller_mst: str = ""
    buyer_mst: str | None = None
    invoice_date: str | None = None
    seller_name: str | None = None
    currency: str = "VND"
    subtotal: int = 0
    vat_amount: int = 0
    total: int = 0
    line_items: list[dict] = Field(default_factory=list)
    confidence: float = 0.0
    notes: str | None = None

    @field_validator("subtotal", "vat_amount", "total", mode="before")
    @classmethod
    def _money_int(cls, value: object) -> int:
        if value is None or value == "":
            return 0
        return int(round(float(value)))

    @field_validator("confidence", mode="before")
    @classmethod
    def _conf(cls, value: object) -> float:
        if value is None or value == "":
            return 0.0
        return float(value)


def plan_from_mapping(data: dict) -> InvoicePlan:
    return InvoicePlan.model_validate(data)
