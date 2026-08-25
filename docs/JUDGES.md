# Judge setup: clone, install, test

English instructions for hackathon judges. You do **not** need our Gmail inbox or a Google Cloud project to verify the harness. The live Gmail → Cloud Run path is shown in the demo video ([docs/DEMO.md](DEMO.md)).

**What this repo is:** an event-driven Taskmaster agent. Gemini 3.5 proposes a Plan JSON. Python code gates math, schema, confidence, and duplicates. The ADK agent has `tools=[]` — the model cannot write Sheets or Gmail.

**What is live (Phase 3):** extract + code gates + harness writes. Pass → `posted` (Sheets, when `SHEETS_SPREADSHEET_ID` is set). Fail → `needs_review` (Gmail draft). Duplicate → `skipped_duplicate`. Unit tests use fake ledger/drafts and do not call Google APIs.

## 1. Prerequisites

- Git
- Python **3.12** or newer (`python --version`)
- pip

Google Cloud, Gmail OAuth client secrets, and API keys are **not** required for the tests below.

## 2. Clone and install

```bash
git clone https://github.com/Olympusxvn/olympus-document-agent.git
cd olympus-document-agent
python -m venv .venv
```

Activate the virtualenv:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Windows (Git Bash)
source .venv/Scripts/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`google-adk` is required to import `main.py` (Cloud Run). Unit tests for ingest, Plan parsing, and gates do not call Gemini or Gmail.

## 3. Run tests (required)

From the repo root, with the venv active:

```bash
python -m pytest tests -q
```

**Expected:** all tests in `tests/` pass.

If `google-adk` did not install, `tests/test_agent_stub.py` is skipped and the rest still pass. That skip is acceptable: the stub only asserts `tools=[]`.

What the tests prove without GCP:

| Test module | What judges should see |
|-------------|------------------------|
| `test_gates.py` | Schema / math (±1 VND) / confidence / duplicate identity |
| `test_pipeline.py` | Gate pass without ledger → `validated`; math fail → `needs_review`; duplicate → `skipped_duplicate` |
| `test_harness.py` | Pass + ledger → `posted` and one row; math-fail → draft, no row; duplicate → neither; no `messages.send` |
| `test_extract_retry.py` | One re-extract when invoice number or seller MST is empty |
| `test_handler.py`, `test_pubsub.py`, `test_watch.py` | Gmail ingest records `received`; Pub/Sub decode; watch body |
| `test_gmail_credentials.py` | ADC (`google.auth.default`) with Gmail + Sheets scopes, not OAuth client env vars |
| `test_agent_stub.py` | ADK agent has no Sheets/Gmail write tools |

You should **not** set `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, or `GMAIL_REFRESH_TOKEN`. Those are not part of this project.

## 4. Optional: local health check

This starts the ADK FastAPI app. `GET /health` does not need GCP. `GET /runs` talks to Firestore and will fail without credentials — that is expected on a laptop.

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8080
```

In another terminal:

```bash
curl http://127.0.0.1:8080/health
```

**Expected:** JSON with `"status":"ok"` and `"phase": 3. Locally `"sheets_configured"` is usually false.

Do not POST `/pubsub` against localhost unless you are mocking Gmail and Firestore. That path is for Pub/Sub push on Cloud Run.

## 5. Optional: hosted ingest (no clone)

Our deployed service (asia-southeast1):

`https://olympus-document-agent-78140974757.asia-southeast1.run.app`

```bash
curl https://olympus-document-agent-78140974757.asia-southeast1.run.app/health
```

**Expected:** `"status":"ok"` and `"phase": 3`. `"sheets_configured": true` after Cloud Run has `SHEETS_SPREADSHEET_ID`.

`GET /runs` lists recent Firestore Run documents when the service can reach Firestore. An empty `runs` list means no invoice has been ingested yet, not that the API is fake.

Sending a VAT invoice to our dedicated inbox is **not** part of local judging. Replay that flow from the demo video.

## 6. Optional: reproduce on your own GCP project

Only if you want to stand up the full Gmail watch yourself. This is **not** required to score the repo.

1. Create a GCP project. Enable Gmail API, Cloud Run, Pub/Sub, Firestore, Vertex AI, Google Sheets API.
2. Copy `.env.example` to `.env` (never commit `.env`).
3. Deploy with the Dockerfile (GitHub → Cloud Run, or `docker build` + Cloud Run).
4. Set Cloud Run env vars from `.env.example`, including `SHEETS_SPREADSHEET_ID`. Use **Application Default Credentials** on the runtime service account. Grant that SA Gmail, Sheets, and Vertex AI User. Share the spreadsheet with the SA.
5. Create topic `gmail-vat`, push subscription to `https://<your-service>/pubsub`.
6. Call `POST /internal/watch-renew` with `X-Ingest-Token`. Gmail `users.watch` expires in about 7 days.

## 7. What not to do

- Do not use chat, an upload widget, or a CLI to “run” an invoice. The product trigger is Gmail.
- Do not expect Sheets writes from unit tests — those use fakes. Live Posted rows need `SHEETS_SPREADSHEET_ID`.
- Do not register Sheets or Gmail write tools on the LLM agent.

## Architecture (short)

```
Gmail (dedicated inbox)
  → Pub/Sub
  → Cloud Run (Google ADK)
       ├─ Gemini 3.5: Plan JSON + confidence only
       └─ Harness (Python): gates → Sheets Posted or Gmail draft
  → Firestore Run: posted | needs_review | skipped_duplicate
```

Harness contract: [HARNESS.md](HARNESS.md). Domain terms: [CONTEXT.md](../CONTEXT.md). Diagram: [ARCHITECTURE.md](ARCHITECTURE.md).
