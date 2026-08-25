# Olympus VAT Agent — product brief

Canonical project context lives in [.planning/PROJECT.md](.planning/PROJECT.md). This file is a short pointer so the repo root does not keep a disqualifying stack story.

- **Hackathon:** All Things Agentic — track **The Taskmaster**
- **Hero chore:** Vietnamese VAT invoice arrives in **Gmail** → harness posts **Google Sheets** or opens a **draft**
- **Model:** Gemini **3.5** Flash (or newer) — extract + confidence only
- **Runtime:** Google **ADK** on **Cloud Run**; **Pub/Sub**; **Firestore**
- **Contract:** [docs/HARNESS.md](docs/HARNESS.md)
- **Demo:** [docs/DEMO.md](docs/DEMO.md)

Supersedes the earlier draft that named Gemini 1.5 Flash, raw Function Calling, FastAPI-only, and business cards as co-equal features. Those are out of scope or forbidden for this submission.
