# Phase 1: Gmail ingest - Context

**Gathered:** 2026-08-25
**Status:** Ready for planning
**Source:** ROADMAP Phase 1 + user has a Google Cloud account (`gcloud` not on PATH yet)

## Phase Boundary

Deliver: a message in the dedicated inbox creates a Firestore Run (`received`) without a chat turn. The Cloud Run service is an ADK app. Extract/gates/Sheets are **out of this phase** (stub agent, empty tools).

## Locked decisions

- Trigger: Gmail `users.watch` → Pub/Sub push to Cloud Run; Scheduler poll is fallback
- Firestore is source of truth; Run id is sanitized RFC 5322 `Message-Id`
- ADK `root_agent` exists with **no write tools**; ingest does not invoke Gemini
- Dedicated inbox OAuth refresh token in env/Secret Manager — not a personal mailbox
- Custom HTTP routes on `get_fast_api_app(..., web=False)` so `/pubsub` is reachable

## Claude's discretion

- Region default `asia-southeast1`
- Scheduler auth: shared `INGEST_TOKEN` header for `/internal/*`
- If `gcloud` missing: ship deploy scripts; do not block unit tests

## Requirements

INGEST-01, INGEST-02, INGEST-03, INGEST-04, STATE-01, ELIG-01
