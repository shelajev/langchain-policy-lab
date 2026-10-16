# An existing ticket-triage app

This app has no Sandbox API dependency. It reads one synthetic support ticket,
uses LangChain to return a validated ticket ID, category and summary, and prints
JSON. `--fake-model` is deterministic and makes no model/tracing calls. Status
fetches and webhook posts require separate flags, even in fake mode.

```bash
uv sync --locked
uv run --locked --offline python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model
```

For a separately approved live run, set `TRIAGE_MODEL=gemini-2.5-flash` and supply
`GOOGLE_API_KEY` or `GEMINI_API_KEY` through the approved runtime credential path,
then omit `--fake-model`. This incurs provider usage. Do not commit `.env` or
load secrets into the image. The app does not automatically read `.env`.

`--status` reads `TRIAGE_STATUS_URL`; `--post-webhook` posts to
`hooks.example.invalid`, an intentionally non-operational, denied example.
Tracing is optional through LangChain's `LANGSMITH_TRACING` /
`LANGSMITH_API_KEY` environment names; the worked Sandbox policy leaves it off.
The fake output tests pipeline wiring, not real-model answer quality.

See the [packaging guide](../../docs/user-guide.md) for the reviewed snapshot
and the [runtime handoff](../../docs/acceptance-handoff.md) for unrun checks.
