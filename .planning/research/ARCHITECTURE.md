# Architecture Research

**Domain:** Event-driven VAT invoice → ledger agent
**Researched:** 2026-08-25
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
Gmail (dedicated inbox)
        │  users.watch
        ▼
Pub/Sub topic  ──push (OIDC)──►  Cloud Run (ADK runtime)
                                      │
                          ┌───────────┴───────────┐
                          │  Model: Gemini 3.5    │  Plan JSON + confidence
                          │  (no Workspace tools) │
                          └───────────┬───────────┘
                                      ▼
                          ┌───────────────────────┐
                          │  Harness: code gates  │
                          │  + idempotent tools   │
                          └───────────┬───────────┘
                     pass │           │ fail / low conf / duplicate
                          ▼           ▼
                     Sheets       Gmail draft
                     (Posted)     (Needs review)
                          │
                          ▼
                     Firestore (Run state of record)
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| Ingest | Decode Pub/Sub, resolve Gmail history, fetch message + attachments | Cloud Run HTTP + Gmail API |
| Extractor | Fill Plan schema from image/PDF | ADK agent, Gemini 3.5, structured output |
| Gates | Schema, math, confidence, duplicate | Pure Python |
| Tools | Sheets append, Gmail draft create | Google APIs, keyed by message-id |
| Store | Run status, processed keys | Firestore |

## Recommended Project Structure

```
olympus-document-agent/
  CONTEXT.md
  CLAUDE.md
  docs/HARNESS.md
  docs/DEMO.md
  docs/adr/
  .planning/
  src/
    ingest/          # Pub/Sub HTTP, Gmail history
    extract/         # ADK agent, Plan schema
    gates/           # schema, math, confidence, idempotency
    tools/           # sheets_append, gmail_draft (harness-only)
    store/           # Firestore Run records
```

## Data flow

1. Gmail notifies Pub/Sub (`historyId` only — not the message body).
2. Runtime syncs history since last `historyId`, skips non-invoice noise.
3. For each new message-id: create Run `received`.
4. Model produces Plan. Runtime never lets the model invoke write tools.
5. Gates decide `posted` | `needs_review` | `skipped_duplicate`.
6. Tools execute at most one side-effect path; Firestore commit is the source of truth.

## Build order

1. Ingest + Firestore skeleton (prove event without Gemini)
2. Extract + gates (unit-test math with fixtures)
3. Tools + end-to-end demo script

## Sources

- Gmail push semantics (historyId, 7-day watch): https://developers.google.com/workspace/gmail/api/guides/push
- ADK Cloud Run: https://docs.cloud.google.com/run/docs/ai/build-and-deploy-ai-agents/deploy-adk-agent

---
*Research completed: 2026-08-25*
