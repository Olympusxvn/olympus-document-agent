from __future__ import annotations

import os
from dataclasses import dataclass, field

from extract.plan import InvoicePlan


@dataclass(frozen=True)
class GateResult:
    passed: bool
    failures: list[str] = field(default_factory=list)


def evaluate_gates(
    plan: InvoicePlan,
    *,
    posted_identities: set[tuple[str, str]] | None = None,
    confidence_threshold: float | None = None,
    math_tolerance_vnd: int | None = None,
) -> GateResult:
    threshold = (
        confidence_threshold
        if confidence_threshold is not None
        else float(os.environ.get("HARNESS_CONFIDENCE_THRESHOLD", "0.75"))
    )
    tolerance = (
        math_tolerance_vnd
        if math_tolerance_vnd is not None
        else int(os.environ.get("HARNESS_MATH_TOLERANCE_VND", "1"))
    )
    posted = posted_identities or set()
    failures: list[str] = []

    if not str(plan.invoice_number).strip() or not str(plan.seller_mst).strip():
        failures.append("schema")
    if plan.subtotal is None or plan.vat_amount is None or plan.total is None:
        failures.append("schema")

    if abs((plan.subtotal + plan.vat_amount) - plan.total) > tolerance:
        failures.append("math")

    if plan.confidence < threshold:
        failures.append("confidence")

    identity = (str(plan.seller_mst).strip(), str(plan.invoice_number).strip())
    if identity in posted and identity != ("", ""):
        failures.append("duplicate_invoice")

    return GateResult(passed=len(failures) == 0, failures=failures)
