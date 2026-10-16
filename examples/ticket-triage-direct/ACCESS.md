# Permission review

Capabilities are host requests, not grants. Review the target runtime's effective composition.

| Resource | Decision | Reason / source |
| --- | --- | --- |
| httpx (pyproject.toml:6) | out-of-scope | Informational dependency or test-only evidence; no extra runtime access needed |
| langchain-core (pyproject.toml:6) | out-of-scope | Informational dependency or test-only evidence; no extra runtime access needed |
| GEMINI_API_KEY (pyproject.toml:6) | out-of-scope | Informational dependency or test-only evidence; no extra runtime access needed |
| GOOGLE_API_KEY (pyproject.toml:6) | out-of-scope | Informational dependency or test-only evidence; no extra runtime access needed |
| generativelanguage.googleapis.com (pyproject.toml:6) | out-of-scope | Informational dependency or test-only evidence; no extra runtime access needed |
| langchain-google-genai (pyproject.toml:6) | allow | Use Gemini to classify synthetic tickets only, with separately approved live budget |
| LangSmith: api.smith.langchain.com; LANGSMITH_API_KEY (off unless explicitly enabled) (src/ticket_triage/app.py:0) | deny | Tracing is off; do not provision a LangSmith credential or network access |
| Static inspection cannot prove complete permissions; confirm model, files, tracing and runtime resources (src/ticket_triage/app.py:0) | allow | Confirmed synthetic data/tickets only, Gemini gemini-2.5-flash, no tracing, no status fetch, no webhook; static inference remains incomplete |
| LANGSMITH_TRACING (src/ticket_triage/app.py:20) | deny | Tracing is off; do not provision a LangSmith credential or network access |
| LANGCHAIN_TRACING_V2 (src/ticket_triage/app.py:21) | deny | Tracing is off; do not provision a LangSmith credential or network access |
| developer must confirm data paths (src/ticket_triage/app.py:23) | allow | Read synthetic ticket JSON from declared data/tickets only |
| dynamic-url (src/ticket_triage/app.py:27) | deny | Status enrichment is disabled; name an exact host and review policy before enabling it |
| TRIAGE_STATUS_URL (src/ticket_triage/app.py:27) | deny | Status enrichment is disabled; name an exact host and review policy before enabling it |
| TRIAGE_MODEL (src/ticket_triage/chain.py:27) | allow | Developer selects gemini-2.5-flash; no alternate provider endpoint is authorized |
| dynamic-url (src/ticket_triage/sources.py:6) | deny | Status enrichment is disabled; name an exact host and review policy before enabling it |
| hooks.example.invalid (src/ticket_triage/sources.py:13) | deny | Webhook and test status endpoints must not receive ticket data |
| socket (tests/test_app.py:2) | out-of-scope | Informational dependency or test-only evidence; no extra runtime access needed |
| developer must confirm data paths (tests/test_app.py:17) | out-of-scope | Informational dependency or test-only evidence; no extra runtime access needed |
| status.example.invalid (tests/test_app.py:25) | deny | Webhook and test status endpoints must not receive ticket data |
| TRIAGE_STATUS_URL (tests/test_app.py:38) | deny | Status enrichment is disabled; name an exact host and review policy before enabling it |
| status.example.invalid (tests/test_app.py:38) | deny | Webhook and test status endpoints must not receive ticket data |

Runtime allow: generativelanguage.googleapis.com. Runtime deny: hooks.example.invalid, status.example.invalid.

Excluded by policy: .env/.env.* (except .env.example), private/, VCS/venv/cache directories, keys and credential files; additional project ignore rules apply.

Broad/IP access: none

## Credentials

- Service `google`; env `GOOGLE_API_KEY` (sentinel); header `x-goog-api-key`; domain `generativelanguage.googleapis.com`; format `%s`.

## Excluded files

- .env (always)
- .pytest_cache
- .venv
- key and credential files (always)
- private/ (always)
- src/ticket_triage/__pycache__
- tests/__pycache__

## What this does not protect

Static inspection is incomplete. Denied/out-of-scope findings are not proof of absence.
Temporary scoped bootstrap network is requested separately in RUN.md; remove it before runtime.
The workload and host policy affect the effective boundary. Allowed services can incur costs, store data or have side effects.
Isolation does not solve prompt injection or answer correctness. Cloud needs separate secrets and policy; cloud cannot mount this local workspace.
Build/TCK/container checks are not local or cloud SBX runtime confinement evidence.
