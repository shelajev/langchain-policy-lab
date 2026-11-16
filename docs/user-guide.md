# Skill reference: langchain-sandbox-kit

This page is the reference for the skill used in
[Run your LangChain app in Docker Sandboxes](run-your-langchain-in-docker-sandboxes.md).
Use the main guide for a walkthrough, or this page directly as a reference
for app requirements, helper commands, answers, generated files and repository
checks.

Python 3.11+ is enough to run the inspection and generation helper in the
coding agent's authorized environment, on the host or in a separate sandbox. Locking dependencies, building kit images, and running
sandboxes also require `uv`, Git, Docker with local Buildx, and the `sbx` CLI.
Keep your coding agent separate from the app runtime: the coding agent uses
its own model and account to read the skill and drive the helper,
while the kit configures only your app's runtime model provider and
proxy-managed credential inside the sandbox guest.

## What the skill needs from your app

Because the kit builds the app's Python environment inside a container image
without pulling arbitrary git URLs or unpinned packages, the skill expects a
standard, hashed project layout:

- An entrypoint: a root `agent.py` (or any root `.py` file), or a module under
  `src/` for packaged apps. `--entrypoint` takes a file path such as
  `src/ticket_triage/app.py`, not the dotted module name used at launch. The
  app keeps its relative layout inside the kit.
- `pyproject.toml` with exact direct pins (`package==version`), a `uv.lock`
  whose artifacts come from public PyPI with SHA-256 hashes, and
  `.python-version` with an exact version such as `3.13.7`. Requirements-only
  apps need that conversion first; see
  [dependency setup](../skills/langchain-sandbox-kit/references/dependencies.md).
- Custom package indexes, VCS or path dependencies and `tool.uv.sources` are
  refused and need manual packaging.

## Helper commands

The helper is `skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py`. It
uses only the Python 3.11+ standard library, never imports or runs app code, never resolves dependencies and never starts a sandbox.

The commands below assume your working directory is the skill directory
(`skills/langchain-sandbox-kit/` in this repository, or
`.claude/skills/langchain-sandbox-kit/` or `.agents/skills/langchain-sandbox-kit/`
once copied into your project). If you run from the repository root or another
directory instead, pass the path to `sbx_langchain_kit.py` from there. `--project APP`,
`NEW_REPORT.json`, `ANSWERS.json`, and `--out NAME` resolve relative to your
current working directory. Replace these placeholders with absolute paths to
avoid ambiguity, especially if the skill is copied inside `APP`. The report,
answers and kit output must be outside `APP`: for example, project
`/work/my-agent`, report `/work/inspection.json`, answers `/work/answers.json`
and output `/work/my-agent-kit`. In helper commands, `NAME` is that output
path; its basename (`my-agent-kit`) must match the answers `name`. In generated
filenames and runtime commands below, `NAME` means that basename.

```bash
python3 scripts/sbx_langchain_kit.py inspect --project APP --entrypoint agent.py --json NEW_REPORT.json
python3 scripts/sbx_langchain_kit.py generate --project APP --entrypoint agent.py --answers ANSWERS.json --out NAME
python3 scripts/sbx_langchain_kit.py explain --manifest NAME/kit-manifest.json
```

- `inspect` prints one question per finding and writes the full report to a
  new file outside the project. Findings include provider packages and their
  default hosts, environment variable names, literal URLs, URLs built at
  runtime, file reads, `subprocess`/`socket` imports, unknown LangChain
  integrations, secret-like literals and files it could not parse.
The JSON report stores IDs and categories in `findings` and ready-to-read
questions in `questions`; it does not generate an answers skeleton. For
example, the committed single-file app emits this question:

```text
- 99e16f2b158c65a9: provider-package: langchain-google-genai; allow with reason, deny, or out-of-scope? (pyproject.toml:5)
```

Its corresponding `findings` entry is:

```json
{"confidence":"declared","file":"pyproject.toml","id":"99e16f2b158c65a9","kind":"provider-package","line":5,"value":"langchain-google-genai"}
```

Use each `id` as a key under `decisions`; copy IDs from your own current report,
not this example.

- `generate` refuses to run until every current finding has a decision. It
  writes the kit to a new directory outside the project, named to match the
  answers `name`.
- `explain` prints `PERMISSIONS.md` after verifying it against the manifest
  hash.

Exit codes: `0` success, `2` missing or stale answers, `3` unsafe or
unsupported input, `4` refused overwrite. `--force` replaces an earlier output
only when every file still matches the manifest, so it never overwrites your
edits.

## The answers file

The full contract is in
[answers.schema.md](../skills/langchain-sandbox-kit/references/answers.schema.md).
In short:

```json
{
  "name": "my-agent-kit",
  "launch": "python agent.py",
  "dataPaths": [],
  "decisions": {
    "3f81b54c78a07b5d": {"action": "allow", "credential": "google", "reason": "App uses Gemini only"},
    "1313c81151bf928b": {"action": "deny", "reason": "Tracing stays off"}
  }
}
```

- Every finding ID from the current inspection needs `allow`, `deny` or
  `out-of-scope` with a reason. Old or extra IDs are refused, so inspect again
  after changing the app.
- `hosts` lists exact lowercase host names for a decision, for example the host
  behind a URL the app builds at runtime. Wildcards and IP addresses need
  `allowBroad: true` and are flagged in `PERMISSIONS.md`.
- `credential` names the `sbx secret set` service (`google`, `openai` or
  `anthropic`) on the allowed provider-package decision. No secret value goes
  in the file.
- `dataPaths` lists the data and config files or directories the app reads, as
  relative paths. They are copied with the same layout.
- `launch` is the reviewed command run inside the sandbox guest, such as
  `python agent.py` or
  `python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model`.
  The command must start with `python`, not `python3`. The generated
  instructions replace it with `/opt/NAME/venv/bin/python` and change into
  `/opt/NAME/app` before running it.

Setting `"action": "allow"` adds a network or credential request to this kit
mixin; it does not make the effective composed sandbox policy exclusive. Other
grants from the base agent or sandbox configuration can still widen access,
while explicit `deny` rules win over allows.

## Generated files

Commands in `RUN.md` run on the host to build, configure secrets for, and
start the sandbox; paths under `/opt/NAME` live inside the sandbox guest image.

| File | Purpose |
| --- | --- |
| `NAME.yaml` | Kit descriptor: a mixin with agent context, runtime network allow/deny list and one optional proxy-managed credential per allowed provider |
| `NAME.dockerfile` | Builds `app/` with its locked environment under `/opt/NAME` on a pinned uv image; the final stage is an overlay containing only `/opt/NAME`, composed onto the workload image |
| `NAME-context.md` | Instructions for the agent in the sandbox guest: where the app is and how to run it |
| `app/` | Selected snapshot: the lock files, root Python files, `src/` and declared data paths |
| `.dockerignore` | Limits the build context to `app/` and the context file |
| `PERMISSIONS.md` | Every finding with its decision and reason, the allow/deny lists and what the kit does not protect |
| `RUN.md` | Host `sbx` commands for this kit: create, secret, run, clean up, plus optional unrun cloud and publishing steps |
| `kit-manifest.json` | Input, answers and output hashes for `explain` and `--force` |

Files and directories that never enter `app/`: `.env` and `.env.*` (except
`.env.example`), `private/`, `.git`, `.venv`, caches, `.claude`, `.codex`,
`.agents`, keys and credential files, plus anything your `.gitignore` or
`.dockerignore` excludes.

Boundary limits: static inspection does not execute code or catch dynamically
constructed behavior outside AST/text findings, the kit descriptor only requests
policy from `sbx` rather than enforcing network isolation in Python, and any
cloud or Docker Hub publishing steps in `RUN.md` are optional and unrun here.

## Provider mappings

See the provider table in the
[guide](run-your-langchain-in-docker-sandboxes.md#choose-the-apps-model-provider)
and [capabilities.md](../skills/langchain-sandbox-kit/references/capabilities.md).
Gemini maps to the `google` secret service. There is no `gemini` service in
`sbx secret set`.

## Worked examples in this repository

| Example | App | Generated kit | Answers |
| --- | --- | --- | --- |
| Single file, primary | [examples/single-file-agent](../examples/single-file-agent/README.md) | [examples/single-file-agent-kit](../examples/single-file-agent-kit/RUN.md) | [single-file-agent.answers.json](../examples/single-file-agent.answers.json) |
| Raw `agent.py` + `requirements.txt` | [raw-agent fixture](../skills/langchain-sandbox-kit/tests/fixtures/raw-agent/) | generated in the guide | [raw-agent.answers.json](../examples/raw-agent.answers.json) |
| Packaged app with data, a status URL and a webhook | [examples/ticket-triage](../examples/ticket-triage/README.md) | [examples/ticket-triage-kit](../examples/ticket-triage-kit/RUN.md) | [ticket-triage.answers.json](../examples/ticket-triage.answers.json) |

The `examples/*-direct/` directories and the helper's `direct` subcommand are
kept only as internal regression fixtures; the learning path uses kits.

## Repository checks

Run from the repository root on the host. Git, Docker, local Buildx and
`kit-tck` (built from
[docker/sandbox-kit-spec](https://github.com/docker/sandbox-kit-spec) at the
pin in [capabilities.md](../skills/langchain-sandbox-kit/references/capabilities.md))
are needed for the build checks.

```bash
bash scripts/check-skill.sh             # helper unit tests
bash scripts/check-single-file.sh       # single-file kit build, kit-tck, shell-workload probe
bash scripts/check-generated-kit.sh /tmp/NEW-layout   # ticket-triage kit
bash scripts/check-raw-single-file.sh   # raw app -> lock -> kit build
python3 scripts/check-doc-links.py
bash scripts/clean-checkout.sh          # everything, from a fresh clone
```

The probes compose the kit's overlay onto the pinned `docker/sbx-kit-shell`
image with networking off and run the command from `RUN.md`. They show that the
artifact and its launch command work; they are not evidence of sandbox
network policy or credential injection. See
[acceptance-handoff.md](acceptance-handoff.md) for the host-side sandbox checks
and the distinction between the single-file kit's native/live results and the
unrun policy-lab sample.
