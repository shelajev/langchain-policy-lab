# Permission review

These entries record review decisions. Resolved hosts and provider credentials become access requests, not automatic grants; review the effective policy composed with your target runtime and existing host rules.
A row can be out-of-scope because another approved finding already covers that request. Deny without a resolved host records intent but creates no host deny rule. In particular, `optional-tracing` is informational: a hostname in its description is not a resolved host unless the answer supplies `hosts`.

| Resource | Decision | Reason / source |
| --- | --- | --- |
| dependency: httpx (pyproject.toml:6) | out-of-scope | Informational dependency or test-only evidence; no extra runtime access needed |
| dependency: langchain-core (pyproject.toml:6) | out-of-scope | Informational dependency or test-only evidence; no extra runtime access needed |
| env-name: GEMINI_API_KEY (pyproject.toml:6) | out-of-scope | Informational dependency or test-only evidence; no extra runtime access needed |
| env-name: GOOGLE_API_KEY (pyproject.toml:6) | out-of-scope | Duplicate provider evidence; the approved langchain-google-genai package decision already requests the Gemini host and GOOGLE_API_KEY credential. |
| provider-host: generativelanguage.googleapis.com (pyproject.toml:6) | out-of-scope | Duplicate provider evidence; the approved langchain-google-genai package decision already requests the Gemini host and GOOGLE_API_KEY credential. |
| provider-package: langchain-google-genai (pyproject.toml:6) | allow | Use Gemini to classify synthetic tickets only, with separately approved live budget |
| optional-tracing: LangSmith: api.smith.langchain.com; LANGSMITH_API_KEY (off unless explicitly enabled) (src/ticket_triage/app.py:0) | deny | Tracing is off; do not provision a LangSmith credential or network access |
| scope-confirmation: Static inspection cannot prove complete permissions; confirm model, files, tracing and runtime resources (src/ticket_triage/app.py:0) | allow | Confirmed synthetic data/tickets only, Gemini gemini-2.5-flash, no tracing, no status fetch, no webhook; static inference remains incomplete |
| env-name: LANGSMITH_TRACING (src/ticket_triage/app.py:20) | deny | Tracing is off; do not provision a LangSmith credential or network access |
| env-name: LANGCHAIN_TRACING_V2 (src/ticket_triage/app.py:21) | deny | Tracing is off; do not provision a LangSmith credential or network access |
| file-read: developer must confirm data paths (src/ticket_triage/app.py:23) | allow | Read synthetic ticket JSON from declared data/tickets only |
| dynamic-url: dynamic-url (src/ticket_triage/app.py:27) | deny | Status enrichment is disabled; name an exact host and review policy before enabling it |
| env-name: TRIAGE_STATUS_URL (src/ticket_triage/app.py:27) | deny | Status enrichment is disabled; name an exact host and review policy before enabling it |
| env-name: TRIAGE_MODEL (src/ticket_triage/chain.py:27) | allow | Developer selects gemini-2.5-flash; no alternate provider endpoint is authorized |
| dynamic-url: dynamic-url (src/ticket_triage/sources.py:6) | deny | Status enrichment is disabled; name an exact host and review policy before enabling it |
| literal-host: hooks.example.invalid (src/ticket_triage/sources.py:13) | deny | Webhook and test status endpoints must not receive ticket data |
| process-or-socket: socket (tests/test_app.py:2) | out-of-scope | Informational dependency or test-only evidence; no extra runtime access needed |
| file-read: developer must confirm data paths (tests/test_app.py:17) | out-of-scope | Informational dependency or test-only evidence; no extra runtime access needed |
| literal-host: status.example.invalid (tests/test_app.py:25) | deny | Webhook and test status endpoints must not receive ticket data |
| env-name: TRIAGE_STATUS_URL (tests/test_app.py:38) | deny | Status enrichment is disabled; name an exact host and review policy before enabling it |
| literal-host: status.example.invalid (tests/test_app.py:38) | deny | Webhook and test status endpoints must not receive ticket data |

Requested runtime allow: generativelanguage.googleapis.com. Requested runtime deny: hooks.example.invalid, status.example.invalid. An allow request adds to composed policy rather than creating an exclusive allowlist.

Excluded from the snapshot by policy: .env/.env.* (except .env.example), private/, VCS/venv/cache directories, and key or credential files; additional project ignore rules also apply.

Broad/IP access: none

## Credentials

- Service `google`; env `GOOGLE_API_KEY` (sentinel); header `x-goog-api-key`; domain `generativelanguage.googleapis.com`; format `%s`.

## Excluded files

- .env (always)
- key and credential files (always)
- private/ (always)

## What this does not protect

Static inspection is incomplete: denied or out-of-scope findings do not prove a capability is absent in code or dependencies.
Temporary scoped bootstrap network is requested separately in RUN.md; remove it before runtime.
The workload and host policy affect the effective boundary, and allow requests do not override broader inherited grants. Allowed services can incur costs, store data, or cause external side effects.
Sandbox isolation does not solve prompt injection or answer correctness. Cloud sandboxes need separate secrets and policy, and proxy header injection applies only to supported matching requests.
Builds, Docker kit conformance checks (`kit-tck`), and ordinary container runs are not evidence of local or cloud SBX runtime confinement.
