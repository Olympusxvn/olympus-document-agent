# Phase 1 research (ingest)

**Researched:** 2026-08-25

- Gmail push payload is `{ emailAddress, historyId }` (not the message). Sync with `users.history.list` then `users.messages.get`. Watch expires ~7 days; renew daily.
- Pub/Sub push to Cloud Run: OIDC invoker SA. Gmail must publish to the topic: `gmail-api-push@system.gserviceaccount.com`.
- ADK: `get_fast_api_app(agents_dir=..., web=False)` then add `/pubsub`. `web=True` can swallow custom routes.
- Phase 1 does not call the model. Agent is eligibility stub only.
