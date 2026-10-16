# Run your LangChain in Docker Sandboxes

Bring an existing Python app, inspect its access needs, and generate a reviewable
v3 mixin for Docker Sandboxes. The app runs inside the sandbox, not just the
coding agent that edits it. Start with the [tutorial](docs/run-your-langchain-in-docker-sandboxes.md)
or the [step-by-step guide](docs/user-guide.md).

## Try the existing-app journey

An existing `agent.py` plus dependencies works without moving it into `src/`:

```bash
python3 skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py inspect --project examples/single-file-agent --entrypoint agent.py
```

The [single-file example](examples/single-file-agent/README.md) shows reviewed
lock setup. The larger example below exercises data paths and optional access.

Prerequisites: Python 3.11+ for inspection; uv 0.9.26 and Python 3.13.7 for the
example; Docker buildx and the pinned [kit-tck installer](scripts/install-ci-tools.sh)
for builds. Runtime needs a supported host with Docker Sandboxes and `sbx`.

From this repository root:

```bash
bash scripts/check-example.sh
python3 skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py inspect --project examples/ticket-triage --entrypoint src/ticket_triage/app.py
python3 skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py generate --project examples/ticket-triage --entrypoint src/ticket_triage/app.py --answers examples/ticket-triage.answers.json --out /tmp/my-ticket-triage-kit
python3 skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py explain --manifest /tmp/my-ticket-triage-kit/kit-manifest.json
bash scripts/check-skill.sh
bash scripts/check-generated-kit.sh /tmp/fresh-ticket-triage-layout
```

Use fresh output/layout paths. The answers are reviewed decisions for **this
synthetic app**, not defaults for yours. The helper does not import source,
resolve dependencies or grant access. It asks about inferred resources and
dynamic endpoints; generation requires explicit decisions and reasons.

On your approved host, inspect the environment before creating it:

```bash
sbx env plan ./examples/ticket-triage-kit/sbxenv.local.yaml
sbx env run --detach ./examples/ticket-triage-kit/sbxenv.local.yaml
sbx env exec ./examples/ticket-triage-kit/sbxenv.local.yaml -- sh -lc 'cd /opt/ticket-triage/app && python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model'
sbx env rm ./examples/ticket-triage-kit/sbxenv.local.yaml
```

The [host acceptance handoff](docs/acceptance-handoff.md) covers credential
binding, separately approved real-model calls, denied-operation checks and the
mount-free cloud equivalent. Cloud execution is not production serving.

## Use a coding agent, or work manually

Ask your agent to read [the repository skill](skills/langchain-sandbox-kit/SKILL.md):

> Package my LangChain app at ./ticket-triage to run in Docker Sandboxes. Inspect
> it without executing it, ask about unresolved access, and show packaging before
> requesting any permissions.

For normal discovery **in your own project**, copy the entire skill folder into
`.agents/skills/langchain-sandbox-kit/` (Codex) or
`.claude/skills/langchain-sandbox-kit/` (Claude Code). Both support symlinks. Its
relative scripts/templates/references are required. This repo leaves ACR-managed
agent folders alone and installs nothing into personal host skill directories.
See [source provenance](docs/provenance.md). The [manual path](docs/user-guide.md)
shows how to adapt a single-file kit template to your own app, dependencies,
launch command and permissions without running the helper.

## What has actually passed?

| Evidence class | Current status |
| --- | --- |
| Offline app + helper tests, source/build | PASS |
| Generated v3 artifact TCK | PASS |
| Read-only, nonroot, network-none container probe | PASS, **not SBX confinement proof** |
| Actual local SBX and cloud SBX | **NOT RUN**, host acceptance required |
| Live application model | PASS: one approved synthetic ticket in the implementation sandbox, **not local/cloud SBX acceptance** |

Exact commands and logs: [runtime matrix](docs/evidence/runtime-matrix.md).
A kit requests capabilities; the host decides. Review effective composition.
Isolation does not solve prompt injection, answer correctness or side effects
on allowed services. Keep real `.env` and private files out of contexts/images.

## Supporting example: policy lab

The earlier retrieval/tool lab remains at `sample/`, packaged by `langchain.yaml`
and `langchain.dockerfile`. See the [policy-lab guide](docs/policy-lab-guide.md).
Its [checks](scripts/check-sample.sh), build/TCK and filesystem probe continue
in CI; it is a supporting fixture, not the primary product journey.
