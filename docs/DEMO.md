# Demo script (~4 minutes)

Phase 3 is implemented in code: pass → Sheets `Posted` row; math-fail → Gmail draft, no row; duplicate → no second row. Film unedited. Do not use chat to “run” the agent.

Goal: Taskmaster (event → other apps) + harness (pass writes, fail does not) + GCP proof.

## Prep (off camera)

- Dedicated Gmail signed in
- Demo Sheet `Posted` tab visible, empty of the three test invoices
- Cloud Console: Cloud Run service, Pub/Sub subscription, and Vertex AI or Gemini/API logs
- Three attachments:
  1. **Pass** — real-looking VN VAT invoice, numbers add up
  2. **Math-fail** — same layout, total off by a large amount
  3. **Duplicate** — same seller MST + số HĐ as (1), can be a forward of (1)

## Shot list

| Time | What | Say |
|------|------|-----|
| 0:00–0:25 | Title + problem | Vietnamese VAT photos sit in Gmail. Typing them into Sheets is the chore. This agent watches the inbox. |
| 0:25–0:50 | Architecture diagram | Gemini 3.5 extracts a Plan. Code checks math and schema. Only the harness writes Sheets or creates a draft. |
| 0:50–1:20 | **Pass** | Gmail: compose to dedicated inbox, attach pass invoice, Send. Do not open a chat. |
| 1:20–1:50 | **GCP proof** | Console: Cloud Run request / Pub/Sub delivery / Gemini or Vertex log for this Run. Point at `*.run.app` or log lines. |
| 1:50–2:20 | Sheets | New Posted row: số HĐ, MST, money, message-id. |
| 2:20–3:00 | **Math-fail** | Send math-fail invoice. Show **no** new Posted row. Open Gmail **Drafts** — operator draft lists the math gate. |
| 3:00–3:35 | **Duplicate** | Send duplicate identity. Sheet row count unchanged. |
| 3:35–4:00 | Close | Model reasons; machine executes. Never sent mail. Repo + README spin-up. |

## Spoken value line (use once)

“If the totals don’t add up, we refuse to write the ledger. Autonomy is finishing the chore — not inventing numbers.”

## Must appear on camera

- [ ] Gmail Send as the trigger (not `parse.py`, not an upload widget)
- [ ] Cloud Console proving GCP
- [ ] Sheets Posted row for pass
- [ ] Draft + no row for math-fail
- [ ] No second row for duplicate

## After recording

Turn Cloud Run min instances to 0 / stop unused services so credits survive judging. Hosted URL is optional; this video is the proof.

## Submission checklist (hackathon)

- [ ] ~4 min video following this script
- [ ] Architecture diagram (same split as the voiceover)
- [ ] Public or shared repo; README spin-up
- [ ] Optional: public blog/social with `#AllThingsAgenticHackathon`
