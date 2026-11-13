# Developer answers, version 1

JSON object: `name` (lowercase-kebab), `decisions`, `dataPaths`, `launch`.
`decisions` maps **every** current inspection finding ID to an object containing
`action` (`allow`, `deny`, `out-of-scope`) and a nonempty `reason`.
Extra/stale IDs are refused. Regenerate answers after source changes.

Optional per-decision fields:
- `hosts`: exact lowercase hostnames, never URLs. A provider-package decision
  defaults to that provider's documented host only when explicitly allowed.
  A literal-host decision uses its observed host. Dynamic URLs need named hosts.
- `credential`: the provider's `sbx secret set` service (`google`, `openai` or
  `anthropic`), only on an explicitly allowed provider-package decision with
  its exact host. No secret value is accepted. LangSmith has no built-in
  `sbx` secret service, so the helper refuses a LangSmith credential.
- `allowBroad: true`: explicit exception for wildcard/IP hosts, with a reason;
  flagged in PERMISSIONS.md. Prefer exact DNS hosts.

`dataPaths` lists required relative data/config files or directories, retaining layout.
No `..`, absolute paths, symlinks or excluded private paths. `launch` is a reviewed
simple command such as `python agent.py` or `python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model`.
No shell expansion, redirection, hooks, `lifecycle` or `sbx@1` fields are allowed.
Neither decisions nor acknowledgement authorize packaging secret-like literals.

Example decision (use real IDs from inspect):

```json
{"action":"allow","reason":"Classify synthetic tickets using Gemini only","credential":"google"}
```

Lock format is intentionally narrower than arbitrary Python projects: uv lock
plus exact direct pins and PyPI hashes. Requirements-only, custom registries,
VCS/path dependencies and optional dependency groups require manual packaging.
The helper does not resolve them or pretend that static lock validation proves
the full graph: `uv sync --locked` in the build checks freshness independently.
