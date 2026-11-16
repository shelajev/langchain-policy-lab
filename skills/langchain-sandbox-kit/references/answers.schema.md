# Developer answers, version 1

The answers file is a JSON object with `name` (in lowercase-kebab form),
`decisions` and `launch`. Its optional `dataPaths` list defaults to empty. `decisions` must
map **every** finding ID from the current `inspect` report to an object with
`action` (`allow`, `deny`, or `out-of-scope`) and a non-empty `reason`. Extra or
stale IDs are rejected with exit code `2`. After source changes, inspect again
and re-review the answers: edits that leave findings unchanged can keep the same IDs.

Choose the action for the intended access, not merely because an item was found:

- `allow` approves the requested use. Resolved hosts become allow requests;
  an allowed provider-package can also request its mapped credential service.
- `deny` rejects the use. Resolved hosts become explicit host deny requests.
  Without resolved hosts, the decision is recorded but adds no network rule.
- `out-of-scope` records why the finding needs no separate request, for example
  duplicate evidence already covered by a provider-package decision.

For environment names, file-read findings and imports, these actions record
review decisions; they do not set environment values, copy files or disable
Python functions. `dataPaths` controls selected data copying. Secret-like
literals and unsafe or incomplete inputs still block generation regardless of
the action: `inspect` reports them for review; it does not make them safe.

Optional per-decision fields:

- `hosts`: lowercase hostnames, never full URLs. If you omit this field, a
  recognized provider-package decision uses its mapped host, and a literal-host
  or provider-host finding uses the detected host. This applies to both allow
  and deny decisions. Informational findings, such as optional tracing, do not
  resolve a host automatically. To allow a dynamic URL, name its exact hosts;
  a deny without resolved hosts records intent but adds no network deny.
- `credential`: the provider's `sbx secret set` service (`google`, `openai`, or
  `anthropic`), allowed only on an explicitly allowed provider-package decision
  whose resolved hosts include the provider's mapped exact host. You may omit
  `hosts` to use that default. If you supply hosts, the mapped host must remain
  in the list; other valid reviewed hosts can coexist but do not change where
  the credential is injected. Secret values are never accepted here. Because
  LangSmith has no built-in `sbx` secret service, the helper refuses a
  LangSmith credential.
- `allowBroad: true`: explicit opt-in for wildcard or IP hosts, paired with a
  reason. These exceptions are flagged in `PERMISSIONS.md`; prefer exact DNS
  hostnames whenever possible.

`dataPaths` lists the relative data or config files and directories the app
needs at runtime, copied in their original relative layout. Paths with `..`,
absolute paths, symlinks, and excluded private paths (such as `.env`) are
rejected. `launch` records a reviewed command for `RUN.md` and `agent-context@1`,
such as `python agent.py` or
`python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model`.
The launch must begin with `python`; shell expansions and redirections are
forbidden. Hooks, `lifecycle` and `sbx@1` are not accepted answers fields, and neither `decisions` nor any acknowledgement authorizes packaging
secret-like literals.

Example decision (replace the key with a real finding ID from `inspect`):

```json
{"action":"allow","reason":"Classify synthetic tickets using Gemini only","credential":"google"}
```

The supported lock format is intentionally narrower than arbitrary Python
projects: `uv.lock` with public PyPI hashes, exact direct pins in
`pyproject.toml`, and a mandatory exact `.python-version`. Projects that rely on `requirements.txt` alone, private registries,
VCS/path dependencies, or optional dependency groups need manual packaging. The
helper does not resolve dependencies or claim that static lock validation proves
the entire dependency graph; `uv sync --locked` during the image build checks
lock freshness independently.
