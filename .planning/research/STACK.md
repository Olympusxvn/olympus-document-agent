# Stack Research

**Domain:** Event-driven document-to-ledger agent (Vietnamese VAT invoices)
**Researched:** 2026-08-25
**Confidence:** HIGH (eligibility locked by hackathon rules; versions checked against official docs)

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Gemini 3.5 Flash | `gemini-3.5-flash` (or newer) via Gemini API or Vertex AI | Multimodal extract + confidence | Contest **requires** Gemini 3.5+. Flash first; Pro only if extract quality fails. |
| Google ADK (Python) | current `google-adk` | Agent runtime, eval, Cloud Run deploy | Contest requires a Google agent framework. ADK is the documented Cloud Run path. |
| Cloud Run | scale-to-zero, min instances 0 | HTTPS runtime for Pub/Sub push | Contest requires a GCP infra service; scale-to-zero fits $150 credits. |
| Cloud Pub/Sub | Gmail topic + push subscription | Event-driven mailbox notifications | Official Gmail push uses Pub/Sub; maps to Taskmaster "watch a change". |
| Cloud Firestore | Native mode | Run state + idempotency keys | Survives Cloud Run scale-to-zero; cheaper than always-on SQL for this volume. |
| Gmail API | `users.watch` + messages + drafts | Inbound invoices + HITL drafts | Hero trigger. Watch expires ~7 days — renew daily via Scheduler. |
| Google Sheets API | spreadsheets.values.append | Posted ledger | Visible side-effect for the 4-minute demo. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `google-adk` | latest | Agent definition + deploy | Always |
| `google-cloud-firestore` | latest | State + locks | Always |
| `google-api-python-client` | latest | Gmail + Sheets | Always |
| `google-auth` / `google-auth-oauthlib` | latest | Dedicated-inbox OAuth | Local bootstrap + stored refresh token in Secret Manager |
| `pydantic` v2 | latest | Plan schema | Code gates consume a typed Plan |
| `python-stdnum` | latest (`stdnum.vn.mst`) | MST checksum | Optional v1 if time; not demo-blocking |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Google Cloud Console | Demo proof | Video must show Run / Pub/Sub / Vertex or Gemini logs |
| `gcloud run deploy` / ADK Cloud Run tutorial | Deploy | Official: https://docs.cloud.google.com/run/docs/ai/build-and-deploy-ai-agents/deploy-adk-agent |
| Secret Manager | OAuth + API keys | Never commit `credentials.json` |
| Cloud Scheduler | Renew `users.watch` daily; poll fallback | Watch must be called at least every 7 days |

## Installation

```bash
python -m venv venv
# Windows: venv\Scripts\activate
pip install google-adk google-cloud-firestore google-api-python-client google-auth pydantic
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| ADK | Genkit / GenAI SDK / Antigravity | Only if ADK deploy blocks the calendar; still must be a listed Google agent framework |
| Pub/Sub push | Cloud Scheduler poll of Gmail | If `users.watch` + push OIDC eats too much of the 6 days |
| Firestore | Cloud SQL | Overkill for run records; keep SQL out of v1 |
| Gemini API | Vertex AI | Either satisfies rules; Vertex logs look stronger in a Console demo |

## What NOT to Use

- **Gemini 1.5 / 2.x as the billed model** — disqualifies the submission
- **Raw Gemini Function Calling as the write path** — model would own execution; violates harness contract
- **FastAPI-only without ADK** — misses required agent framework unless paired with Genkit/GenAI SDK
- **Always-on GKE / dedicated vector DB** — burns credits; not needed for one schema
- **Personal Gmail as the watch target** — noisy, unsafe, bad demo

## Sources

- Hackathon requirements: https://allthingsagentichackathon.devpost.com/
- Gmail push: https://developers.google.com/workspace/gmail/api/guides/push
- Pub/Sub → Cloud Run: https://cloud.google.com/run/docs/tutorials/pubsub
- ADK on Cloud Run: https://docs.cloud.google.com/run/docs/ai/build-and-deploy-ai-agents/deploy-adk-agent
- MST check digit: Gera Tools + python-stdnum `stdnum.vn.mst`

---
*Research completed: 2026-08-25*
