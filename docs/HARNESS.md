# Harness contract

The model proposes a **Plan**. The **Harness** is the only component that may call Google Sheets or Gmail write APIs. This file is the spec for Phase 2–3; ADK agent code must not contradict it.

See also: [CONTEXT.md](../CONTEXT.md), [adr/0001-model-reasons-machine-executes.md](adr/0001-model-reasons-machine-executes.md).

## State machine

Firestore document id: Gmail `message-id` (RFC 5322, stable across retries).

```
received → extracting → validating → validated   (Phase 2; no Sheets yet)
                                 ↘ needs_review
                                 ↘ skipped_duplicate
validated → posted                                 (Phase 3 Sheets append)
```

| Status | Meaning | Side effects allowed |
|--------|---------|----------------------|
| `received` | Ingest stored the message-id and attachment refs | none |
| `extracting` | Gemini is filling a Plan | none |
| `validating` | Gates running | none |
| `validated` | All required gates passed. Sheets write is Phase 3 | none |
| `posted` | All required gates passed and Sheets append succeeded | Sheets (already done) |
| `needs_review` | Schema, math, confidence, or extract failed | Gmail draft in Phase 3 |
| `skipped_duplicate` | Same message-id already terminal, or (seller_mst, invoice_number) already `validated` or `posted` | none |

Transitions are monotonic. A terminal status (`validated`, `posted`, `needs_review`, `skipped_duplicate`) never goes back to `extracting`.

Crash rule: if status is `posted`, a retry must no-op. If status is `validating` and Sheets append is uncertain, the harness **reads** the Sheet (or a Firestore `sheet_row_id`) before appending — prefer recording `sheet_row_id` in the same Firestore transaction after a successful append.

## Plan schema (model output)

Gemini returns JSON matching this shape. Pydantic is the parser; extra fields are ignored.

```json
{
  "invoice_number": "string",
  "seller_mst": "string",
  "buyer_mst": "string | null",
  "invoice_date": "YYYY-MM-DD | null",
  "seller_name": "string | null",
  "currency": "VND",
  "subtotal": 0,
  "vat_amount": 0,
  "total": 0,
  "line_items": [],
  "confidence": 0.0,
  "notes": "string | null"
}
```

Money fields are integers (VND). `confidence` is 0.0–1.0. The model may set `notes` for illegible regions; notes never override gates.

## Code gates

Evaluated in order. First fail wins. The model does not see gate internals and cannot skip them.

| Gate | Pass condition | On fail |
|------|----------------|---------|
| Schema | Non-empty `invoice_number`, `seller_mst`, `subtotal`, `vat_amount`, `total`; types parse | `needs_review` |
| Math | `subtotal + vat_amount == total` with absolute tolerance **1** VND | `needs_review` |
| Confidence | `confidence >= HARNESS_CONFIDENCE_THRESHOLD` (default **0.75**) | `needs_review` |
| Idempotency (message) | No existing Run with this message-id in a terminal status | `skipped_duplicate` |
| Idempotency (invoice) | No existing **validated or posted** Run with same `(seller_mst, invoice_number)` | `skipped_duplicate` |

Write permission:

```
math pass AND schema pass AND confidence pass AND not duplicate
  → Phase 2: status validated (no Sheets)
  → Phase 3: EXEC-01 Sheets append → posted
else if duplicate
  → skipped_duplicate, no draft required
else
  → needs_review; Phase 3 EXEC-02 Gmail draft, no Sheets
```

Optional **GATE-05** (v2 / if time): MST Mod-11 on the 10-digit base (weights `31,29,23,19,17,13,7,5,3`; check digit `11 - (sum mod 11)` with 11→0 and 10 invalid). 13-digit codes use the first 10 digits. Failure → `needs_review`. Do not block the film if unimplemented.

## Tools (harness-only)

These functions exist as Python callables invoked **after** gates. They are not registered on the LLM agent.

### `sheets_append_posted(plan, run) -> sheet_row_id`

- Appends one row to the demo spreadsheet tab `Posted`.
- Columns: `posted_at`, `message_id`, `invoice_number`, `seller_mst`, `invoice_date`, `subtotal`, `vat_amount`, `total`, `confidence`.
- Must be called at most once per message-id. Use Firestore transaction: if status already `posted`, return existing `sheet_row_id`.

### `gmail_create_review_draft(plan, run, gate_failures) -> draft_id`

- Creates a draft to the operator (dedicated inbox), never `messages.send`.
- Body lists failed gate names, Plan snapshot, and Gmail permalink if available.
- Must not run on `skipped_duplicate` unless we never notified (default: skip).

### Forbidden

- `messages.send`
- Any Google API from inside the Gemini tool list
- Appending to Sheets from a `needs_review` path

## Extractor (model)

- Model: `gemini-3.5-flash` or newer (verify id on Vertex vs AI Studio).
- Input: invoice image and/or PDF bytes from Gmail.
- Output: Plan JSON only.
- On schema fail: **one** re-extract with a tighter “fill required fields” prompt, then gate again. No crop/ROI loop.

## Configuration

| Env | Default | Role |
|-----|---------|------|
| `HARNESS_CONFIDENCE_THRESHOLD` | `0.75` | GATE-03 |
| `HARNESS_MATH_TOLERANCE_VND` | `1` | GATE-02 |
| `SHEETS_SPREADSHEET_ID` | required | EXEC-01 |
| `SHEETS_POSTED_TAB` | `Posted` | EXEC-01 |
| `GMAIL_OPERATOR` | dedicated inbox | EXEC-02 |
| `PUBSUB_FALLBACK_POLL` | `false` | If true, Scheduler poll replaces push |

## Test fixtures (Phase 2 must ship)

1. **pass.json** — numbers add up, confidence 0.9 → would append
2. **math_fail.json** — `subtotal + vat != total` → `needs_review`
3. **low_conf.json** — confidence 0.4, math ok → `needs_review`
4. **dup_invoice.json** — same MST + số HĐ as a posted fixture → `skipped_duplicate`
