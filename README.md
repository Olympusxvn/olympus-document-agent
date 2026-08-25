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
gcloud config set project olympus-vat-agent
.\scripts\gcp_setup.ps1
```

## Spin-up (Phase 1)

GitHub → Cloud Run is the deploy path. Gmail uses **Application Default Credentials** on the Cloud Run runtime service account. Do **not** set `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, or `GMAIL_REFRESH_TOKEN`.

Cloud Run **Variables & Secrets** — keep:

- `GOOGLE_CLOUD_PROJECT` = `olympus-vat-agent`
- `GMAIL_ADDRESS` = mailbox to watch (Workspace user; impersonated when the runtime SA has domain-wide delegation)
- `GMAIL_PUBSUB_TOPIC` = `projects/olympus-vat-agent/topics/gmail-vat`
- `INGEST_TOKEN` = shared secret for `/internal/*`

Delete the three OAuth variables, then **Deploy**.

The runtime service account needs Gmail API access (org policy: ADC / IAM, not API keys). Grant Gmail scopes to that SA in Google Workspace Admin if the inbox is a user mailbox.

Pub/Sub push: `https://olympus-document-agent-78140974757.asia-southeast1.run.app/pubsub`

Daily: `POST /internal/watch-renew` with header `X-Ingest-Token` (watch expires in ~7 days). Fallback: Scheduler `POST /internal/poll`.

Local tests: `python -m pytest tests -q`.

## Out of scope for v1

Business cards, Google Contacts, sending email, ERP connectors, chat-as-trigger.

## License

TBD by the contest submission.
