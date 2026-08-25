# Olympus VAT Agent

Event-driven processing of Vietnamese VAT invoices from Gmail into a ledger, with a hard split between model reasoning and machine execution.

## Language

**Invoice**:
A Vietnamese VAT invoice (hóa đơn GTGT) as a photo or PDF attached to or inline in a Gmail message. One Invoice per processing run.
_Avoid_: Receipt, bill, chứng từ (too broad — v1 is VAT invoices only)

**Run**:
One attempt to process one Gmail message through extract → gates → Sheets or draft. Identified by Gmail `message-id`.
_Avoid_: Job, task, session (overloaded with ADK session)

**Plan**:
The structured JSON Gemini returns (fields + confidence). A Plan is a proposal, not permission to write.
_Avoid_: Tool call, function call, action (those are harness-owned)

**Harness**:
Deterministic code that validates a Plan and is the only component allowed to call Sheets or Gmail APIs.
_Avoid_: Agent (the ADK process includes both model and harness; say Harness for the execution half)

**Code gate**:
A pure function over a Plan (schema, arithmetic, confidence, idempotency) that returns pass or fail. Fail forbids Sheets append.
_Avoid_: Guardrail, Model Armor (different Google products)

**Posted**:
A Run whose Plan passed every Code gate and whose Sheets append succeeded. Firestore records this so retries cannot append again.
_Avoid_: Saved, synced, complete (ambiguous if draft-only)

**Needs review**:
A Run that failed a Code gate or fell below confidence. The Harness creates a Gmail draft; it does not append Sheets.
_Avoid_: Error, rejected (the invoice may be valid in the world — we declined to post)

**Skipped duplicate**:
A Run whose Gmail `message-id` or (seller MST + invoice number) was already Posted or already processed.
_Avoid_: Ignored, filtered

**Dedicated inbox**:
The hackathon Gmail account watched by the agent. Not a personal mailbox.
_Avoid_: User inbox, my Gmail

## Flagged ambiguities

- **Agent**: In ADK docs this is the whole process. In this repo, say **model** vs **Harness**. The Cloud Run service is the **runtime**.
- **Draft**: Always a Gmail draft to the operator. Never a draft row in Sheets as the success path.

## Example dialogue

Dev: A duplicate Invoice arrived on a new message-id. Do we Needs review?
Domain: No. If seller MST + số HĐ already Posted, the Run is Skipped duplicate — no second Sheets row, no extra draft unless we never posted.
Dev: Gemini is sure the total is right but subtotal + VAT doesn't match. Can we trust the Plan?
Domain: No. Arithmetic is a Code gate. That Run is Needs review. The model does not override math.
