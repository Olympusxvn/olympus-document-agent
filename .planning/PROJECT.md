# Olympus VAT Agent

## What This Is

An event-driven Taskmaster agent for the All Things Agentic Hackathon. A dedicated Gmail inbox receives Vietnamese VAT invoices (photo or PDF); Gemini 3.5 extracts a structured plan; a deterministic harness validates math and schema in code, then either appends a Google Sheets row or creates a Gmail draft for human review. The human never chats to run the workflow.

## Core Value

A VAT invoice that arrives in Gmail becomes a posted Sheets row without a chat turn — or is blocked from writing when math, schema, or confidence fails.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Gmail watch (Pub/Sub push, Scheduler poll fallback) starts a run with no chat
- [ ] Gemini 3.5 extracts invoice JSON + confidence only — never calls Workspace APIs
- [ ] Code gates: required schema, `subtotal + vat == total`, confidence threshold, idempotency
- [ ] Pass → append Google Sheets; fail / low-confidence → Gmail draft, no Sheets write, never send
- [ ] Firestore persists state machine; crash/retry does not double-append
- [ ] Demo proves GCP (Cloud Run / Pub/Sub / Vertex or Gemini logs) plus pass / math-fail / duplicate

### Out of Scope

- Business cards / Google Contacts — splits the 4-minute demo; not the hero chore
- Sending email to vendors — v1 drafts only
- ERP / SAP / QuickBooks / HubSpot — 6-day deadline
- Multi-page tax PDF batches — one invoice per message
- Full HITL dashboard — Gmail draft is the review surface
- Model-owned Function Calling to Sheets/Gmail — violates the harness contract
- Universal OCR for every country — one Vietnamese VAT schema

## Context

Hackathon: All Things Agentic (deadline 31 Aug 2026 17:00 PT). Track: **The Taskmaster**. Judges: 40% autonomous operational utility, 30% architectural discipline, 30% demo + GCP proof.

Official Taskmaster language is event-driven coordination (watch a change, finish the job without guiding each step). Chat/upload UIs map to Collaborative Partner. Eligibility requires Gemini 3.5+, one Google agent framework (ADK), and one GCP service (Cloud Run + Pub/Sub + Firestore).

Philosophy (locked in grill): the model handles reasoning; the machine handles execution. Root `PROJECT.md` / `README.md` originally described Gemini 1.5 Flash + raw Function Calling + business cards — that stack is disqualifying and is superseded by this document.

Hero user: the builder's own dedicated inbox for Vietnamese VAT invoices (SME/admin chore they actually have).

## Constraints

- **Timeline**: ~6 days to submission (31 Aug 2026 17:00 PT) — coarse roadmap, sequential execution
- **Tech stack**: Gemini 3.5 Flash (or newer) via Gemini API or Vertex AI; Google ADK Python; Cloud Run; Pub/Sub; Firestore; Gmail API; Sheets API
- **Eligibility**: Must show GCP in the demo video (Console, Cloud Run URL, Vertex/Gemini logs)
- **Budget**: $150 GCP credits; scale-to-zero Cloud Run; Flash not Pro unless extract quality forces it
- **Security**: Dedicated Gmail, not a personal inbox; secrets in env/Secret Manager; never commit `credentials.json`
- **New project**: Work must be built during the contest window; disclose any reused templates

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Taskmaster, not Collaborative Partner | Official track wants event-driven action, not chat | — Pending |
| Gmail watch as trigger | Matches Taskmaster examples (inbox → other apps) | — Pending |
| VAT invoice as hero chore | Math-in-code is the visible harness proof | — Pending |
| Auto-append iff math + schema pass | Autonomy without posting garbage numbers | — Pending |
| Fail / low-confidence → draft only | HITL without a chat control plane | — Pending |
| Never send outbound mail | Side-effect blast radius | — Pending |
| Gemini extracts; harness executes tools | Architectural Discipline 30%; ADK idempotency webinar | — Pending |
| Idempotency (message-id + MST + số HĐ) in v1 | Duplicate Gmail deliveries are guaranteed | — Pending |
| ADK + Cloud Run + Pub/Sub + Firestore | Eligibility + scale-to-zero | — Pending |
| Business cards out of v1 | One 4-minute story | — Pending |
| MST checksum if time (not demo-blocking) | Cheap VN differentiator | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-08-25 after initialization*
