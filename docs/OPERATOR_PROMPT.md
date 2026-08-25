# Operator UI prompt (Agent Studio / Gemini app)

Do **not** paste this into Cloud Build. Cloud Build already deploys https://github.com/Olympusxvn/olympus-document-agent on push.

Paste the block below into the **Operator web app** (Vertex AI / Agent Studio / Gemini “build an app” chat) as a full rewrite.

---

```
REWRITE THIS APP. Replace the entire UI. Do not keep Vietnamese copy. Do not keep Phase 1 banners.

This Operator UI is a READ-ONLY viewer for the Olympus VAT Agent. It is NOT the Taskmaster runtime. It MUST NOT upload invoices, MUST NOT start a run from chat, MUST NOT call Sheets or Gmail write APIs.

Source of truth (public repo, already shipped Phase 3):
https://github.com/Olympusxvn/olympus-document-agent

Live ingest (asia-southeast1):
https://olympus-document-agent-78140974757.asia-southeast1.run.app

On load, fetch:
- GET {ingest}/health
- GET {ingest}/runs

Expected health JSON:
{"status":"ok","phase":3,"sheets_configured": true|false}

Expected /runs JSON:
{"phase":3,"runs":[{message_id, gmail_id, sender, received_at, status, attachment_ids, plan, gate_failures, seller_mst, invoice_number, sheet_row_id, draft_id, ...}]}

If health or /runs returns HTTP 403: do NOT say the pipeline is down. Show: “Ingest Cloud Run returned 403 — unauthenticated callers are denied (Cloud Run Invoker IAM). The backend may still be running. This Operator UI cannot process invoices.” If CORS fails, say CORS, not “service down”. If the list is empty, show an empty table — NEVER invent rows (no Initech, Acme, or fake KPIs).

LANGUAGE: 100% English. Every label, button, banner, empty state, chatbot greeting, placeholder, footer.

NAV
- Title: Olympus VAT Agent
- Tag: Operational Interface
- Links: Dashboard | Operational Assistant

DASHBOARD
Banner (info, not warning):
Title: PHASE 3 LIVE — extract, code gates, Sheets, drafts
Body: Pipeline is Gmail users.watch → Pub/Sub → Cloud Run (Google ADK). Gemini 3.5 Flash returns a Plan JSON + confidence only (ADK tools=[]). Python gates check schema, math (subtotal + VAT == total, ±1 VND), confidence (default 0.75), and duplicate (message-id and seller MST + invoice number). Pass → Google Sheets tab Posted (status posted). Fail → Gmail draft to the operator, never messages.send (status needs_review). Duplicate → skipped_duplicate, no second Sheets row. Manual upload and chat are not triggers.

If health.sheets_configured is false, add one line: “Sheets is not configured on Cloud Run yet (SHEETS_SPREADSHEET_ID missing). Gate pass stays validated until the spreadsheet id is set.”

Section: Pipeline overview
Subtitle: Monitoring Olympus VAT Agent (asia-southeast1)
Ingest status from /health: OK phase 3, or 403/CORS text as above.

Three metric cards (counts from /runs, not placeholders):
1. Received — count status == "received" (plus extracting/validating if you want an “in flight” note)
2. Posted to Sheets — count status == "posted" (also show validated if sheets_configured is false)
3. Needs review — count status == "needs_review"
Optional fourth: Skipped duplicate — count status == "skipped_duplicate"
Do NOT gray cards as “Phase 2 not available”. Phase 3 is in the repo.

Table: Recent runs
Caption: Live data from GET /runs (Firestore)
Columns: RUN ID (message_id) | TIME (received_at) | SENDER | STATUS | GATES (gate_failures join) | SHEET ROW | DRAFT ID
Empty: “No runs yet. Send a Vietnamese VAT invoice (photo or PDF) to the dedicated Gmail inbox. Do not use this UI to process invoices.”

STATUS MEANINGS (use in UI help and chatbot):
- received — ingest stored the Gmail message
- extracting — Gemini filling the Plan
- validating — code gates running
- validated — gates passed, Sheets id not configured
- posted — gates passed and Sheets append succeeded
- needs_review — schema, math, confidence, extract, or Sheets error; Gmail draft in Phase 3
- skipped_duplicate — same message-id already terminal, or same (seller_mst, invoice_number) already posted/validated

OPERATIONAL ASSISTANT (chat)
Read-only. Badge: Read-only
Title: Operational Assistant
Subtitle: Ask about pipeline status, architecture, or run statuses. This chat cannot process invoices.
Greeting:
“Hello. I am the Operational Assistant for Olympus VAT Agent. I explain the pipeline and Firestore run statuses. Architecture: dedicated Gmail → Pub/Sub → Cloud Run (ADK) → Gemini 3.5 Plan JSON → Python harness (schema, math, confidence, idempotency) → Google Sheets Posted or a Gmail draft. The model has no write tools. The system never sends email. Phase 3 is in the GitHub repo. How can I help?”
Placeholder: Ask about system status (e.g. “What is the current architecture?”)
Send button: Send
Footer: This interface cannot process invoices. It only explains pipeline status. Trigger is Gmail, not chat.

Chat answers must match the repo:
- Model reasons, machine executes
- Never Function Calling to Workspace APIs
- Never Gemini 1.5
- Region asia-southeast1 for ingest; Firestore may be nam5
- Judges clone https://github.com/Olympusxvn/olympus-document-agent and run: python -m pip install -r requirements.txt && python -m pytest tests -q
- Demo film: pass invoice → Posted row; wrong total → draft, no row; duplicate → no second row

Visual: keep the current dark navy header, white cards, light gray page. Professional, submission-ready, English only.

Publish/redeploy this Operator app after the rewrite.
```
