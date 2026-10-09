# Primary source and API provenance

Collected inside this task sandbox on 2026-10-09. A version pin is a reproducible
input, not a claim that it is permanently the newest release. Distribution
metadata, file hashes and observed commands are in `evidence/`.

## Docker specification and authoring skill

- Official source: `https://github.com/docker/sandbox-kit-spec`, exact commit
  `a1d110de252bcc3cb2fa6d47fe37137a1a328b97`.
- Recovered from the existing Go module cache
  `github.com/docker/sandbox-kit-spec/v3@v3.0.0-m.8.0.20261008125117-a1d110de252b`;
  CI tool installation independently fetches and verifies the exact git commit.
- Archived unmodified in `references/`: `skills/create-kit-v3/SKILL.md`,
  `RECIPES.md`, `docs/spec/SPEC-v3.md`, agent-context capability reference,
  `schema/kit.schema.json`, agent-context/network/credential schemas and the
  official `sbxenv.yaml` example. `FIELD-MAPPING.md` is an applicable field
  reference recommended by the skill, not evidence of using migration.
  The target had no v2 kit, so migrate-kit-to-v3 was not executed.
- Archive SHA-256 values: `evidence/reference-hashes.txt`. Upstream license is
  preserved in `references/LICENSE`. Archived partial schemas retain upstream
  `$ref` paths: use the complete pinned upstream tree for standalone JSON-schema
  tooling; the authoritative local source check is the Docker frontend.
- Build frontend: `docker.io/docker/sandbox-kit:3`, observed index digest
  `sha256:e6a397771e865625047cf84256a914c7974b3e749d858259b5bc9c653ddb6f0d`,
  pinned in `langchain.yaml`. This is an official published frontend image;
  its source revision is not inferred to equal the skill pin.
- Artifact checker: kit-tck built from the exact skill/spec commit with Go
  **1.26.8**. The preexisting binary and independently built binary both report
  `dev (a1d110de)`; build metadata records the full commit. The upstream go.mod
  has a replace directive, so the CI script uses source checkout plus
  `go build -mod=readonly`, not the rejected `go install @commit` command.

## Python distribution inputs

Primary release metadata is the PyPI JSON API at
`https://pypi.org/pypi/<distribution>/<version>/json`. Exact snapshots in
`evidence/pypi-*.json` include Python constraints, dependency requirements,
upload timestamps and each wheel/sdist SHA-256. `sample/uv.lock` pins the entire
resolved graph with public download URLs, sizes and hashes.
The `build` dependency group additionally records hatchling's dependency
distributions; uv's verified `build-constraint-dependencies` setting pins
isolated PEP 517 builds to packaging 26.3, pathspec 0.12.1, pluggy 1.6.0 and
trove-classifiers 2026.9.21.13. These build tools are not kit runtime packages.

| Distribution | Pin | Purpose |
| --- | --- | --- |
| langchain | 1.4.4 | Tool API facade and installed orchestration toolkit |
| langchain-core | 1.6.9 | Documents, retriever, LCEL, prompt/chat/parser interfaces |
| pydantic | 2.14.0 | Typed tool bounds and structured output validation |
| langchain-google-genai | 4.4.0 | Optional sample provider; bundled in kit |
| pytest | 8.4.2 | Offline behavioral suite, not kit runtime |
| hatchling | 1.27.0 | Pinned project build backend |

No langchain-community dependency is needed: ingestion and lexical retrieval
use core interfaces directly. Direct versions in the planner draft were checked
against actual PyPI metadata and installed successfully; transitive versions
are the lock's values, not guessed lists.

Official source commits resolved from release refs:

- `https://github.com/langchain-ai/langchain` tag `langchain==1.4.4` resolves to
  `34489d61433cbf5044a630de2e7797e361672900`.
- The same repository's `langchain-core==1.6.9` resolves to
  `fc7dc7757a46ebb444be1ead0efdeab5ca7ad8ce`.
- `https://github.com/langchain-ai/langchain-google` tag `libs/genai/v4.4.0`
  resolves to `d38d42fdb540ce78205ac0e15e756f9ca831c26f`.

These source refs are context for the APIs; the installed distributions are
identified by their PyPI artifact hashes. Installed-source provenance is measured
directly by `scripts/record-api-provenance.py` and saved in
`evidence/api-provenance.json`, including relative implementation path, first
source line and full-file SHA-256 for each used API. In particular:

| Public API | Implementation in langchain-core 1.6.9 |
| --- | --- |
| `Document` | `langchain_core/documents/base.py` |
| `BaseRetriever` | `langchain_core/retrievers.py` |
| `RunnableLambda` | `langchain_core/runnables/base.py` |
| `ChatPromptTemplate` | `langchain_core/prompts/chat.py` |
| `BaseChatModel` | `langchain_core/language_models/chat_models.py` |
| `StrOutputParser` | `langchain_core/output_parsers/string.py` |
| `langchain.tools.tool` | re-export of `langchain_core/tools/convert.py` |

`ChatGoogleGenerativeAI` is in `langchain_google_genai/chat_models.py` 4.4.0.
The measured fields include `model`, `temperature`, `max_retries` (alias
`retries`), `timeout` (alias `request_timeout`), and `max_output_tokens`
(alias `max_tokens`). Optional package imports/field inspection are not live
provider validation. Official API navigation is
`https://reference.langchain.com/python/`; the versioned distribution source
above is the exact implementation tested here.

## Interpreter and ABI

- uv **0.9.26** official release:
  `https://github.com/astral-sh/uv/releases/tag/0.9.26`.
  `scripts/install-ci-tools.sh` verifies the official tarball SHA-256 values:
  arm64 `f71040c59798f79c44c08a7a1c1af7de95a8d334ea924b47b67ad6b9632be270`,
  amd64 `30ccbf0a66dc8727a02b0e245c583ee970bdafecf3a443c1686e1b30ec4939e8`.
- Build image `ghcr.io/astral-sh/uv:0.9.26-bookworm-slim` index digest
  `sha256:85c530098e4db6143cf1b63d1634a9150210a3f98690b3eb6e9fa6515bc60954`.
- Managed CPython **3.13.7**, Python Build Standalone build **20250918**.
  Exact GNU Linux x86-64 and arm64 archive URLs and SHA-256 values come from
  uv's pinned `crates/uv-python/download-metadata.json` at
  `https://raw.githubusercontent.com/astral-sh/uv/0.9.26/crates/uv-python/download-metadata.json`;
  relevant entries are saved in `evidence/python-downloads.json`.
- GNU builds require a compatible ELF loader/glibc and native-extension ABI.
  Upstream guidance at
  `https://github.com/astral-sh/python-build-standalone/blob/main/docs/running.rst`
  distinguishes GNU and musl targets. This lab bundles a GNU interpreter and
  does not claim Alpine/musl compatibility. The native Debian arm64 probe
  observed `/lib/ld-linux-aarch64.so.1` and glibc/libm dependencies.
- Probe base `debian:bookworm-slim` pinned index digest
  `sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587`.
  The observed compatibility claim is Debian 12/glibc 2.36 arm64 only;
  amd64 execution belongs to the authored hosted CI job until it runs.

## SBX environment grammar

Official release queried from `https://api.github.com/repos/docker/sbx-releases/releases/latest`:
**v0.47.0**, published 2026-10-05. Downloaded
`https://github.com/docker/sbx-releases/releases/download/v0.47.0/DockerSandboxes-linux-arm64.tar.gz`
inside the sandbox, extracted only the CLI/version metadata, ran only help/version.
Observed archive SHA-256:
`6a3c45df52ff32722bb33e4d2c66f9920e284b9a3adeba17afcfcea3ad346eff`.
That is an observed hash, not an independently checked release signature.
CLI reports source `0411f50ee4700fe7bd37e6e7e3aced563e850ca9`.

`evidence/sbx-help.txt` preserves actual `env`, `env run`, `env exec` and
`env rm` help. It documents relative kit/workspace resolution, host lifecycle
execution and `[PATH...] -- COMMAND` syntax. The official example supplies
`schemaVersion: "1"`, a reference-derived `agent`, `kits` and `workspace`.
The selected official shell workload is `docker/sbx-kit-shell:1.0.0`, index
digest `sha256:367c9a4b3fd550f777e1d57cc53550afb4a1385055d79111acf6f996272ff6de`.
No daemon-backed environment parse, creation or runtime enforcement was tested.

## Editorial and CI inputs

ACR **0.2.1** (`bc295fecafb04287a819bc4f21aed4d510a6a1c0`), pinned blog-writer
commit **61844184d925b9f925951241a0d476db7c193e7e**, package **1.2.0**,
content hash `sha256:2366fc9f075d01a1ff50eb86637c63647bf26cf51e301b4badfc6e10cf6c8c92`.
Scoped route and actual helper usage are recorded in `editorial-process.md`.
No identity is selected or inferred from the topic.

Actions checkout is pinned to its official 4.2.2 commit
`11bd71901bbe5b1630ceea73d27597364c9af683`. BuildKit **v0.29.0** uses index
digest `sha256:0039c1d47e8748b5afea56f4e85f14febaf34452bd99d9552d2daa82262b5cc5`.
The real runner is `ubuntu-24.04`; no SBX hosted runner is invented and no
image/repository publishing step is present.
