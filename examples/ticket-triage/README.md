# An existing ticket-triage app

This second example builds on the single-file layout to show a packaged `src/`
app (`ticket_triage.app`) with local data files (`data/tickets/`), a runtime
status URL, an intentionally denied webhook, and optional tracing.

The app has no Sandbox API dependency. It reads one synthetic support ticket,
uses LangChain to return a validated ticket ID, category and summary, and prints
JSON. `--fake-model` is deterministic and makes no model or tracing calls.
Status fetches and webhook posts require separate flags, even in fake mode.

Run from `examples/ticket-triage/` on the host:

```bash
uv sync --locked
uv run --locked --offline python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model
```

The fake result has the input ticket ID, category `technical` and a fixed
synthetic summary. For the bundled `T-101` fixture, the expected JSON is
`{"category": "technical", "summary": "Synthetic offline classification; investigate the reported issue.", "ticket_id": "T-101"}`.
This checks pipeline, data-loading and schema validation, not real-model
answer quality. The optional HTTP flags below are inspection cases, not
additional worked runtime exercises.

The commands above are a local fake-model check. Live operation is documented
here through the [generated sandbox kit](../ticket-triage-kit/RUN.md), whose
reviewed launch also selects `--fake-model`.

For a separately approved live variant in that sandbox, bind the `google`
secret on the host, then run the app in the guest without `--fake-model`.
The app defaults to `gemini-2.5-flash`; setting `TRIAGE_MODEL` in the guest is
optional and overrides that default within the authorized Gemini provider endpoint.
Alternate endpoints require a new access review. The kit does not bake in this model
variable. Its `GOOGLE_API_KEY` placeholder is resolved by the sandbox proxy,
separate from your coding agent's account. A direct host live run would need
its own approved process credential environment; the sandbox placeholder does
not configure that host process.
This incurs provider usage. Do not commit `.env` or load secrets into the
image; the app does not automatically read `.env`.

## Access review and policy boundaries

- `--status` reads `TRIAGE_STATUS_URL`, which exercises how runtime-constructed
  URLs require an explicit host decision in the kit-generation answers file (the JSON
  record of reviewed allow/deny decisions). `tests/test_app.py` supplies the
  synthetic test host `status.example.invalid`.
- `--post-webhook` posts to `hooks.example.invalid`, an intentionally
  non-operational, denied example.
- Tracing is optional through LangChain's `LANGSMITH_TRACING` /
  `LANGSMITH_API_KEY` environment names; the worked Sandbox policy in
  `examples/ticket-triage-kit/` leaves it off.

When reviewing the generated kit, remember that `allow` requests add to this
mixin without making the composed sandbox policy exclusive if other sandbox
grants exist, while explicit `deny` rules win over allows. The generated descriptor denies
`hooks.example.invalid` and `status.example.invalid`; tracing is left without
a grant, which is different from an explicit host deny.

See the [packaging guide](../../docs/user-guide.md) for the reviewed snapshot.
The [validation summary](../../docs/acceptance-handoff.md) records native
checks of the single-file kit; it does not establish native acceptance of this
ticket-triage example.
