## README.md

# LangChain Policy Lab for Docker Sandboxes

Try a policy assistant over four fictional company documents: retrieve a meal
allowance, inspect its citations, calculate a trip total, and test an unsupported
question. The default model copies retrieved passages deterministically, so you
can check the LangChain pipeline without employee data or a model API key.

This independent learning lab packages that exercise as a Docker Sandboxes v3
mixin kit. It is not a production support service or an official Docker guide.

## Choose your route

- For the SBX product story, read the [product overview](docs/product-overview.md),
  then the [marketing brief](docs/marketing-brief.md) for audiences and supported claims.
- To run the sample, start with the quickstart below and continue in the
  [developer guide](docs/user-guide.md) for explanations, failures and optional paths.
- The [blog outline](docs/blog-outline.md) is a proposal only; author selection
  and publication approval remain pending.

## What you get

- [langchain.yaml](langchain.yaml) declares the v3 mixin;
  [langchain.dockerfile](langchain.dockerfile) builds its file overlay with Python
  3.13.7, locked dependencies and the bundled sample. A workload supplies the
  operating system and agent launch. There is no published kit image.
- [langchain-context.md](langchain-context.md) supplies packaged guidance for
  the coding agent through the mixin's sole capability request, agent context.
  The mixin requests no credentials, network access, extra mounts or privilege;
  a chosen workload and runtime policy still determine the sandbox's access.
- [sample/](sample/) provides policy retrieval, source/section/chunk citations,
  bounded read-only meal and receipt tools, and evaluations. The developer's
  goal is a repeatable policy-QA workflow before considering the optional live
  Gemini path, which needs separate provider approval.
- [sample/sbxenv.yaml](sample/sbxenv.yaml) declares how to combine the pinned
  shell workload, local mixin and repository workspace. It is a runtime
  environment declaration, not a Python install step or a grant of live access.
- Local review passed 49 tests, 11 evaluation cases and 19 kit conformance checks,
  plus a Debian filesystem probe. [Hosted Actions run 37961247968](https://github.com/shelajev/langchain-policy-lab/actions/runs/37961247968)
  passed. Actual composed SBX execution and live Gemini sample validation are
  **unrun human handoffs**; artifact checks do not establish runtime policy enforcement.

## Quickstart without a paid credential

Start at the repository root on Linux with Git and uv **0.9.26** installed.
If uv is missing, follow [Prerequisites and downloads](docs/user-guide.md#prerequisites-and-downloads)
first. No Docker daemon or SBX installation is needed for this Python path.

uv downloads the managed interpreter into its user-level Python store, shown by
`uv python dir` (normally `~/.local/share/uv/python` on Linux). `--no-bin` avoids
adding Python launchers to your user bin directory; it does not replace system
Python. `uv sync` creates `sample/.venv` and installs the locked dependencies.

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

Installation downloads Python and packages. Subsequent commands use the local
installation; `--offline` prevents uv dependency downloads, not arbitrary Python
networking. The default model makes no model request.

Expect a `grounded` answer containing `$90` and a `travel_policy.md` citation,
a tool result with `total_usd: 270`, an `unsupported` pet question with no
citations, evaluation `passed: true` for 11 cases, and 49 passing tests. These
results test retrieval, citations and tool behavior, not live-model reasoning.

## Continue or inspect the evidence

The [developer guide](docs/user-guide.md) keeps kit build commands and prerequisites
in one place, followed by the separately unrun [SBX handoff](docs/user-guide.md#6-optional-human-docker-sandboxes-journey)
and [live Gemini path](docs/user-guide.md#7-optional-approved-live-gemini).
The [verification report](docs/verification-report.md) and
[independent QC report](docs/qc-delivery-report.md) describe observed checks and
their limits; [provenance](docs/provenance.md) records the source and API pins.

## docs/product-overview.md

# A LangChain developer journey with Docker Sandboxes kits

An enterprise developer wants to build an assistant that answers questions about
travel and expenses. Before using real company documents or connecting a paid
model, they need a small project where they can inspect the retrieved sources,
exercise tools, and check whether changes break expected behavior.

This independent lab provides that project and packages its development dependencies
as a Docker Sandboxes v3 kit. It lets an SBX product manager examine a concrete
example of what a framework-specific kit could offer to developers.

SBX is the Docker Sandboxes runtime and its `sbx` command-line tool. Product
managers can read this overview and the [marketing brief](marketing-brief.md)
without running commands. For the runnable journey, use the
[developer guide](user-guide.md); no prior kit or SBX knowledge is required.

## The kit and the project serve different purposes

The **LangChain kit** supplies the environment: Python 3.13.7, locked LangChain
dependencies, a bundled copy of the sample, and instructions for the coding
agent. Its descriptor is [langchain.yaml](../langchain.yaml), and its build recipe
is [langchain.dockerfile](../langchain.dockerfile). The recipe builds a file
overlay, not a complete operating system. [langchain-context.md](../langchain-context.md)
contains the packaged coding-agent guidance delivered through its agent-context
capability; it is separate from the sample's policy documents.

It is a **mixin kit**. A workload supplies the base operating system and agent;
the LangChain mixin adds the framework and project tools to that workload. The
developer can keep their chosen workload while adding LangChain support. This
example uses a pinned shell workload in [sample/sbxenv.yaml](../sample/sbxenv.yaml).
That environment declaration selects the workload and local mixin and sets the
repository root as the workspace. It tells the runtime what to assemble; it does
not install the local Python project or approve model-provider access.
The recipe targets Linux with glibc; compatibility with other bases needs checking.

The **sample project** supplies the exercise: four fictional company policy
documents, a LangChain retrieval pipeline, cited answers, two expense tools, and
tests. It gives the developer something useful to build on after the environment
is available. The kit contains the sample, and the repository also exposes its
source under [sample/](../sample/) for editing and testing.

The **guide** explains the experience step by step. It starts with a local Python
run, which has been verified, then describes the separately unrun SBX composition
path. Read [the developer guide](user-guide.md) for commands and expected outputs.

## Follow the developer's first task

The developer asks, "What is the Tier 1 meal allowance?" The application reads the
synthetic policy documents, retrieves relevant sections, and returns the $90 daily
allowance with the source file, section, and chunk identifier. The developer can
open the cited document and compare the answer with the source.

Next, they calculate a three-day trip's meal allowance. A bounded LangChain tool
returns $270. Another tool checks the fictional $25 receipt threshold. These
tools calculate results from explicit inputs; they do not submit expenses or
modify a company system.

Then the developer asks a question the documents cannot answer. The example pet
question returns an unsupported result without citations. Invalid tool inputs
also fail. These cases let the developer inspect failure behavior alongside the
successful answer.

The developer runs an evaluation suite and tests before changing the project.
They can then change a policy, retrieval behavior, or tool and rerun the checks.
The default model copies retrieved text deterministically, so the exercise needs
no API key and produces repeatable outputs. It tests the LangChain pipeline and
citation handling; a real model's answer quality needs a separate evaluation.

Once provider access is approved, the guide offers an optional live Gemini path,
which remains unrun for this sample.
Adapting the project to real enterprise data would also require decisions about
document access, retrieval quality, prompt injection, and runtime policy. Those
are adoption work, rather than capabilities demonstrated by this sample.

## Where SBX fits into that journey

The intended sandbox path is to combine the shell workload and LangChain mixin
using `sample/sbxenv.yaml`, mount the project workspace, and work on the sample
inside that environment. The kit supplies the pinned Python environment instead
of requiring the developer to assemble it inside each workload.

The mixin requests only agent context: packaged guidance for the agent. It does
not itself request network access, credentials, privilege, or extra host mounts.
The selected workload and runtime policies still determine the complete sandbox's
access. The sample's local Python quickstart can be tried independently of SBX.

For a product demonstration, the next step is to launch that composed environment
with an available SBX daemon, verify its interpreter and workspace behavior, and
check runtime policy enforcement. This actual composed SBX run remains an unrun
human handoff. The environment declaration's CLI grammar was
checked against official SBX help, but this composed runtime demonstration has
not been executed.

## What a product manager can assess today

The repository contains a built and verified kit artifact recipe, a working
sample, a developer guide, and an automated verification workflow. Independent
QC passed 49 tests, 11 evaluation cases, 19 kit conformance checks, and a Debian
filesystem probe using the bundled interpreter. The
[first hosted workflow, run 37961247968](https://github.com/shelajev/langchain-policy-lab/actions/runs/37961247968)
also passed. See [verification evidence](verification-report.md) and
[independent QC](qc-delivery-report.md) for the scope of those results.

This gives a concrete artifact set for discussing framework-specific kits:
what environment the kit should install, what starter project helps a developer
get moving, and what guide and checks make that project understandable. It does
not yet demonstrate a published kit installation or the full SBX runtime journey.
There is no Docker Hub release, real customer deployment, or live-model quality
result. Live Gemini sample validation also remains an unrun human handoff.

For sharing the idea, the [marketing brief](marketing-brief.md) explains the
audience and supported claims. The [blog outline](blog-outline.md) proposes a
developer article; it is an outline, not a finished post. Start with this overview
for the product story and use the guide for the hands-on developer story.

## docs/user-guide.md

# Build and evaluate a synthetic policy assistant

## Who this is for

Python developers and AI platform engineers can use this lab to inspect a small
retrieval pipeline before adapting it to internal support. The exercise connects
policy ingestion, cited answers, bounded tools and evaluation with a reproducible
Docker Sandboxes v3 mixin. All policies and thresholds are fictional.

Your first result is a credential-free policy-QA workflow: check the retrieved
answer against its citations, invoke an expense tool explicitly, and run the
evaluation before changing the sample. Steps 1-4 run locally without Docker or
SBX. Step 5 builds and checks the kit artifact. Steps 6-7 are optional human
handoffs for actual SBX composition and live Gemini; both remain unrun here.
For the product story instead of commands, read the
[product overview](product-overview.md) and [marketing brief](marketing-brief.md).

The default assistant is an extractive fake chat model. It returns retrieved
passages verbatim, so its results test orchestration and citation plumbing rather
than live LLM reasoning. A separately approved Gemini path is available later.

A Docker Sandboxes kit is an OCI (Open Container Initiative) image containing
files plus a descriptor. Version 3 is the descriptor grammar used here. A
workload kit supplies the operating system and agent launch; a mixin layers
tools and environment values onto it. The sandbox runtime composes these
artifacts and handles their typed capability requests. This mixin's sole
request, agent context, supplies packaged guidance text for the agent to read.
It does not provide policy data from the workload or grant network access.

[langchain.yaml](../langchain.yaml) declares the mixin and its capability;
[langchain.dockerfile](../langchain.dockerfile) builds the overlay;
[langchain-context.md](../langchain-context.md) contains the agent guidance.
The editable [sample project](../sample/) supplies the policy-QA exercise.
Its [sample/sbxenv.yaml](../sample/sbxenv.yaml) declares a pinned shell workload,
this local mixin and the repository workspace for the optional runtime path.
The mixin requests no credentials, extra mounts or privilege. Workload requests
and runtime policies still matter to the composed environment's access.

## Prerequisites and downloads

Assume basic Python, terminal and Git knowledge. No prior uv, SBX or Kits v3
knowledge is needed. uv manages Python installations and locked project
dependencies; the commands below explain its relevant options. Familiarity
with containers is useful for step 5 onward, where Docker tooling is required.

The Python journey requires Git, Linux, uv **0.9.26** and access to public Python
downloads. `sample/.python-version` pins **CPython 3.13.7**. uv downloads the
managed interpreter when requested; no system Python installation is needed.
The local verified target is Linux arm64, Debian 12/glibc 2.36. The automated
workflow targets native x86-64 `ubuntu-24.04`; its first hosted run passed.
macOS, Windows, Alpine/musl and arbitrary minimal images are not verified targets.

To obtain uv, use its official 0.9.26 release at
`https://github.com/astral-sh/uv/releases/tag/0.9.26`. Select the archive for your
Linux architecture, check its published checksum, extract it, and put `uv` on
`PATH`. If also preparing kit tooling, `scripts/install-ci-tools.sh` does this
with pinned checksums for x86-64 and arm64, and builds kit-tck; it additionally
requires curl, tar, sha256sum, Git and Go with toolchain downloads enabled.
kit-tck is Docker's checker for kit artifact format and declarations, not a
sandbox runtime or a runtime security test.

Building the kit requires a functioning Docker Engine and Buildx that supports
OCI directory export. Local checks used Docker **29.4.3**, Buildx **0.33.0** and
BuildKit **0.29.0**. The CI script selects a docker-container builder. Installation
needs access to GitHub/release assets, PyPI/files.pythonhosted.org, Go module and
checksum services, GHCR and Docker Hub. Runtime deterministic checks need none
of those connections. No credential is needed for the Python quickstart.

Start from a checkout or an extracted copy of this repository. Commands below
begin at its root unless a `cd` changes the directory. The repository is on GitHub;
the kit image has not been published to a registry.

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
requires 60% query-token coverage, and returns at most two passages. LangChain
Expression Language (LCEL) then
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
passed in its first hosted run after the repository was pushed to GitHub.

## 6. Optional HUMAN Docker Sandboxes journey

`sbx` is the Docker Sandboxes command-line tool. Its `sbxenv.yaml` environment
file selects a workload, mixins and workspace for the runtime to assemble.

This actual composed SBX run is an unrun human handoff. On a human-controlled
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

Live Gemini sample validation remains an unrun human handoff.

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

## docs/marketing-brief.md

# Marketing brief: a policy-assistant lab for platform teams

## Audience and problem

An SBX product manager can use the [product overview](product-overview.md) to
assess the kit's developer value, then use this brief to explain the evidence
and limits. SBX means Docker Sandboxes and its runtime tooling. A LangChain
developer should start with the [README quickstart](../README.md#quickstart-without-a-paid-credential)
and [developer guide](user-guide.md) for the runnable journey.

An AI platform engineer needs a small, inspectable workflow before approving a
support assistant that handles internal policy documents. A useful first demo
should expose retrieval, citations and tool boundaries without requiring a
paid model account or real employee data.

This independent lab packages that exercise as a Docker Sandboxes v3 mixin.
Teams can add the pinned LangChain/Python runtime to an existing workload, keeping
its operating system and agent. [langchain.yaml](../langchain.yaml) declares the
mixin; [langchain.dockerfile](../langchain.dockerfile) builds its file overlay;
[langchain-context.md](../langchain-context.md) supplies coding-agent guidance.
The [sample project](../sample/) contains the assistant and checks, while
[sample/sbxenv.yaml](../sample/sbxenv.yaml) declares the pinned workload, local
mixin and workspace for the optional runtime path.

The developer first runs deterministic policy QA with citations and explicit,
bounded tools. Four synthetic Markdown policies make the initial
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
matter. Actual composed SBX execution and policy enforcement remain an unrun
human handoff.
No inference about enterprise security or compliance follows from kit-tck.

GitHub Actions is configured to build and verify on a real Ubuntu runner,
including fresh-checkout testing. Its
[first hosted run, 37961247968](https://github.com/shelajev/langchain-policy-lab/actions/runs/37961247968)
passed. Live Gemini sample validation remains an unrun human handoff: the
extractive fake checks plumbing, while the
Gemini provider is a separately approved, potentially billable path.

## Positioning and limits

Describe it as a reproducible learning lab for policy retrieval and bounded
tools. Avoid "production-ready," "secure by default," "universal portability,"
or a claim that fake answers establish model quality. The evidenced runtime
target is Linux arm64 on Debian/glibc; hosted checks passed on Ubuntu x86-64.
Other workloads require compatibility
checks. This repository has no customer deployment evidence.

The next evaluation should test policy access control, prompt injection,
retrieval quality and citation entailment using approved data. A team adopting
it owns those decisions and its runtime policies. Review the
[verification evidence](verification-report.md) before proposing a runtime demo.

No personal or corporate author identity has been selected. This is a factual
explainer, not a Docker corporate announcement or an account of an author's
customer experience. The repository has been shared privately on GitHub; no kit image or corporate announcement has been published.

## docs/blog-outline.md

# Proposed blog outline

Working angle: **Follow a policy answer from a Markdown section to its citation**.
Audience: Python developers and AI platform engineers evaluating internal
support assistants. This proposes a post; it is not an approved new-blog draft.
For the existing product story, read the [product overview](product-overview.md)
and [marketing brief](marketing-brief.md). The [README quickstart](../README.md#quickstart-without-a-paid-credential)
and [developer guide](user-guide.md) provide the runnable journey.

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
   Distinguish the descriptor (`langchain.yaml`), file-overlay recipe
   (`langchain.dockerfile`) and agent guidance (`langchain-context.md`) from the
   policy-QA project in `sample/`. Explain how `sample/sbxenv.yaml` declares the
   pinned shell workload, local mixin and repository workspace. The mixin's
   agent-context request grants no model access, credentials or extra mounts.
6. Close with the decisions a platform team still owns: approved data and
   provider access, runtime policy tests, access control and realistic evaluation.

Use the repository's [guide](user-guide.md) and [verification report](verification-report.md)
as reader-visible supporting evidence. Do not invent a customer story, personal
failure anecdote or deployment results.
[Hosted workflow run 37961247968](https://github.com/shelajev/langchain-policy-lab/actions/runs/37961247968)
passed; that is execution evidence, separate from the workflow definition.
Actual composed SBX execution and live Gemini sample validation remain unrun
human handoffs. The credential-free deterministic journey does not establish
live-model quality or runtime policy enforcement.

## Pending author gates

- Select and approve a personal and/or explicitly chosen corporate identity.
- Agree on the post's angle and outline with that author.
- Run the pinned blog-writer package's full new-blog workflow, including its
  identity/voice evidence gates, if a finished post is requested.
- Approve publication destination and any product/security claims separately.

These optional gates do not block the kit, sample or neutral guide. No post or
kit image has been published. The repository has been shared privately on GitHub.

