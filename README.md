# LangChain Policy Lab for Docker Sandboxes

This repository demonstrates how Docker Sandboxes can give a LangChain developer
a reusable development environment and a working project to learn from. We built
a **v3 kit mixin**, a **sample enterprise policy assistant**, and a **developer
guide** that connects the two.

A developer's first task is concrete: answer “What can I expense on a business
trip?” from company policy documents, show the source of the answer, and calculate
a meal allowance. The sample uses fictional documents so a team can try that
workflow without uploading employee data or obtaining a model API key.

## Start here

| Reader | What to read |
| --- | --- |
| SBX product manager: what did we build, and why? | [Product overview and developer story](docs/product-overview.md) |
| LangChain developer: how do I try it? | [Step-by-step developer guide](docs/user-guide.md) |
| Platform engineer: what goes into a sandbox? | [Kit descriptor](langchain.yaml), [image recipe](langchain.dockerfile), and [sample environment](sample/sbxenv.yaml) |
| Reviewer: what works, and what remains untested? | [Verification report](docs/verification-report.md) and [independent QC report](docs/qc-delivery-report.md) |
| Someone explaining the project to others | [Marketing brief](docs/marketing-brief.md) and [proposed blog outline](docs/blog-outline.md) |

## What is in the repository?

- **The kit:** a Docker Sandboxes v3 mixin that packages Python, pinned LangChain
  dependencies, the sample application, and guidance for the coding agent. A mixin
  adds these to an existing workload rather than supplying its own operating
  system or agent. It is built locally; there is no published Docker Hub image.
- **The sample project:** a small policy assistant with retrieval, cited answers,
  meal and receipt tools, and an evaluation suite. The default model returns
  retrieved text deterministically. Optional Gemini support provides a path to
  a real model once provider access is approved.
- **The sandbox declaration:** `sample/sbxenv.yaml` shows how to combine the
  pinned shell workload with this local kit and the project workspace.
- **The guide and checks:** a runnable developer journey, tests, kit build and
  conformance checks, and a GitHub Actions workflow. The marketing brief and blog
  outline describe how the example could be presented; a finished blog post has
  not been written.

## What has been demonstrated?

Independent review passed 49 tests, 11 evaluation cases, and 19 kit conformance
checks. The bundled application also ran in a Debian filesystem probe without
system Python, as a non-root user, with networking disabled and a read-only root
filesystem. The [first hosted GitHub Actions run](https://github.com/shelajev/langchain-policy-lab/actions/runs/37961247968)
passed as well.

The remaining product demonstration is the **actual composed SBX environment**:
launching the workload plus mixin, checking the resulting environment, and
verifying runtime policy enforcement. That has not been run. Live Gemini sample
validation is also pending. The current result is a tested learning lab, with
those runtime checks explicitly handed off to a human.

## Try the sample

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

A Docker Sandboxes kit is an OCI (Open Container Initiative) image: its layers
carry files and its **v3 descriptor** declares what the sandbox runtime must
provide. A workload kit supplies the base operating system and agent launch.
A mixin overlays tools and environment values onto that workload; runtime
composition combines them into a sandbox. Agent context is packaged guidance
text delivered for the agent to read, not input data received from the workload.

`langchain.yaml` is a v3 **mixin**: it adds a bundled interpreter, locked
dependencies and the sample to an existing workload. It owns no entrypoint or
workload user. Its only typed request is agent context. It requests no network,
credentials, extra mounts or privilege. Linux glibc compatibility is deliberately
narrow: local evidence covers arm64 on Debian 12, not Alpine or arbitrary bases.

From the root, with Docker/Buildx, Go and curl available:
kit-tck is Docker's kit artifact conformance checker; it checks the packaged
descriptor/layers, not whether a composed sandbox runs or enforces policy.
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
the first hosted workflow passed after this repository was pushed to GitHub.

## Next steps

- Read [the full guide](docs/user-guide.md) for failure handling, version pins,
  optional approved Gemini calls and the HUMAN Docker Sandboxes journey.
- `sbx` is the Docker Sandboxes command-line tool. `sample/sbxenv.yaml` is its
  environment configuration file, selecting a pinned shell workload plus this local mixin;
  CLI grammar was checked against official sbx **v0.47.0** help. Assembled SBX
  runtime and policy checks are optional and not run here.
- [Verification report](docs/verification-report.md) separates observed checks
  from unrun ones; [provenance](docs/provenance.md) identifies primary APIs/tools.
- [Marketing brief](docs/marketing-brief.md) and [proposed outline](docs/blog-outline.md)
  are neutral drafts; author selection and publication gates remain pending.
