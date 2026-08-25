# Project Research Summary

**Project:** Olympus VAT Agent
**Domain:** Event-driven Vietnamese VAT invoice agent (Taskmaster / harness)
**Researched:** 2026-08-25
**Confidence:** HIGH

## Executive Summary

This is not an OCR chatbot. It is a Taskmaster workflow: Gmail changes fan in through Pub/Sub to a Cloud Run ADK runtime; Gemini 3.5 proposes a Plan; code decides whether Google Sheets may be written.

The stack is forced by contest eligibility (Gemini 3.5+, ADK, GCP) and by the grill: model reasons, machine executes. The main risks are at-least-once Gmail delivery (double append) and leftover 1.5/Function-Calling docs that would disqualify the story.

## Key Findings

### Recommended Stack

Gemini 3.5 Flash + ADK Python on Cloud Run, Gmail `users.watch` → Pub/Sub push, Firestore for Run state, Sheets append and Gmail drafts as the only side effects. Scheduler renews the 7-day watch and is the poll fallback.

**Core technologies:**
- Gemini 3.5 Flash: multimodal Plan — eligibility
- ADK + Cloud Run: required framework + infra, scale-to-zero
- Pub/Sub + Gmail API: event-driven trigger
- Firestore: source of truth for Posted / Needs review / Skipped duplicate

### Expected Features

**Must have (table stakes):**
- Watch inbox without a chat turn
- Code math + schema + confidence gates
- Sheets on pass; draft on fail; never send
- Idempotent writes

**Should have (competitive):**
- VN MST checksum in code
- Honest architecture diagram + Console proof in video

**Defer (v2+):**
- Business cards, Contacts, ERP, send-mail, HITL dashboard, ROI re-crop loops

### Architecture Approach

Split the ADK process: extractor has no write tools; harness owns gates and Google API clients. Gmail notifies with `historyId` only — the runtime must sync and then key work by `message-id`.

**Major components:**
1. Ingest — Pub/Sub HTTP, Gmail history sync
2. Extractor — Gemini 3.5 Plan
3. Harness — gates + Sheets/draft tools + Firestore

### Critical Pitfalls

1. **Function Calling writes** — model must not own Sheets/Gmail tools
2. **Idempotency trap** — at-least-once push + retries
3. **LLM arithmetic** — always code-check totals
4. **Expired watch** — renew daily
5. **Chat as happy path** — demo from Gmail Send
6. **Stale 1.5 docs** — already being replaced

## Implications for Roadmap

### Phase 1: Gmail ingest + Run store
**Rationale:** Prove event-driven path and GCP before spending Gemini budget.
**Delivers:** Watch → Cloud Run → Firestore `received`
**Addresses:** Ingest table stakes, watch renewal
**Avoids:** Expired watch, chat-first skeleton

### Phase 2: Extract + code gates
**Rationale:** Harness contract is the differentiator; unit-test without live Sheets.
**Delivers:** Plan schema, math/schema/confidence/idempotency gates
**Uses:** Gemini 3.5, pydantic
**Implements:** Extractor + gates

### Phase 3: Side effects + demo
**Rationale:** Visible Taskmaster proof and 30% demo score.
**Delivers:** Sheets Posted, Gmail draft Needs review, 4-minute script, architecture diagram
**Avoids:** Double append, send-mail

### Phase Ordering Rationale

- Ingest first so the trigger is real, not a CLI parser
- Gates before tools so we never append from an untested path
- Demo last so the video matches running GCP

### Research Flags

- **Phase 1:** Gmail push + Cloud Run OIDC is the fiddliest OAuth; budget a Scheduler poll fallback
- **Phase 2:** Confirm live `gemini-3.5-flash` model id on the chosen API (AI Studio vs Vertex)

Phases with standard patterns:
- **Phase 3:** Sheets append and draft create are well-documented

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Locked by contest + official Gmail/ADK/Run docs |
| Features | HIGH | Grill decisions |
| Architecture | HIGH | Harness split is explicit |
| Pitfalls | HIGH | ADK idempotency webinar + Gmail at-least-once |

**Overall confidence:** HIGH

### Gaps to Address

- Exact Gemini 3.5 model string on Vertex vs AI Studio: verify at first extract call
- MST checksum edge cases for pre-2010 codes: optional gate, fail-open to schema/math only if checksum disagrees with a known-good invoice

## Sources

### Primary (HIGH confidence)
- https://allthingsagentichackathon.devpost.com/ — eligibility, Taskmaster, judging
- https://developers.google.com/workspace/gmail/api/guides/push — watch, historyId, 7-day expiry
- https://cloud.google.com/run/docs/tutorials/pubsub — push to Cloud Run
- https://docs.cloud.google.com/run/docs/ai/build-and-deploy-ai-agents/deploy-adk-agent — ADK on Run

### Secondary (MEDIUM confidence)
- Gera Tools / python-stdnum `stdnum.vn.mst` — MST check digit
- Hackathon webinar topics (long-running ADK, idempotency trap) — design emphasis

---
*Research completed: 2026-08-25*
*Ready for roadmap: yes*
