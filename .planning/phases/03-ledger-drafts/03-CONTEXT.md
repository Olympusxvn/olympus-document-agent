# Phase 3: Ledger, drafts, demo - Context

**Status:** Implemented in repo
**Source:** ROADMAP Phase 3 + docs/HARNESS.md

## Phase Boundary

Harness appends Google Sheets on gate pass (`posted`). Harness creates a Gmail draft on gate fail (`needs_review`). Duplicate identities skip both. `messages.send` is forbidden. ADK `tools=[]`.

## Locked

- ADC for Gmail + Sheets scopes
- Share the spreadsheet with the Cloud Run runtime SA
- Demo film follows docs/DEMO.md
