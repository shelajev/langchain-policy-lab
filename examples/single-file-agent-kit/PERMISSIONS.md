# Permission review

Capabilities are host requests, not grants. Review the target runtime's effective composition.

| Resource | Decision | Reason / source |
| --- | --- | --- |
| LangSmith: api.smith.langchain.com; LANGSMITH_API_KEY (off unless explicitly enabled) (agent.py:0) | deny | Tracing is disabled; no LangSmith network or key requested |
| Static inspection cannot prove complete permissions; confirm model, files, tracing and runtime resources (agent.py:0) | allow | Developer selects gemini-2.5-flash for synthetic ticket classification, with separate live budget approval; no files or other runtime resources needed |
| LANGSMITH_TRACING (agent.py:14) | deny | Keep LANGSMITH_TRACING false; tracing is not part of this task |
| langchain-core (pyproject.toml:5) | out-of-scope | Core dependency needs no additional runtime access |
| GEMINI_API_KEY (pyproject.toml:5) | out-of-scope | Use the GOOGLE_API_KEY proxy sentinel; no second Gemini credential needed |
| GOOGLE_API_KEY (pyproject.toml:5) | allow | Use GOOGLE_API_KEY as the SDK sentinel for the runtime-only google service binding; host must approve and bind it |
| generativelanguage.googleapis.com (pyproject.toml:5) | allow | Only the selected Gemini API host is needed |
| langchain-google-genai (pyproject.toml:5) | allow | Selected Gemini provider; no alternate provider or endpoint authorized |

Runtime allow: generativelanguage.googleapis.com. Runtime deny: (none).

Excluded by policy: .env/.env.* (except .env.example), private/, VCS/venv/cache directories, keys and credential files; additional project ignore rules apply.

Broad/IP access: none

## Launch ownership

This is a mixin, not a workload. Docker's `shell` agent is the workload and owns entrypoint, user and session.
Launch from /opt/single-file-agent-kit/app: `/opt/single-file-agent-kit/venv/bin/python agent.py` (see RUN.md).

## What this does not protect

Static inspection is incomplete. Denied/out-of-scope findings are not proof of absence.
No install-phase network is requested; image builds still download locked dependencies.
Other kits and host policy affect the effective boundary. Allowed services can incur costs, store data or have side effects.
Isolation does not solve prompt injection or answer correctness. Cloud needs separate secrets and policy.
Build/TCK/container checks are not local or cloud SBX runtime confinement evidence.
