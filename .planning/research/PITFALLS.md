# Pitfalls Research

**Domain:** Event-driven VAT invoice → ledger agent
**Researched:** 2026-08-25
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Treating Function Calling as execution

**What goes wrong:**
Gemini chooses `spreadsheets.append` itself. The demo looks "agentic" and then double-writes, skips math, or sends mail.

**Why it happens:**
ADK samples wire tools onto the agent. Contest copy talks about agents taking action.

**How to avoid:**
Model tools = none (or read-only). Harness calls write APIs after gates. See `docs/adr/0001-model-reasons-machine-executes.md`.

**Warning signs:**
`tools=[append_sheet, create_draft]` on the LLM agent.

**Phase to address:**
Phase 2 (extract + gates) before any live Sheets call.

---

### Pitfall 2: The Gmail idempotency trap

**What goes wrong:**
Pub/Sub redelivers; `users.watch` fires on many inbox changes; Cloud Run retries after timeout → two Sheets rows for one invoice.

**Why it happens:**
Push notifications are at-least-once. Gmail payloads are historyIds, not unique invoice events.

**How to avoid:**
Idempotency keys: Gmail `message-id` and `(seller_mst, invoice_number)`. Firestore transaction before append. Treat duplicate as `skipped_duplicate`.

**Warning signs:**
Append without a prior "already processed?" read.

**Phase to address:**
Phase 1 store + Phase 3 tools.

---

### Pitfall 3: Letting the model do arithmetic

**What goes wrong:**
Invoice total "looks right" in the Plan while `subtotal + vat != total`. Posted ledger is wrong. Judges who check the sample image catch it.

**Why it happens:**
Multimodal models round, skip line items, or hallucinate totals.

**How to avoid:**
Code gate with VND integer tolerance (0 or 1 dong). Fail → draft, never append.

**Warning signs:**
Prompt text like "verify the math yourself".

**Phase to address:**
Phase 2.

---

### Pitfall 4: Expired Gmail watch

**What goes wrong:**
Demo day: no events. Watch lasts ~7 days and must be renewed.

**Why it happens:**
Docs: call `watch` at least every 7 days; recommend daily.

**How to avoid:**
Cloud Scheduler job to renew `users.watch`. Document in README spin-up.

**Warning signs:**
`expiration` in the past; silent inbox.

**Phase to address:**
Phase 1.

---

### Pitfall 5: Chat UI as the happy path

**What goes wrong:**
Judges classify the project as a chatbot. 40% autonomy score collapses.

**Why it happens:**
Upload widgets are faster to build than Gmail OAuth.

**How to avoid:**
Demo script starts at Send in Gmail. Any UI is a Run viewer.

**Warning signs:**
README "run `python parse.py --image`".

**Phase to address:**
Phase 3 demo.

---

### Pitfall 6: Disqualifying stack leftover in docs

**What goes wrong:**
README still says Gemini 1.5 + Function Calling. Judges read docs first.

**Why it happens:**
Old root `PROJECT.md` / `README.md` were written as a finished submission.

**How to avoid:**
Root README + `.planning/PROJECT.md` are the only stack story. 1.5 language is gone.

**Warning signs:**
The string `1.5 Flash` anywhere in the repo.

**Phase to address:**
Initialization (this research set).

---
*Research completed: 2026-08-25*
