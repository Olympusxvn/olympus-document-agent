# Feature Research

**Domain:** Event-driven VAT invoice → ledger agent
**Researched:** 2026-08-25
**Confidence:** HIGH (scoped by grill + contest track language)

## Feature Landscape

### Table Stakes (Users Expect These)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Inbound without chat | Taskmaster is a workflow, not a bot | MEDIUM | Gmail watch |
| Structured extract from photo/PDF | The chore is messy camera shots | MEDIUM | Gemini 3.5 multimodal |
| Arithmetic audit | Posting a wrong total is worse than not posting | LOW | Code, not LLM |
| Ledger write | "Sends the right info to the right places" | MEDIUM | Sheets append |
| Failure visible to operator | Silent drop is unacceptable | LOW | Gmail draft |
| No double-write | Gmail push + retries will duplicate | MEDIUM | Idempotency keys |

### Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Harness vs Function Calling | Architectural Discipline 30% | MEDIUM | Model cannot call write tools |
| VN MST checksum | Offline catch of OCR typos | LOW | v1 if time; python-stdnum |
| Three-path demo (pass / math-fail / duplicate) | Judges see autonomy *and* restraint | LOW | Script in `docs/DEMO.md` |
| Firestore run log | Traceable reasoning + state | MEDIUM | Diagram is honest |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Chat upload UI as control plane | Easy to demo | Maps to Collaborative Partner; tanks 40% | State viewer only |
| Auto-send vendor email | "Full autonomy" | Irreversible; contest still wants HITL for money | Draft only |
| Business cards in the same agent | Old README | Two stories in 4 minutes | Out of scope v1 |
| Self-repair ROI crop loops | Old README | Extra Gemini spend, hard to demo | One re-extract if schema fail |
| Model Armor / Agent Registry | Enterprise track kit | Wrong track; burns calendar | Skip |

## Feature Dependencies

```
Gmail watch
  └──requires──> Pub/Sub + Cloud Run
Plan extract
  └──requires──> Gemini 3.5 + typed schema
Code gates
  └──requires──> Plan extract
Sheets append / Gmail draft
  └──requires──> Code gates + Firestore idempotency
Demo video
  └──requires──> All of the above + Console proof
```

---
*Research completed: 2026-08-25*
