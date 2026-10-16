# Run your LangChain in Docker Sandboxes

Run your existing `agent.py` or Python project in a shell sandbox, with reviewed
dependencies and deliberate access. Keep its layout; a reusable kit is optional.
Start with the [tutorial](docs/run-your-langchain-in-docker-sandboxes.md) for the
manual and coding-agent routes, or the [guide](docs/user-guide.md).

## Quick path: direct execution

From this repository root, inspect the ready-locked single-file example, then
prepare a separate sanitized workspace and access plan:

```bash
python3 skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py inspect --project examples/single-file-agent --entrypoint agent.py
python3 skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py direct --project examples/single-file-agent --entrypoint agent.py --answers examples/single-file-agent.answers.json --out /tmp/my-agent-direct
```

Use a fresh output directory. Review `ACCESS.md`, `RUN.md`, `setup-deps.sh`,
`sbxenv.yaml` and `workspace/` before approving anything. The answers belong to
this synthetic fixture, not your app. For an unstructured `agent.py` plus
requirements, the [tutorial](docs/run-your-langchain-in-docker-sandboxes.md)
shows normal reviewed lock creation and matching raw-fixture answers.

Inspection needs Python 3.11+ and never imports source. The direct plan preserves
included files byte-for-byte, excludes secrets/private files, and mounts only
`workspace/`. It selects the official pinned shell workload, not a generated
mixin. The shell has Python; setup verifies and installs uv inside the sandbox,
then installs the locked dependencies there. No app source runs on the host.

On a supported, approved Docker Sandboxes host, follow the generated `RUN.md`
in order: existing credential, plan/create, scoped policy, in-sandbox setup,
remove bootstrap grants, launch, denied checks and cleanup. All SBX runtime
steps are **NOT RUN here**. After that setup, an offline app check is:

```bash
sbx env exec /tmp/my-agent-direct/sbxenv.yaml -- .venv/bin/python agent.py --fake-model
```

For a real model call, approve input, budget and credential use separately.
Direct uses built-in service `google`; the optional generated kit uses its
own `gemini` service. Never copy a key into YAML or the workspace. Inspect
inherited policy: one narrow allow does not cancel broader existing grants.

## With a coding agent, or manually

Ask your agent to read [the repository skill](skills/langchain-sandbox-kit/SKILL.md):

> Run my existing LangChain app at ./examples/single-file-agent in Docker
> Sandboxes. Inspect agent.py without executing it, ask about unresolved access,
> and prepare a direct-run plan. Preserve the app; reusable packaging is optional.

For discovery **in your own project**, copy the whole skill folder into
`.agents/skills/langchain-sandbox-kit/` (Codex) or
`.claude/skills/langchain-sandbox-kit/` (Claude Code). Keep scripts, templates
and references together; do not install into host-global skill directories.
The [manual tutorial](docs/run-your-langchain-in-docker-sandboxes.md) writes
an environment and sanitized workspace by hand without the helper.

## Optional: reusable kit

LangChain is ordinary Python. A kit packages environment, dependencies and
policy for repeatable distribution or cloud baking; it is not a per-file
conversion or a prerequisite for the first local run. Existing kit generation,
manual template edits and build/TCK checks remain in the [guide](docs/user-guide.md).
The larger [ticket-triage example](examples/ticket-triage/README.md) adds data,
status and webhook questions without changing the direct-first workflow.

Cloud cannot mount your host workspace. It requires an approved transfer or
baked kit, separate secrets/bindings and cloud policy. The host reports cloud
diagnose passed authentication/API/subscription; actual cloud runtime remains
**NOT RUN**, as does local SBX. Ordinary container success is not SBX confinement.
The [host handoff](docs/acceptance-handoff.md) lists allowed/denied checks.
Isolation does not solve prompt injection or side effects on allowed services.

## Supporting example: policy lab

The earlier retrieval/tool lab remains at `sample/`, packaged by `langchain.yaml`
and `langchain.dockerfile`. See the [policy-lab guide](docs/policy-lab-guide.md).
Its [checks](scripts/check-sample.sh), build/TCK and filesystem probe continue
in CI; it is a supporting fixture, not the primary product journey.
