
--- COMPLETE READER DRAFT: README.md ---

# LangChain policy lab: Docker Sandboxes v3 kit

Build a small support assistant over four synthetic company policies. It ingests
Markdown sections, retrieves passages, returns source/section/chunk citations,
and invokes bounded read-only meal and receipt tools through LangChain. The
default model copies retrieved passages deterministically; it needs no API key.

This is a learning kit for AI engineers and platform teams evaluating internal
support workflows. It is not a production support service or a security certification.

## Quickstart without a paid credential

From the repository root, with Git and uv **0.9.26** installed on Linux:
If uv is not installed, follow [Prerequisites and downloads](docs/user-guide.md#prerequisites-and-downloads)
before running these commands.

uv downloads the interpreter into its user-level Python store, shown by
`uv python dir` (normally `~/.local/share/uv/python` on Linux). `--no-bin`
avoids adding Python launchers to your user bin directory; it does not replace
system Python. Then `uv sync` creates `sample/.venv` using that interpreter and
installs the locked project and test dependencies there.

```bash
uv python install --no-bin 3.13.7
cd sample
uv sync --locked --managed-python
uv run --locked --offline python -m langchain_enterprise.cli --query 'What is the Tier 1 meal allowance?'
uv run --locked --offline python -m langchain_enterprise.cli --tool meal --city-tier 1 --days 3
uv run --locked --offline python -m langchain_enterprise.cli --query 'Can I bring my pet python into the office?'
uv run --locked --offline python -m langchain_enterprise.cli --eval-suite
uv run --locked --offline pytest -v
```

Installation downloads Python and locked packages. Subsequent commands use the
local installation; `--offline` prevents uv dependency downloads, not arbitrary
application networking. Tests additionally prohibit socket connections.

Expect a `grounded` answer containing `$90` and a `travel_policy.md` citation,
a tool result with `total_usd: 270`, an `unsupported` pet question with no
citations, evaluation `passed: true` for 11 cases, and 49 passing tests. The fake
model validates this plumbing, not the reasoning quality of a real LLM.

## Kit and verification

`langchain.yaml` is a v3 **mixin**: it adds a bundled interpreter, locked
dependencies and the sample to an existing workload. It owns no entrypoint or
workload user. Its only typed request is agent context. It requests no network,
credentials, extra mounts or privilege. Linux glibc compatibility is deliberately
narrow: local evidence covers arm64 on Debian 12, not Alpine or arbitrary bases.

From the root, with Docker/Buildx, Go and curl available:
`install-ci-tools.sh` downloads checksum-pinned uv and builds Docker's kit-tck
from an exact source commit into the temporary directory you supply:

```bash
bash scripts/install-ci-tools.sh /tmp/langchain-tools
export PATH="/tmp/langchain-tools:$PATH"
```

`check-kit.sh` validates source, builds and exports the OCI image, then runs
artifact conformance checks. Supply a **new** layout path:

```bash
bash scripts/check-kit.sh /tmp/langchain-layout-new
```

`check-filesystem.sh` runs the bundled Python/sample on a Debian base without
system Python, with network disabled. It is a filesystem dependency probe,
not actual SBX composition:

```bash
bash scripts/check-filesystem.sh
```

GitHub Actions executes these checks,
behavioral tests and an isolated clean-checkout journey on `ubuntu-24.04`;
the hosted workflow itself has not been run from this unpublished repository.

## Next steps

- Read [the full guide](docs/user-guide.md) for failure handling, version pins,
  optional approved Gemini calls and the HUMAN Docker Sandboxes journey.
- `sample/sbxenv.yaml` describes a pinned shell workload plus this local mixin;
  CLI grammar was checked against official sbx **v0.47.0** help. Assembled SBX
  runtime and policy checks are optional and not run here.
- [Verification report](docs/verification-report.md) separates observed checks
  from unrun ones; [provenance](docs/provenance.md) identifies primary APIs/tools.
- [Marketing brief](docs/marketing-brief.md) and [proposed outline](docs/blog-outline.md)
  are neutral drafts; author selection and publication gates remain pending.

--- COMPLETE READER DRAFT: docs/user-guide.md ---

# Build and evaluate a synthetic policy assistant

## Who this is for

Python developers and AI platform engineers can use this lab to inspect a small
retrieval pipeline before adapting it to internal support. The exercise connects
policy ingestion, cited answers, bounded tools and evaluation with a reproducible
Docker Sandboxes v3 mixin. All policies and thresholds are fictional.

The default assistant is an extractive fake chat model. It returns retrieved
passages verbatim, so its results test orchestration and citation plumbing rather
than live LLM reasoning. A separately approved Gemini path is available later.

## Prerequisites and downloads

The Python journey requires Git, Linux, uv **0.9.26** and access to public Python
downloads. `sample/.python-version` pins **CPython 3.13.7**. uv downloads the
managed interpreter when requested; no system Python installation is needed.
The local verified target is Linux arm64, Debian 12/glibc 2.36. The automated
workflow targets native x86-64 `ubuntu-24.04`; its hosted run is still pending.
macOS, Windows, Alpine/musl and arbitrary minimal images are not verified targets.

To obtain uv, use its official 0.9.26 release at
`https://github.com/astral-sh/uv/releases/tag/0.9.26`. Select the archive for your
Linux architecture, check its published checksum, extract it, and put `uv` on
`PATH`. If also preparing kit tooling, `scripts/install-ci-tools.sh` does this
with pinned checksums for x86-64 and arm64, and builds kit-tck; it additionally
requires curl, tar, sha256sum, Git and Go with toolchain downloads enabled.

Building the kit requires a functioning Docker Engine and Buildx that supports
OCI directory export. Local checks used Docker **29.4.3**, Buildx **0.33.0** and
BuildKit **0.29.0**. The CI script selects a docker-container builder. Installation
needs access to GitHub/release assets, PyPI/files.pythonhosted.org, Go module and
checksum services, GHCR and Docker Hub. Runtime deterministic checks need none
of those connections. No credential is needed for the Python quickstart.

Start from a checkout or an extracted copy of this repository. Commands below
begin at its root unless a `cd` changes the directory. Nothing is published.

## 1. Install the locked sample

`uv --version` checks the tool pin. `uv python install --no-bin` downloads
CPython into uv's user-level store (normally `~/.local/share/uv/python` on Linux;
`uv python dir` shows the configured location) without adding Python launchers
to the user bin directory or replacing system Python. The following `uv sync`
creates `sample/.venv` and installs the project/test dependencies using that
managed interpreter.

```bash
uv --version
uv python install --no-bin 3.13.7
cd sample
uv sync --locked --managed-python
```

Expect `uv 0.9.26` and a `sample/.venv` containing the pinned project. The default
sync includes development tests but excludes the optional Gemini dependency.
`uv.lock` pins the full dependency graph and distribution hashes. Build-backend
dependencies are also pinned by uv build constraints and recorded in a separate
`build` dependency group; that group is not installed in the kit runtime. Do not
run an unlocked upgrade while reproducing the results.

In this `sample` directory, `data/policies` is the default corpus. Elsewhere,
pass `--policies /absolute/path/to/policies`. The kit's bundled corpus is
`/opt/langchain/sample/data/policies`; its interpreter is
`/opt/langchain/venv/bin/python`. Commands using that interpreter do not need uv.

## 2. Retrieve policy passages and inspect citations

```bash
uv run --locked --offline python -m langchain_enterprise.cli --query 'What is the Tier 1 meal allowance?'
```

Expect JSON with `status: "grounded"`, `provider: "deterministic"`, an answer
containing `Tier 1: $90 per day`, and a citation like:

```json
{"source": "travel_policy.md", "section": "Meal allowance", "chunk_id": "travel_policy:1", "title": "Synthetic Travel Policy"}
```

Open `data/policies/travel_policy.md`, find **Meal allowance**, and compare its
text to the answer. It is a daily meal allowance, not a separate dinner cap.
Other useful queries include `What is the receipt threshold?`,
`What is the home office equipment stipend?`, and
`Where are API keys and secrets stored?`.

Ingestion reads only the selected directory's Markdown files and splits at
`##` section headings. Each section becomes a LangChain `Document` with metadata.
A `BaseRetriever` implementation ranks token overlap after a small synonym map,
requires 60% query-token coverage, and returns at most two passages. LCEL then
connects payload preparation, `ChatPromptTemplate`, `BaseChatModel`, and
`StrOutputParser`. The result must parse and cite only retrieved chunk IDs.

This lexical retriever is intentionally small: there is no vector database,
embedding service, persistent index, PDF loader or access-control filter.
Synonyms are limited; changing wording can produce a refusal for an otherwise
answerable question. Partial overlap can also produce a relevant passage that
does not answer the full question. `grounded` means passages were retrieved and
citations validated; it does **not** certify semantic entailment or factual
correctness of a live answer.

## 3. Invoke bounded read-only tools

```bash
uv run --locked --offline python -m langchain_enterprise.cli --tool meal --city-tier 1 --days 3
uv run --locked --offline python -m langchain_enterprise.cli --tool receipt --amount 25
uv run --locked --offline python -m langchain_enterprise.cli --tool receipt --amount 24.99
```

Expect a meal total of `270` USD, `receipt_required: true` at `25`, and `false`
at `24.99`. Each result includes the source section's citation. The LangChain
tools read the already ingested policy passages; the thresholds are not a
second, independent copy of the dataset.

Meal inputs are strict integers: tiers 1-3 and days 1-30. Receipt amounts must
be finite numbers from 0 through 100,000 USD. Tools reject extra input fields,
strings used as numbers, booleans, invalid tiers and out-of-range amounts.
They cannot write files, run shell commands, fetch URLs or select arbitrary
paths. The CLI invokes tools explicitly; the model does not autonomously select
or execute them. This makes the execution boundary easy to inspect.

## 4. Evaluate refusals and failures

```bash
uv run --locked --offline python -m langchain_enterprise.cli --query 'Can I bring my pet python into the office?'
uv run --locked --offline python -m langchain_enterprise.cli --eval-suite
uv run --locked --offline pytest -v
```

Expect the pet question to return `unsupported`, no citations, and exit 0.
The evaluation prints `passed: true` for six grounded and five unsupported
questions; a failing case exits 1. Tests cover those cases, changed policy data,
tool boundaries, invalid JSON/citations, exceptions and CLI failures. The local
suite has 49 passing tests. It removes provider keys and prohibits socket
connections during test cases; all tests use fake models.

Try `--tool meal --days 31` or `--policies /nonexistent --eval-suite` to see a
configuration/tool failure with exit 1. Empty or oversized questions produce
`invalid_question`; model exceptions or malformed JSON produce
`model_or_output_failure`; unknown or duplicate citation IDs produce
`invalid_citations`. Errors never return a guessed answer or raw exception text.
For diagnosis, check the policy directory and exact input bounds first; for a
live call, check approval, optional package and credential/network availability.

`--offline` constrains uv's package operations. The default fake makes no model
request, but that flag is not a network sandbox for arbitrary Python. To check
the shipped runtime with the network disabled, use the filesystem probe below.

## 5. Build and verify the mixin

Return to the repository root:

```bash
cd ..
```

`install-ci-tools.sh` downloads checksum-pinned uv and builds Docker's kit-tck
from its exact source commit. It writes tools to the directory you supply,
downloads a Go 1.26.8 toolchain if needed, and deletes its temporary source
checkout. Put the resulting binaries on PATH:

```bash
bash scripts/install-ci-tools.sh /tmp/langchain-tools
export PATH="/tmp/langchain-tools:$PATH"
```

Use a fresh OCI directory; `check-kit.sh` refuses an existing path. It executes
`docker buildx build` against `langchain.yaml` for source validation **and** the
content build, exports OCI, and runs `kit-tck validate --layout ... 1.4.4`.
Local artifact evidence reports 19/19 conformance checks. `sbx kit validate` is
not a v3 source validator.

```bash
bash scripts/check-kit.sh /tmp/langchain-layout-new
```

The recipe starts from digest-pinned uv on Debian, installs a managed interpreter
inside `/opt/langchain/python`, and creates a locked noneditable environment
inside `/opt/langchain/venv`. Both trees, the project and synthetic documents go
into the scratch overlay. No symlink depends on the build stage's system Python.
The final `PATH` is additive during SBX composition. Mixin entrypoint, user and
workdir remain the workload's responsibility.

Bundling Python does not bundle a complete operating system. The GNU runtime
still requires the matching architecture's ELF loader and glibc/libm. The
filesystem probe copies the overlay onto digest-pinned Debian bookworm with no
system Python and runs the evaluation as uid 1000, read-only, `--network none`.
Run it with `scripts/check-filesystem.sh`. It manually supplies `PATH`; it does not exercise SBX's additive config merge,
capability negotiation, launch contract or policy enforcement.

```bash
bash scripts/check-filesystem.sh
```

The clean-checkout script clones the current local commit into a temporary
directory, uses an isolated dependency cache and managed Python, installs from
the lock, runs tests and the CLI journey, then removes the temporary checkout.
It only tests committed files. Run it after committing your own changes.

```bash
bash scripts/clean-checkout.sh
```

GitHub Actions uses a real `ubuntu-24.04` runner, downloads checksum-pinned uv,
fetches Docker's exact kit-tck source commit, builds it with Go 1.26.8 and
executes all verification scripts. Required checks have no conditional skips
or `continue-on-error`. No hosted SBX runner or daemon is assumed. The workflow
is authored but has not been dispatched from this unpublished local repository.

## 6. Optional HUMAN Docker Sandboxes journey

This section is a handoff, not a locally observed pass. On a human-controlled
machine with Docker Sandboxes **v0.47.0** or a compatible Kits-v3 runtime and an
existing working daemon, inspect `sample/sbxenv.yaml`. It selects the official
digest-pinned `docker/sbx-kit-shell:1.0.0` workload, adds `../` as this mixin,
and mounts the repository root (`workspace: ..`). `agent: sbx-kit-shell` is
the reference-derived handle, not an arbitrary agent name.

If that runtime is not already installed, the human operator should follow
Docker's installation instructions at `https://docs.docker.com/ai/sandboxes/install/`
and obtain platform-specific packages from
`https://github.com/docker/sbx-releases/releases/tag/v0.47.0`.
Installing just an extracted CLI is sufficient for the help checks performed
here, but not for this daemon-backed journey. Follow Docker's platform/runtime
requirements and verify the installed `sbx version` before continuing.

From the repository root, the v0.47.0 help supports:

```bash
sbx env plan sample/sbxenv.yaml
sbx env run --detached sample/sbxenv.yaml
sbx env exec sample/sbxenv.yaml -- /opt/langchain/venv/bin/python -m langchain_enterprise.cli --policies /opt/langchain/sample/data/policies --eval-suite
sbx env rm sample/sbxenv.yaml
```

Review and approve the environment plan yourself. These commands create and
remove a sandbox only on that human machine. No host lifecycle commands,
secrets or new credential bindings are in this file. Environment lifecycle
commands would run on the **host**, so do not add a `postCreate` test hook here.
The workload may request its own capabilities; this mixin adds only agent
context. The environment's workspace is the sole project mount.

Grammar was checked by downloading Docker's official sbx v0.47.0 Linux arm64
archive inside this task sandbox and running **only version/help**, not a
daemon. Relative paths, kits mappings and environment command forms appear in
that help and the pinned official example. No environment parse/create/run or
actual assembled policy test was performed. Before calling an adaptation
secure, a human must check actual composition, merged environment and denied
network behavior under their own organization's policy.

## 7. Optional approved live Gemini

The sample can send the question and retrieved synthetic passages to
`gemini-2.5-flash` using `langchain-google-genai==4.4.0`. This may incur provider
charges. The editorial Gemini review of these documents is a separate API use;
it is not validation of this sample's live-provider behavior.

Use only an existing organization-approved `GEMINI_API_KEY` or `GOOGLE_API_KEY`
already supplied to the process by your approved environment. Do not put keys
in this checkout, shell history, logs, or `sbxenv.yaml`. For a proxy-managed
sentinel credential, the human operator must approve routing to
`generativelanguage.googleapis.com` and its `x-goog-api-key` injection. This
minimal kit intentionally requests neither that egress nor a credential; the
default environment does not grant live access. Use the operator's installed
`sbx` help and approval process rather than assuming this file enables it.

After explicit approval, from `sample`:

```bash
uv sync --locked --extra gemini
uv run --locked --offline python -m langchain_enterprise.cli --provider gemini --approve-live --query 'What is the receipt threshold?'
```

Both the provider selection and `--approve-live` are required. The SDK has zero
retries, a 30-second request timeout and a 512-token output bound. Verify the
answer's `$25` rule yourself against the cited policy. A live response can
still misinterpret a passage while citing a valid ID. No live-provider quality
or reliability claim follows from the deterministic tests. Live sample calls
have not been run for this delivery.

## Enterprise adaptation choices

Keep policy ownership and effective dates explicit. Introduce access control
before retrieval, policy versioning, audit retention rules and representative
evaluation data before using real internal documents. Select an approved model
and data-handling agreement; measure unsupported questions and injection
attempts. A production index requires a separate storage/embedding decision.

The demo's heading-based chunk IDs change when sections are reordered. The
lexical retriever and citation-ID check are not authorization or entailment
controls. Read-only tool bounds limit these two functions, not arbitrary
Python execution by a developer. Docker artifact conformance is not evidence
of runtime isolation, compliance or readiness for enterprise deployment.

Exact source pins and API paths are in [provenance](provenance.md).
Observed commands, logs and unrun checks are in the [verification report](verification-report.md).

--- COMPLETE READER DRAFT: docs/marketing-brief.md ---

# Marketing brief: a policy-assistant lab for platform teams

## Audience and problem

An AI platform engineer needs a small, inspectable workflow before approving a
support assistant that handles internal policy documents. A useful first demo
should expose retrieval, citations and tool boundaries without requiring a
paid model account or real employee data.

This kit packages that exercise as a Docker Sandboxes v3 mixin. Teams can add
the pinned LangChain/Python runtime to an existing workload rather than replace
the agent environment. Four synthetic Markdown policies make the initial
questions and expected answers shareable. The meal tool returns 270 USD for
a three-day Tier 1 trip; the receipt tool distinguishes 24.99 from 25 USD.

## What the evidence supports

Local Linux arm64 checks passed 49 behavioral tests, an 11-case deterministic
evaluation, source build, OCI export and 19/19 kit-tck artifact checks. A
filesystem-only probe ran the bundled interpreter on Debian 12 without system
Python, as a non-root user, with network disabled and a read-only root filesystem.
The dependency lock and image digests make the installed inputs explicit.

The mixin requests only typed agent context. It adds no credential, network,
privilege or host-sharing requests. That gives a platform reviewer a small
declaration to inspect; capabilities requested by a chosen workload still
matter. Actual SBX composition and policy enforcement remain a HUMAN check.
No inference about enterprise security or compliance follows from kit-tck.

GitHub Actions is configured to build and verify on a real Ubuntu runner,
including fresh-checkout testing. Its hosted execution is pending. Live model
validation is also pending: the extractive fake checks plumbing, while the
Gemini provider is a separately approved, potentially billable path.

## Positioning and limits

Describe it as a reproducible learning lab for policy retrieval and bounded
tools. Avoid "production-ready," "secure by default," "universal portability,"
or a claim that fake answers establish model quality. The evidenced runtime
target is Linux arm64 on Debian/glibc; other workloads require compatibility
checks. This repository has no customer deployment evidence.

The next evaluation should test policy access control, prompt injection,
retrieval quality and citation entailment using approved data. A team adopting
it owns those decisions and its runtime policies. Start with the
[guide](user-guide.md), then review the [verification evidence](verification-report.md).

No personal or corporate author identity has been selected. This is a factual
explainer, not a Docker corporate announcement or an account of an author's
customer experience. Publication and distribution are not authorized.

--- COMPLETE READER DRAFT: docs/blog-outline.md ---

# Proposed blog outline

Working angle: **Follow a policy answer from a Markdown section to its citation**.
Audience: Python developers and AI platform engineers evaluating internal
support assistants. This proposes a post; it is not an approved new-blog draft.

1. Open with the Tier 1 meal question and its synthetic `$90` passage. Show the
   source, section and chunk ID before discussing an LLM.
2. Trace ingestion and lexical retrieval into the LangChain prompt/model/parser
   pipeline. Explain why the offline extractive fake is useful and what it
   cannot validate.
3. Run the three-day meal tool and the receipt boundary at `$25`. Explain the
   strict input limits and explicit, read-only invocation.
4. Ask an unsupported pet question and inspect its empty citations. Show how
   malformed model output and invalid IDs fail rather than return a guess.
5. Package the exercise as a v3 mixin with its own interpreter. Use the observed
   source build, OCI export, kit-tck and Debian filesystem probe as distinct
   evidence; explain the remaining glibc and composition constraints.
6. Close with the decisions a platform team still owns: approved data and
   provider access, runtime policy tests, access control and realistic evaluation.

Use only the published [guide](user-guide.md) and [verification report](verification-report.md)
as reader-visible supporting evidence. Do not invent a customer story, personal
failure anecdote, deployment results or a passed hosted workflow.

## Pending author gates

- Select and approve a personal and/or explicitly chosen corporate identity.
- Agree on the post's angle and outline with that author.
- Run the pinned blog-writer package's full new-blog workflow, including its
  identity/voice evidence gates, if a finished post is requested.
- Approve publication destination and any product/security claims separately.

These optional gates do not block the kit, sample or neutral guide. No post,
image or repository has been published or pushed.
