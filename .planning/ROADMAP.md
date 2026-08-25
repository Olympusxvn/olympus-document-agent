# Roadmap: Olympus VAT Agent

## Overview

Ship a Taskmaster demo in three coarse phases: prove Gmail→Cloud Run→Firestore without a chatbot; lock the harness so Gemini never writes; then attach Sheets/drafts and film the three-path video with GCP proof.

## Phases

- [ ] **Phase 1: Gmail ingest** - Event-driven Run records on Cloud Run with no chat trigger
- [ ] **Phase 2: Extract and gates** - Gemini 3.5 Plans plus code-only permission to write
- [ ] **Phase 3: Ledger, drafts, demo** - Posted Sheets, Needs review drafts, 4-minute script

## Phase Details

### Phase 1: Gmail ingest
**Goal**: A message in the dedicated inbox creates a Firestore Run without anyone chatting.
**Depends on**: Nothing (first phase)
**Requirements**: INGEST-01, INGEST-02, INGEST-03, INGEST-04, STATE-01, ELIG-01
**Success Criteria** (what must be TRUE):
  1. Sending mail to the dedicated inbox results in a Cloud Run invocation (Pub/Sub push, or Scheduler poll fallback)
  2. A Firestore document exists for the Gmail message-id with status `received`
  3. `users.watch` is renewed on a schedule; README documents the 7-day expiry
  4. The service is an ADK app on Cloud Run (even if extract is stubbed)
**Plans**: 2 plans
**UI hint**: no

Plans:
- [ ] 01-01: Cloud Run ADK skeleton, Firestore Run schema, secrets
- [ ] 01-02: Gmail watch + Pub/Sub push (Scheduler poll fallback) + watch renewal

### Phase 2: Extract and gates
**Goal**: Every Plan is gated in code; the model cannot call Workspace write APIs.
**Depends on**: Phase 1
**Requirements**: EXTRACT-01, EXTRACT-02, EXTRACT-03, GATE-01, GATE-02, GATE-03, GATE-04, STATE-02
**Success Criteria** (what must be TRUE):
  1. A fixture image produces a typed Plan from Gemini 3.5 with a confidence score
  2. Unit tests fail GATE-01/02/03 without touching Sheets
  3. Duplicate message-id or (MST, số HĐ) after Posted is `skipped_duplicate` in tests
  4. Agent definition exposes no Sheets/Gmail write tools to the model
**Plans**: 2 plans
**UI hint**: no

Plans:
- [ ] 02-01: Plan schema + Gemini 3.5 extract (one re-extract on schema miss)
- [ ] 02-02: Code gates + Firestore status transitions + idempotency tests

### Phase 3: Ledger, drafts, demo
**Goal**: Visible side effects and a judge-proof video.
**Depends on**: Phase 2
**Requirements**: EXEC-01, EXEC-02, EXEC-03, ELIG-02, DEMO-01, DEMO-02, DEMO-03
**Success Criteria** (what must be TRUE):
  1. Valid invoice email → one new Posted row in the demo Sheet
  2. Wrong-total invoice email → Gmail draft, no new Posted row
  3. Duplicate invoice identity → no second Posted row
  4. Demo video can show Cloud Console (Run / Pub/Sub / Gemini or Vertex logs)
**Plans**: 2 plans
**UI hint**: no

Plans:
- [ ] 03-01: Harness tools — Sheets append, Gmail draft, never send
- [ ] 03-02: Architecture diagram, README spin-up, film `docs/DEMO.md`

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Gmail ingest | 0/2 | Not started | - |
| 2. Extract and gates | 0/2 | Not started | - |
| 3. Ledger, drafts, demo | 0/2 | Not started | - |

---
*Last updated: 2026-08-25 after initialization*
