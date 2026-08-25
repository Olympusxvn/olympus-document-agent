# Model reasons, machine executes

Gemini 3.5 produces a structured Plan (extract + confidence). The Harness owns schema/math/confidence/idempotency gates and is the only caller of Sheets append and Gmail `drafts.create`. Write tools are not registered on the LLM agent.

**Status:** accepted

## Considered options

1. **ADK Function Calling / agent tools for Sheets and Gmail** — faster to copy from ADK samples; model would choose when to write. Rejected: fights the product philosophy, skips arithmetic as a hard gate, and double-writes on Gmail redelivery.
2. **Model verifies math in the prompt** — rejected: multimodal totals are unreliable; judges can check a sample invoice.
3. **This split (Plan JSON + code gates + harness tools)** — chosen for Taskmaster Architectural Discipline and the ADK long-running/idempotency story.

## Consequences

- Extract agent tool list is empty (or read-only).
- `docs/HARNESS.md` is the contract; Phase 2 tests the gates without live Workspace.
- Demo must show a math-fail that does **not** append Sheets — that is the architecture, not a bug.
