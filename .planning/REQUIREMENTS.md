# Requirements: Olympus VAT Agent

**Defined:** 2026-08-25
**Core Value:** A VAT invoice that arrives in Gmail becomes a posted Sheets row without a chat turn — or is blocked from writing when math, schema, or confidence fails.

## v1 Requirements

### Ingest

- [ ] **INGEST-01**: Dedicated Gmail inbox notifies the runtime when new mail arrives, without a chat or upload UI as the trigger
- [ ] **INGEST-02**: Runtime receives Gmail changes via Pub/Sub push to Cloud Run (Scheduler poll of a label is the documented fallback)
- [ ] **INGEST-03**: Runtime renews `users.watch` on a schedule so the watch does not expire during the contest window
- [ ] **INGEST-04**: Runtime fetches the message and invoice image/PDF from Gmail and records a Run as `received` in Firestore

### Extract

- [ ] **EXTRACT-01**: Gemini 3.5 (or newer) returns a typed Plan: invoice number, seller MST, date, subtotal, VAT, total, confidence
- [ ] **EXTRACT-02**: The model has no Sheets or Gmail write tools — it only produces a Plan
- [ ] **EXTRACT-03**: If required fields are missing, the runtime may re-extract once; it does not loop on ROI crops

### Gates

- [ ] **GATE-01**: Missing required Plan fields fails the Run — no Sheets append
- [ ] **GATE-02**: `subtotal + vat_amount` must equal `total` in VND (tolerance 0 or 1 dong) in code — no Sheets append on fail
- [ ] **GATE-03**: Confidence below threshold fails the Run — no Sheets append
- [ ] **GATE-04**: Duplicate Gmail `message-id` or duplicate `(seller_mst, invoice_number)` after a Posted run is `skipped_duplicate` — no second Sheets row

### Execution

- [ ] **EXEC-01**: Math + schema + confidence pass → harness appends one Sheets row (Posted)
- [ ] **EXEC-02**: Fail or low-confidence → harness creates a Gmail draft to the operator explaining the gate; no Sheets append
- [ ] **EXEC-03**: The system never sends an email (`drafts.create` only)

### State and eligibility

- [ ] **STATE-01**: Firestore is the source of truth for Run status: `received` → `extracting` → `validating` → `posted` | `needs_review` | `skipped_duplicate`
- [ ] **STATE-02**: A crash or Pub/Sub retry after Posted does not append a second row
- [ ] **ELIG-01**: The running service uses Google ADK and is deployed on Cloud Run
- [ ] **ELIG-02**: Demo video shows GCP proof (Cloud Run, Pub/Sub, and/or Vertex/Gemini logs)

### Demo

- [ ] **DEMO-01**: Operator can complete the pass path: send a valid VAT invoice to the dedicated inbox and see a new Sheets row
- [ ] **DEMO-02**: Operator can complete the math-fail path: send an invoice with a wrong total and see a Gmail draft, no new Posted row
- [ ] **DEMO-03**: Operator can complete the duplicate path: resend the same invoice identity and see no second Posted row

## v2 Requirements

### Gates

- **GATE-05**: Code validates Vietnamese MST checksum (10-digit Mod 11; 13-digit = parent + branch). Not demo-blocking.

### Product

- **CARD-01**: Business card extract → Google Contacts
- **EXEC-04**: Human reply on the review draft promotes a Needs review Run to Posted
- **INGEST-05**: Drive folder watch as a second trigger
- **BATCH-01**: Multi-page PDF tax packs

## Out of Scope

| Feature | Reason |
|---------|--------|
| Chat/upload as the way to run the workflow | Collaborative Partner, not Taskmaster |
| Gemini 1.5 / raw Function Calling writes | Disqualifies eligibility and harness contract |
| Sending mail to vendors | Irreversible; v1 drafts only |
| SAP / QuickBooks / HubSpot | 6-day calendar |
| Full HITL web dashboard | Draft is the review surface |
| Agent Registry / Model Armor / GEAP fleet kit | Fortified Enterprise Fleet track, not Taskmaster |
| Universal non-VN invoice schemas | One hero schema |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| INGEST-01 | Phase 1 | Pending |
| INGEST-02 | Phase 1 | Pending |
| INGEST-03 | Phase 1 | Pending |
| INGEST-04 | Phase 1 | Pending |
| STATE-01 | Phase 1 | Pending |
| ELIG-01 | Phase 1 | Pending |
| EXTRACT-01 | Phase 2 | Pending |
| EXTRACT-02 | Phase 2 | Pending |
| EXTRACT-03 | Phase 2 | Pending |
| GATE-01 | Phase 2 | Pending |
| GATE-02 | Phase 2 | Pending |
| GATE-03 | Phase 2 | Pending |
| GATE-04 | Phase 2 | Pending |
| STATE-02 | Phase 2 | Pending |
| EXEC-01 | Phase 3 | Pending |
| EXEC-02 | Phase 3 | Pending |
| EXEC-03 | Phase 3 | Pending |
| ELIG-02 | Phase 3 | Pending |
| DEMO-01 | Phase 3 | Pending |
| DEMO-02 | Phase 3 | Pending |
| DEMO-03 | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 21 total
- Mapped to phases: 21
- Unmapped: 0

---
*Requirements defined: 2026-08-25*
*Last updated: 2026-08-25 after initialization*
