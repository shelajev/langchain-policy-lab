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
