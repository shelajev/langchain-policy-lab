# Permission review

These entries record review decisions. Resolved hosts and provider credentials become access requests, not automatic grants; review the effective policy composed with your target runtime and existing host rules.
A row can be out-of-scope because another approved finding already covers that request. Deny without a resolved host records intent but creates no host deny rule. In particular, `optional-tracing` is informational: a hostname in its description is not a resolved host unless the answer supplies `hosts`.

| Resource | Decision | Reason / source |
| --- | --- | --- |
| optional-tracing: LangSmith: api.smith.langchain.com; LANGSMITH_API_KEY (off unless explicitly enabled) (agent.py:0) | deny | Tracing is disabled; no LangSmith network or key requested |
| scope-confirmation: Static inspection cannot prove complete permissions; confirm model, files, tracing and runtime resources (agent.py:0) | allow | Developer selects gemini-2.5-flash for synthetic ticket classification, with separate live budget approval; no files or other runtime resources needed |
| env-name: LANGSMITH_TRACING (agent.py:14) | deny | Keep LANGSMITH_TRACING false; tracing is not part of this task |
| dependency: langchain-core (pyproject.toml:5) | out-of-scope | Core dependency needs no additional runtime access |
| env-name: GEMINI_API_KEY (pyproject.toml:5) | out-of-scope | Use the GOOGLE_API_KEY proxy sentinel; no second Gemini credential needed |
| env-name: GOOGLE_API_KEY (pyproject.toml:5) | allow | Use GOOGLE_API_KEY as the SDK sentinel for the runtime-only google service binding; host must approve and bind it |
| provider-host: generativelanguage.googleapis.com (pyproject.toml:5) | allow | Only the selected Gemini API host is needed |
| provider-package: langchain-google-genai (pyproject.toml:5) | allow | Selected Gemini provider; no alternate provider or endpoint authorized |

Requested runtime allow: generativelanguage.googleapis.com. Requested runtime deny: (none). An allow request adds to composed policy rather than creating an exclusive allowlist.

Excluded from the snapshot by policy: .env/.env.* (except .env.example), private/, VCS/venv/cache directories, and key or credential files; additional project ignore rules also apply.

Broad/IP access: none

## Launch ownership

This kit is a mixin, not a standalone workload. Docker's `shell` agent is the workload and owns the entrypoint, user, and session.
Inside the sandbox, launch from /opt/single-file-agent-kit/app: `/opt/single-file-agent-kit/venv/bin/python agent.py` (see RUN.md).

## Credentials

- Service `google`; runtime only, optional; placeholder env `GOOGLE_API_KEY`; header `x-goog-api-key`; domain `generativelanguage.googleapis.com`; format `%s`.

## What this does not protect

Static inspection is incomplete: denied or out-of-scope findings do not prove a capability is absent in code or dependencies.
No install-phase network is requested; image builds still download locked dependencies.
Other kits and host policy affect the effective boundary, and allow requests do not override broader inherited grants. Allowed services can incur costs, store data, or cause external side effects.
Sandbox isolation does not solve prompt injection or answer correctness. Cloud sandboxes need separate secrets and policy, and proxy header injection applies only to supported matching requests.
Builds, Docker kit conformance checks (`kit-tck`), and ordinary container runs are not evidence of local or cloud SBX runtime confinement.
