# Olympus VAT Agent

<!-- GSD:project-start source:PROJECT.md -->
## Project

Event-driven Taskmaster agent: dedicated Gmail receives Vietnamese VAT invoices; Gemini 3.5 proposes a Plan; a deterministic harness posts Google Sheets or creates a Gmail draft. Core value — a valid invoice becomes a Posted row without a chat turn; invalid math/schema/confidence must not write.

Planning: `.planning/PROJECT.md`. Domain terms: `CONTEXT.md`.
<!-- GSD:project-end -->

<!-- GSD:stack-start source:STACK.md -->
## Technology Stack

- Gemini 3.5 Flash (or newer) via Gemini API or Vertex AI — extract only
- Google ADK (Python) on Cloud Run
- Pub/Sub (Gmail `users.watch` push; Scheduler poll fallback)
- Firestore (Run state)
- Gmail API + Sheets API (harness-owned writes)
- Pydantic v2 for Plan parsing

Do not introduce Gemini 1.5 or register Sheets/Gmail write tools on the LLM agent.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

- Glossary in `CONTEXT.md` (Plan vs Harness vs Posted vs Needs review).
- Execution contract in `docs/HARNESS.md`.
- New architecture decisions in `docs/adr/` when they are hard to reverse.
- Money is integer VND; math is code, not prompt.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Gmail → Pub/Sub → Cloud Run ADK → Gemini Plan → code gates → Sheets (`posted`) or Gmail draft (`needs_review`) or no-op (`skipped_duplicate`). Firestore is source of truth. Details: `.planning/research/ARCHITECTURE.md`.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project-local skills yet.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work
- `/gsd-plan-phase 1` — next step after this initialization

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` — do not edit manually.
<!-- GSD:profile-end -->
