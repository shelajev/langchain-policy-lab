# Build and evaluate a synthetic policy assistant

## Who this is for

Python developers and AI platform engineers can use this lab to inspect a small
retrieval pipeline before adapting it for internal support. It assumes you know
Python, LangChain, Git, shell workflows, and how to work with a coding agent,
but have never built a Docker Sandboxes (SBX) kit. The exercise connects policy
ingestion, cited answers, bounded tools, and an evaluation suite with a
reproducible Docker Sandboxes v3 mixin. All policies and thresholds in the
sample corpus are fictional.

If you are looking for the primary single-file kit learning path, start with
[Run your LangChain app in Docker Sandboxes](run-your-langchain-in-docker-sandboxes.md).
Note that the single-file kit's native runtime pass evidence in the
[validation summary](acceptance-handoff.md) covers that single-file kit only;
it is separate from this policy-lab sample, where composed SBX execution and
live Gemini calls remain unrun.

### How the seven steps break down

Your first goal is a credential-free policy-QA loop you can inspect end to end
before changing any code: verify a retrieved answer against its citations,
call read-only expense tools explicitly, and run the evaluation suite and tests.

- **Steps 1-4 (host, Python only):** Run locally inside `sample` with no Docker,
  no `sbx`, no API keys, and no runtime network calls.
- **Step 5 (host, repository root):** Run helper scripts to build and check
  the OCI kit layout, probe the bundled Python overlay inside an offline Debian
  container, and verify a clean git checkout.
- **Steps 6-7 (optional human handoffs, unrun):** Step 6 tests actual `sbx`
  composition against a daemon-backed runtime; Step 7 sends one approved query
  to live Gemini.

### Why start with an extractive fake model?

Keep your coding agent's model and account separate from the application
runtime here. By default, this app uses a deterministic extractive fake chat
model (`provider: "deterministic"`) with no provider credentials. It echoes
retrieved passages verbatim so you can test retrieval, citation checks, tool
input validation, and failure paths without spending tokens or mixing up
plumbing bugs with LLM behavior. Live Gemini is isolated to Step 7 behind
explicit opt-in flags.

### What a Docker Sandboxes v3 kit is

A Docker Sandboxes kit is an OCI (Open Container Initiative) image containing
files plus a descriptor. Version 3 is the descriptor grammar used here.
A **workload** kit provides the operating system and the process/user settings
used to start its shell or coding agent;
a **mixin** layers extra tools, files, and environment values on top. When you
launch an environment, the sandbox runtime composes those artifacts and
evaluates their typed capability requests.

In this repository, those pieces map directly to five paths:

- [langchain.yaml](../langchain.yaml) declares the mixin and its single
  capability request.
- [langchain.dockerfile](../langchain.dockerfile) builds the filesystem overlay.
- [langchain-context.md](../langchain-context.md) contains packaged guidance text
  for the agent to read.
- [sample/](../sample/) holds the editable policy-QA Python project.
- [sample/sbxenv.yaml](../sample/sbxenv.yaml) declares a pinned shell workload,
  this local mixin, and the repository workspace for the optional Step 6 path.

This mixin's sole capability request is agent context
(`langchain-context.md`), packaged guidance for a coding-agent workload. It
does not launch the app. The shell workload in Step 6 has no coding agent to
read it automatically; you run the Python command yourself. This mixin
requests no credentials, extra mounts, network
egress, or privilege, and it does not pull policy data from the workload.
However, adding or omitting a request in a mixin does not make the effective
composed sandbox policy exclusive: other kits (including the workload) can
contribute grants that widen access, and runtime denies win over grants.

## Prerequisites and downloads

Start from a Git clone of the public repository at
`https://github.com/shelajev/langchain-policy-lab` if you will run all of Step 5.
An extracted archive is enough for the Python exercise, but cannot run the
clean-checkout check, which needs Git history. The kit image itself has
not been published to Docker Hub, Docker Cloud, or any other registry, and
Cloud or Hub workflows remain unrun and optional.

Unless a step explicitly says a command runs inside a container or sandbox
guest, run commands on your **host** starting at the repository root until a
`cd` changes your working directory.

### Required for Steps 1-4 (Python quickstart)

You need **Git**, Linux, **uv 0.9.26**, and network access to public Python
downloads for **CPython 3.13.7** (pinned in `sample/.python-version`) and
PyPI/`files.pythonhosted.org` for the locked packages installed by `uv sync`. No system Python installation or API key is needed.

- **Verified targets:** Local checks ran on Linux arm64 (Debian 12 / glibc
  2.36). Automated CI targets native x86-64 `ubuntu-24.04` and passed its first
  hosted run.
- **Unverified targets:** macOS, Windows, Alpine/musl, and arbitrary minimal
  images are not verified.

If `uv` is missing, install it from the
[official 0.9.26 release](https://github.com/astral-sh/uv/releases/tag/0.9.26).
The block below supports `x86_64` and `aarch64` (`arm64`) Linux with glibc and
requires `curl`, `tar`, plus `sha256sum` and `install` from GNU coreutils
(install any missing tool via your distribution's package manager first).

Run this block in Bash from any host directory. It downloads into a temporary
directory, checks the published SHA-256 checksum, extracts the nested binary,
and installs only `uv` into `~/.local/bin` (the parentheses keep the `cd`
local, and `set -eu` stops on error):

```bash
(
  set -eu
  case "$(uname -m)" in
    x86_64) target="x86_64-unknown-linux-gnu" ;;
    aarch64|arm64) target="aarch64-unknown-linux-gnu" ;;
    *) printf 'Supported architectures: x86_64 and aarch64\n' >&2; exit 1 ;;
  esac
  download_dir="$(mktemp -d)"
  cd "$download_dir"
  archive="uv-$target.tar.gz"
  release_url="https://github.com/astral-sh/uv/releases/download/0.9.26"
  curl --fail --location --output "$archive" "$release_url/$archive"
  curl --fail --location --output "$archive.sha256" "$release_url/$archive.sha256"
  sha256sum -c "$archive.sha256"
  tar -xzf "$archive"
  mkdir -p "$HOME/.local/bin"
  install -m 755 "uv-$target/uv" "$HOME/.local/bin/uv"
)
```

Expect `uv-<target>.tar.gz: OK` from the checksum check. If the download or
checksum fails, stop and fix the issue before continuing. Once it succeeds,
add `~/.local/bin` to your current shell's `PATH` and verify the version:

```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```

Expect a line starting with `uv 0.9.26`. That `export` applies only to the
current terminal; add `export PATH="$HOME/.local/bin:$PATH"` to `~/.bashrc`
if you want it in future Bash sessions.

### Required for Step 5 onward (kit build and verification)

Building and checking the mixin requires **Git**, a functioning local **Docker
Engine**, and **Buildx** with OCI directory export support. Local verification
used Docker **29.4.3**, Buildx **0.33.0**, and BuildKit **0.29.0**; CI selects a
`docker-container` builder. The check scripts use your active builder; they do
not create one. In `docker buildx ls`, `*` marks the selected builder.
A `docker-container` driver is the configuration used by CI for OCI exports.
If you already have a suitable builder selected, keep it. Otherwise, with a
local Docker Engine selected and the name `langchain-ci` unused, the same
pinned setup as the [CI workflow](../.github/workflows/ci.yml) is:

```bash
docker buildx create --name langchain-ci --driver docker-container --driver-opt image=moby/buildkit:v0.29.0@sha256:0039c1d47e8748b5afea56f4e85f14febaf34452bd99d9552d2daa82262b5cc5 --use
docker buildx inspect --bootstrap
```

This creates and selects a builder using that local engine. Confirm it is
marked active before running the build checks; do not continue with a builder
that cannot export OCI layouts.

If you use `scripts/install-ci-tools.sh` to install pinned `uv` and build
`kit-tck`, you also need `curl`, `tar`, `sha256sum`, Git, and **Go** with
toolchain downloads enabled. `kit-tck` is Docker's checker for kit artifact
format and declarations; it is not a sandbox runtime or a runtime security
test.

Installation and build steps pull from GitHub release assets,
PyPI/`files.pythonhosted.org`, Go module and checksum services, GHCR, and Docker
Hub. After installation, the deterministic Python checks make no network calls.
The Step 5 container process runs with networking disabled, but building its
images can still download artifacts.

## 1. Install the locked sample

Run these commands on your **host**, starting at the repository root. The
`cd sample` step moves you into `sample/` for Steps 1-4:

```bash
uv --version
uv python install --no-bin 3.13.7
cd sample
uv sync --locked --managed-python
```

Here is what happens:

- `uv python install --no-bin 3.13.7` places CPython 3.13.7 into `uv`'s
  user-level store (typically `~/.local/share/uv/python` on Linux; check with
  `uv python dir`) without adding launchers to your bin directory or touching
  system Python.
- `uv sync --locked --managed-python` creates `sample/.venv` and installs the
  project and development test dependencies using the hashes in `uv.lock`.

Expect `uv 0.9.26` and a populated `sample/.venv`. The default sync excludes
the optional `gemini` extra. Build-backend dependencies are pinned by `uv` build
constraints in a separate `build` dependency group that is not installed in the
kit runtime. Do not run an unlocked upgrade while reproducing these results,
and do not assume fresh unlocked resolutions would behave the same way without
testing them.

Inside `sample/`, `data/policies` is the default policy corpus. If you invoke
the CLI from another directory, pass `--policies /absolute/path/to/policies`.
Inside the built kit image (Step 5 onward), the bundled corpus sits at
`/opt/langchain/sample/data/policies` and the interpreter is
`/opt/langchain/venv/bin/python` (no `uv` needed there).

## 2. Retrieve policy passages and inspect citations

Run this on your **host** from `sample/`:

```bash
uv run --locked --offline python -m langchain_enterprise.cli --query 'What is the Tier 1 meal allowance?'
```

Expect JSON with `status: "grounded"`, `provider: "deterministic"`, an answer
containing `Tier 1: $90 per day`, and a citation like:

```json
{"source": "travel_policy.md", "section": "Meal allowance", "chunk_id": "travel_policy:1", "title": "Synthetic Travel Policy"}
```

Open `data/policies/travel_policy.md`, find **Meal allowance**, and compare it
to the returned text: it is a daily meal allowance, not a per-dinner cap. Other
useful queries to try are `What is the receipt threshold?`,
`What is the home office equipment stipend?`, and
`Where are API keys and secrets stored?`.

### How the pipeline and boundaries work

Under the hood, ingestion reads only Markdown files in the selected directory
and splits at `##` section headings, turning each section into a LangChain
`Document` with metadata. A custom `BaseRetriever` scores token overlap after
a small synonym map, requires at least 60% query-token coverage, and returns at
most two passages. LangChain Expression Language (LCEL) then wires payload
preparation, `ChatPromptTemplate`, `BaseChatModel`, and `StrOutputParser`,
requiring valid JSON whose citations match retrieved chunk IDs.

Keep the retriever's limits in mind:

- It is a small **lexical token-overlap retriever**, not FAISS or any vector
  database. There is no embedding service, persistent index, PDF loader, or
  access-control filter.
- Because the synonym map is minimal, rewording a question can trigger a refusal
  even when a passage exists, and partial token overlap can retrieve a related
  section that does not answer the full question.
- `grounded` only means passages were retrieved and citation IDs validated.
  It does **not** certify semantic entailment or factual correctness of a live
  model's answer.

## 3. Invoke bounded read-only tools

Run these commands on your **host** from `sample/`:

```bash
uv run --locked --offline python -m langchain_enterprise.cli --tool meal --city-tier 1 --days 3
uv run --locked --offline python -m langchain_enterprise.cli --tool receipt --amount 25
uv run --locked --offline python -m langchain_enterprise.cli --tool receipt --amount 24.99
```

Expect a meal total of `270` USD, `receipt_required: true` at `25`, and
`receipt_required: false` at `24.99`, each accompanied by the source section's
citation. The LangChain tools parse the already-ingested policy passages rather
than hardcoding a separate copy of the thresholds.

Tool bounds are enforced in code: meal inputs require integers
(`--city-tier` 1-3, `--days` 1-30), and receipt amounts must be finite numbers from `0`
through `100,000` USD. The tools reject extra fields, strings passed as
numbers, booleans, invalid tiers, and out-of-range values. They cannot write
files, run shell commands, fetch URLs, or pick arbitrary paths. Because the CLI
invokes them explicitly, the model never autonomously chooses or executes tools.

## 4. Evaluate refusals and failures

Run these checks on your **host** from `sample/`:

```bash
uv run --locked --offline python -m langchain_enterprise.cli --query 'Can I bring my pet python into the office?'
uv run --locked --offline python -m langchain_enterprise.cli --eval-suite
uv run --locked --offline pytest -v
```

Expected outcomes:

- The pet question returns `unsupported`, empty citations, and exit code `0`.
- `--eval-suite` prints `passed: true` across six grounded and five unsupported
  questions (11 cases total), exiting `1` if any case fails.
- `pytest -v` runs 49 tests covering those cases, modified policy data, tool
  input bounds, malformed JSON/citations, exceptions, and CLI errors. All tests
  use fake models, strip provider keys, and block socket connections.

To inspect error handling, try `--tool meal --city-tier 1 --days 31` or
`--policies /nonexistent --eval-suite`; both exit `1`. Empty or oversized
questions return `invalid_question`, model exceptions or malformed JSON return
`model_or_output_failure`, and unknown or duplicate citation IDs return
`invalid_citations`. Failures never return a guessed answer or raw exception
text. When troubleshooting, check the policy directory path and exact input
bounds first; for live calls, verify approval, the `gemini` extra, and
credential or network availability.

Note what `--offline` does and does not isolate: it keeps `uv` from touching
the network for package operations, and the default fake model makes no API
requests, but `--offline` is **not** a network sandbox for arbitrary Python
code. To verify the packaged runtime with networking actually disabled, run
the filesystem probe in Step 5.

## 5. Build and verify the mixin

All helper scripts in this step run on your **host** from the **repository
root**. First return from `sample/` to the repository root:

```bash
cd ..
```

### Install helper tools and check the OCI kit

From the repository root, `scripts/install-ci-tools.sh` downloads
checksum-pinned `uv` and builds `kit-tck` into the directory you supply. The
`go` command must already be installed: the script requests Go 1.26.8 with
`GOTOOLCHAIN=go1.26.8`, which can download that toolchain; it does not install
Go from scratch. It then removes its temporary source checkout:

```bash
bash scripts/install-ci-tools.sh /tmp/langchain-tools
export PATH="/tmp/langchain-tools:$PATH"
```

The installer prints the installed uv and `kit-tck` versions and verifies the
checker's source commit in `docker/sandbox-kit-spec`. It installs the same uv
0.9.26 alongside the checker, so prepending this tools directory selects the
CI-pinned copy rather than your earlier installation. An error stops the script; continue only after exit 0.

Next, run `scripts/check-kit.sh` from the repository root with a fresh output
directory path (it refuses to overwrite an existing directory). It runs
`docker buildx build` against `langchain.yaml` for both source validation and
content build, exports the OCI layout, and executes
`kit-tck validate --layout ... 1.4.4` (`1.4.4` selects the kit's OCI reference
tag, also used as this mixin's version). Local checks reported 19/19 conformance
checks passing. Note that `sbx kit validate` is not a v3 source validator.

```bash
bash scripts/check-kit.sh /tmp/langchain-layout-new
```

The Dockerfile stage starts from digest-pinned `uv` on Debian, installs a
managed CPython interpreter into `/opt/langchain/python`, and creates a locked,
noneditable environment in `/opt/langchain/venv`. Both trees, the sample
project, and the synthetic policies go into a `scratch` overlay with no
symlinks pointing back to the build stage's system Python. During SBX
composition, `PATH` is additive; entrypoint, user, and working directory remain
the workload's responsibility.

### Probe the offline runtime and clean checkout

Bundling Python does not bundle a whole operating system: the GNU Python
runtime still expects a matching architecture's ELF loader and `glibc`/`libm`.
From the repository root on your **host**, `scripts/check-filesystem.sh`
builds its own `langchain:filesystem` overlay from `langchain.yaml`, then
copies it onto digest-pinned Debian bookworm (with no system Python). It does
not consume Step 5's OCI export. It runs the evaluation inside that container
as uid `1000`,
read-only, with `--network none`:

```bash
bash scripts/check-filesystem.sh
```

Expect the Python version, shared-library information and evaluation JSON
with `passed: true`, followed by exit 0.

Keep its boundary clear: the probe supplies `PATH` manually and proves the
bundled Python and evaluation suite work offline on Debian bookworm, but it
does **not** test SBX's additive config merge, capability negotiation, launch
contract, or policy enforcement.

Finally, from the repository root on your **host**, `scripts/clean-checkout.sh`
clones your current local commit into a temporary directory, installs from
`uv.lock` using an isolated cache and managed Python, runs the test suite and
CLI checks, and removes the temporary directory. Because it tests committed
files only, use a Git checkout and commit your changes before running it.
It needs network access to fetch Python and packages into its isolated stores,
plus Docker, Buildx and `kit-tck` for its build/container checks:

```bash
bash scripts/clean-checkout.sh
```

A successful run finishes with `Clean-checkout journey passed with isolated
dependency cache and managed interpreter.` It exits nonzero if a required
tool or check fails.

In GitHub Actions, an `ubuntu-24.04` runner installs pinned `uv`, builds
`kit-tck` with Go 1.26.8 from the exact commit, and runs all verification
scripts with no conditional skips or `continue-on-error` (and no SBX daemon
assumed). That workflow passed on its first hosted run after push.

## 6. Optional HUMAN Docker Sandboxes journey

This composed SBX run has not been verified against a live sandbox daemon.
The [validation summary](acceptance-handoff.md) covers a different artifact,
the single-file kit. Treat the commands below as an optional runtime check,
not a recorded success.

On a machine with Docker Sandboxes **v0.47.0** (or a
compatible Kits-v3 runtime) and a working daemon, inspect `sample/sbxenv.yaml`.
It selects the digest-pinned official `docker/sbx-kit-shell:1.0.0` workload,
adds `../` as this mixin, and mounts the repository root (`workspace: ..`).
`agent: sbx-kit-shell` selects the shell agent identified by the
`docker/sbx-kit-shell` workload reference listed under `kits`; it tells the
runtime which process to start alongside the mixin.

This environment points to the local source directory `../`, not the OCI
layout exported in Step 5. Step 5 validates that source but does not produce an
input consumed by these commands. The runtime must support local v3 source
kits; inspect the plan and stop if it rejects that setup. That composition
behavior has not been exercised for this policy-lab environment. The command
below runs the baked `/opt/langchain` copy, not live edits in the mounted
repository; rebuild the mixin to include source changes.

If the runtime is not installed yet, follow Docker's instructions at
`https://docs.docker.com/ai/sandboxes/install/` and get platform packages from
`https://github.com/docker/sbx-releases/releases/tag/v0.47.0`. Extracting only
the CLI binary is enough for `--help` checks, not for this daemon-backed
journey. Check `sbx version` before proceeding.

Run these commands one at a time on your **host** from the **repository root**.
`sbx env plan`, `run`, and `rm` drive the host daemon and sandbox lifecycle;
`sbx env exec` runs `/opt/langchain/venv/bin/python` inside the composed
**sandbox guest**. Inspect the plan before approving creation, and wait for
evaluation output before removing the sandbox:

```bash
sbx env plan sample/sbxenv.yaml
sbx env run --detached sample/sbxenv.yaml
sbx env exec sample/sbxenv.yaml -- /opt/langchain/venv/bin/python -m langchain_enterprise.cli --policies /opt/langchain/sample/data/policies --eval-suite
sbx env rm sample/sbxenv.yaml
```

Expected outcomes if you run this check (not recorded results):

- `plan` prints the proposed environment without making changes. Confirm it
  selects the pinned shell workload, the local LangChain mixin, and the
  repository workspace.
- After your approval, `run --detached` creates or starts the sandbox without
  attaching a terminal. The subsequent `exec` must find the bundled interpreter;
  a launch error or missing Python means composition failed.
- `exec` should print evaluation JSON with `passed: true` across the same 11
  cases as the local run. Save the actual output; investigate any error or
  failed case.
- After your removal approval, `rm` removes the sandbox. Treat a cleanup error
  as unfinished cleanup, not a passing handoff.

These criteria do not predict exact daemon messages or prove denied-network
behavior; capture the actual output and verify runtime policy separately.

### Access review and composition limits

Review and approve the plan yourself. `sample/sbxenv.yaml` contains no host
lifecycle hooks, secrets, or credential bindings, and `workspace: ..` is its
sole project mount. Do not add a `postCreate` test hook there, because
environment lifecycle commands run on the **host**.

Remember that the workload may request its own capabilities while this mixin
adds only agent context. Adding or omitting an allow request in a mixin does
not make the effective composed sandbox policy exclusive: other grants can widen
access, and runtime denies win over grants.

Only the official `sbx` v0.47.0 Linux arm64 `version` and `help` output was
checked; no daemon was used. Relative paths, `kits` mappings, and `env`
subcommands appear in that help and the pinned official example, but no
environment parse, create, run, merged-policy check, or denied-network test
was performed. Before calling any adaptation secure, verify actual composition,
merged environment variables, and denied-network behavior under your
organization's policy.

## 7. Optional approved live Gemini

This policy-lab sample has not been tested against the live Gemini API.
The sample can send the user question and retrieved synthetic passages to
`gemini-2.5-flash` via `langchain-google-genai==4.4.0`, which may incur
provider charges. This is the app's runtime provider, separate from your coding agent's model
and account.

Use only an existing organization-approved `GEMINI_API_KEY` or `GOOGLE_API_KEY`
already injected into the process by your approved environment. Never put keys
in this checkout, shell history, logs, or `sbxenv.yaml`. If you use a
proxy-managed sentinel credential, the operator must approve routing to
`generativelanguage.googleapis.com` and `x-goog-api-key` header injection;
this minimal kit intentionally requests neither that egress nor any
credential. Check the complete environment's effective policy and bindings;
the absence of a request in this mixin alone does not prove access is blocked.

After explicit approval, run these commands on your **host** from **`sample/`**
(if you are still at the repository root after Step 5 or Step 6, `cd sample`
first):

```bash
uv sync --locked --extra gemini
uv run --locked --offline python -m langchain_enterprise.cli --provider gemini --approve-live --query 'What is the receipt threshold?'
```

Both `--provider gemini` and `--approve-live` are required. The SDK client is
configured with zero retries, a 30-second request timeout, and a 512-token
output bound. Verify the `$25` rule in the answer against the cited policy
yourself: a live model can cite a valid chunk ID and still misread the text.
Deterministic tests imply no live-provider quality or reliability guarantee.

## Enterprise adaptation choices

Before using real internal documents, make policy ownership and effective
dates explicit, enforce access control **before** retrieval, and add policy
versioning, audit retention rules, and a representative evaluation suite.
Select an approved model with an appropriate data-handling agreement, measure
refusal rates and prompt-injection attempts, and make a separate architecture
decision for production storage and embeddings.

Keep the sample's structural limits in view:

- Heading-based chunk IDs shift whenever sections are reordered.
- The lexical retriever and citation-ID check are not authorization or
  entailment controls.
- Read-only tool bounds restrict only those two CLI functions, not arbitrary
  Python code run by a developer.
- Docker artifact conformance (`kit-tck`) is not evidence of runtime isolation,
  compliance, or enterprise readiness.

Exact source pins and API paths are recorded in [provenance](provenance.md).
The primary single-file kit's native runtime checks and limitations (distinct
from this policy-lab sample's unrun Step 6 and Step 7) are in the
[validation summary](acceptance-handoff.md).
