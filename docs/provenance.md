# Source and dependency provenance

This page documents the pinned kit specification, CI toolchain versions, Python application dependencies, and API metadata inspection scripts behind the [LangChain in Docker Sandboxes guide](run-your-langchain-in-docker-sandboxes.md). See [docs-team-handoff.md](docs-team-handoff.md) for the repository overview and [acceptance-handoff.md](acceptance-handoff.md) for the native sandbox runbook and historical host record.

## Pinned kit specification and CI tools

The specification, schemas, recipes, and environment example under [docs/references/](references/) are pinned copies from [Docker's sandbox-kit-spec](https://github.com/docker/sandbox-kit-spec) at commit `a1d110de252bcc3cb2fa6d47fe37137a1a328b97`, with the Apache-2.0 license retained at [references/LICENSE](references/LICENSE). Leave these pinned reference files unchanged.

`kit-tck` is built from `cmd/kit-tck` at that same pinned `sandbox-kit-spec` commit. The single-file composition probe uses `docker/sbx-kit-shell:1.0.0@sha256:367c9a4b3fd550f777e1d57cc53550afb4a1385055d79111acf6f996272ff6de`. These are reproducibility inputs, not evidence of a new native sandbox run.

CI pins `uv` 0.9.26, Go 1.26.8 (to build `kit-tck`), and BuildKit 0.29.0 (with Python 3.13.7 in clean-checkout runs). See [scripts/install-ci-tools.sh](../scripts/install-ci-tools.sh), [ci.yml](../.github/workflows/ci.yml), and [clean-checkout.sh](../scripts/clean-checkout.sh) for the exact version pins, container digests, and installer checksums.

## Python applications and model paths

All examples and `sample/` declare exact direct dependency pins in `pyproject.toml` and hashed public-PyPI artifacts in `uv.lock`. CI sets `UV_EXCLUDE_NEWER=P7D` when resolving dependencies. The committed single-file `uv.lock` records `exclude-newer-span = "P7D"`, and the generator carries that recorded option into the kit Dockerfile as `ENV UV_EXCLUDE_NEWER=P7D`; the app's `pyproject.toml` alone does not impose it on a fresh resolve. Checked-in lockfiles reflect recorded resolves rather than guaranteeing identical output if re-locked later against upstream PyPI. The kit generator preserves supplied application source and declared data and does not execute source during inspection.

- **Primary learning path (`examples/single-file-agent/` and `examples/single-file-agent-kit/`):** Uses `init_chat_model`, `FakeListChatModel`, and `langchain-google-genai`. Native and live proxy evidence covers Google (Gemini) only; OpenAI and Anthropic are covered only by descriptor and mapping unit checks.
- **Supporting `examples/ticket-triage/`:** Repo-only example packaging `src`, data files, and a dynamic URL. The [current CI contract](docs-team-handoff.md#continuous-integration-contract-current-revision) covers its tests and kit build/TCK/container layers. Earlier unlinked pass reports are historical only; consult the actual revision's CI result for current artifact evidence. Native sandbox and live model runs are unrun.
- **Supporting `sample/` (policy-lab sample):** Repo-only LCEL example using `RunnableLambda`, `ChatPromptTemplate`, `StrOutputParser`, `BaseChatModel`, `AIMessage`, `Document`, `tool`, and a token-overlap `BaseRetriever` (no FAISS or external vector database). Its offline model is deterministic and does not prove live model quality, sandbox network enforcement, or proxy credential injection. The current CI contract covers unit, eval, build, `kit-tck` and container checks; earlier unlinked reports add no broader artifact scope. Consult the actual revision's CI result. Native sandbox and live model runs are unrun.

All policy documents, tickets, incidents, and example endpoints in the repository are synthetic. Offline runs require no production credentials, customer records, or coding-agent logins.

## Inspecting API provenance for the policy-lab sample

[scripts/record-api-provenance.py](../scripts/record-api-provenance.py) targets the `sample/` environment (not the primary `single-file-agent` example). It imports LangChain, Pydantic, and the optional `langchain-google-genai` SDK (`ChatGoogleGenerativeAI`) to report installed implementation metadata and makes no live API calls.

This optional contributor check identifies the installed implementations behind the supporting sample's LangChain API examples; it is not needed to follow the primary kit tutorial. It prints JSON to stdout rather than creating a report file.

To run the reporter:

1. In `sample/`, install the locked environment with the optional Gemini extra: `uv sync --locked --managed-python --extra gemini`
2. From the repository root, run: `sample/.venv/bin/python scripts/record-api-provenance.py`

Expected JSON output keys:

- `apis`: list of records, each with `public_api`, `implementation_module`, `distribution`, `version`, `file`, `source_line`, and `file_sha256`.
- `provider_fields`: inspection of `ChatGoogleGenerativeAI.model_fields` for `model`, `temperature`, `max_retries`, `timeout`, and `max_output_tokens`, each mapping to `present` and `alias`.
