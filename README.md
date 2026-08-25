# Olympus VAT Agent

Event-driven Taskmaster agent for the [All Things Agentic Hackathon](https://allthingsagentichackathon.devpost.com/). Repo: [Olympusxvn/olympus-document-agent](https://github.com/Olympusxvn/olympus-document-agent). A dedicated Gmail inbox receives Vietnamese VAT invoices; **Gemini 3.5** proposes a structured Plan; a **harness** validates math and schema in code, then appends **Google Sheets** or creates a **Gmail draft**. The workflow does not start from chat.

**Track:** The Taskmaster  
**Core rule:** the model reasons; the machine executes. See [docs/HARNESS.md](docs/HARNESS.md) and [docs/adr/0001-model-reasons-machine-executes.md](docs/adr/0001-model-reasons-machine-executes.md).

## Eligibility stack

| Requirement | This project |
|-------------|--------------|
| Gemini 3.5 or newer | Gemini 3.5 Flash via Gemini API or Vertex AI |
| Google agent framework | Google ADK (Python) |
| GCP infrastructure | Cloud Run + Pub/Sub + Firestore |

Not used: Gemini 1.5, model-owned Function Calling to Workspace APIs, FastAPI as a substitute for ADK.

## What it does

1. `users.watch` on a dedicated inbox publishes to Pub/Sub (Cloud Scheduler poll is the fallback).
2. Cloud Run (ADK) loads the message and attachment.
3. Gemini 3.5 returns a Plan (fields + confidence) with **no write tools**.
4. Code gates: required schema, `subtotal + vat == total`, confidence threshold, idempotency (`message-id` and seller MST + số HĐ).
5. Pass → one Sheets row (`Posted`). Fail / low-confidence → Gmail **draft** to the operator. Duplicate → skip. The agent **never sends** mail.

Domain language: [CONTEXT.md](CONTEXT.md). Demo film: [docs/DEMO.md](docs/DEMO.md). Planning: [.planning/PROJECT.md](.planning/PROJECT.md).

## Architecture

```
Gmail (dedicated) → Pub/Sub → Cloud Run (ADK)
                                  ├─ Gemini 3.5: Plan JSON
                                  └─ Harness: gates → Sheets or draft
                         Firestore = Run source of truth
```

## Status

**Phase 1 (Gmail ingest) is in the repo.** Sending mail to the dedicated inbox should create a Firestore Run with status `received`. Extract, math gates, and Sheets writes are Phase 2–3 — the ADK agent is a stub with `tools=[]`.

`gcloud` was not on PATH in the build environment. You already have a Google Cloud **account**; install the [Cloud SDK](https://cloud.google.com/sdk/docs/install), then:

```powershell
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
.\scripts\gcp_setup.ps1 -ProjectId YOUR_PROJECT_ID
```

## Spin-up (Phase 1)

1. Copy `.env.example` to `.env`. Use a **dedicated** Gmail, not a personal inbox.
2. Create an OAuth desktop client (Gmail API). Then:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
$env:GMAIL_CLIENT_ID="..."
$env:GMAIL_CLIENT_SECRET="..."
python scripts/gmail_oauth.py
```

Put the printed refresh token in `.env` as `GMAIL_REFRESH_TOKEN`.

3. Enable APIs, Pub/Sub topic, Firestore, and Gmail publisher IAM via `scripts/gcp_setup.ps1`.
4. Deploy (min instances 0):

```powershell
gcloud run deploy olympus-vat-agent --source . --region asia-southeast1 --set-env-vars GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
```

5. Point a Pub/Sub **push** subscription at `https://SERVICE_URL/pubsub`.
6. Call `POST /internal/watch-renew` (header `X-Ingest-Token`) and schedule that job **daily**. Gmail `users.watch` **expires in about 7 days**; if you skip renewal, the inbox goes silent.
7. Fallback: Cloud Scheduler `POST /internal/poll` every minute if push is blocked.

Sheets env vars wait until Phase 3. Local tests: `python -m pytest tests -q`.

## Out of scope for v1

Business cards, Google Contacts, sending email, ERP connectors, chat-as-trigger.

## License

TBD by the contest submission.
