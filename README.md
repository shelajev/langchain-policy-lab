# Run your LangChain app in Docker Sandboxes

This repository gives you two things: a coding-agent skill that generates a
[Docker Sandboxes](https://docs.docker.com/ai/sandboxes/) kit for an existing
LangChain app, and a learning path built around a single-file example.

A kit packages your unchanged app, its locked Python environment and requested
access. This one is a **mixin**: `sbx` adds it to Docker's `shell` workload,
which supplies the operating system and shell. The generated text files let you
review what will be installed and requested before creating the sandbox.

**Start here:** [Run your LangChain app in Docker Sandboxes](docs/run-your-langchain-in-docker-sandboxes.md)

## Prerequisites and learning path

Running the full walkthrough on your host machine requires Python 3.11+ (for
the inspection helper), `uv`, Git, Docker with local Buildx, and the `sbx` CLI.
Use a coding agent signed in to its own provider, or the guide's direct helper
commands. A Gemini API key is needed only for the final live run.
Keep one boundary clear from the start: whatever model or account powers your
coding agent on the host is separate from the model provider and API key your
LangChain app uses inside the sandbox guest.

The guide covers the workflow in order:

1. Giving your coding agent the skill, while keeping the coding agent's model
   and account separate from your app's runtime model provider (Gemini, OpenAI,
   Anthropic, or others).
2. Locking the app's Python dependencies and generating the kit on the host.
3. Reviewing `PERMISSIONS.md`, the kit descriptor (`NAME.yaml`), and `RUN.md`.
4. Creating the sandbox with `sbx run shell --kit` and running the app offline
   inside the guest.
5. Storing the app's API key on the host with `sbx secret set` and running it
   against the live model provider.
6. Optionally, exploring Docker Sandboxes cloud and publishing the kit to
   Docker Hub (both paths are optional and have not been run or tested here).

## How access review and boundaries work

The helper (`skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py`) needs
only the Python 3.11+ standard library. It parses your app's source and dependency files,
never imports or runs the app, and never grants access by itself. Every network
host and credential in a generated kit comes from an explicit `allow`, `deny`,
or `out-of-scope` decision you record with a reason.

Keep two boundary limits in mind when reviewing a kit:

- Adding an `allow` request to a kit does not make the composed sandbox policy
  exclusive. Other grants from the base agent or sandbox configuration can still
  widen effective access, while explicit `deny` rules win over allows.
- Static inspection checks imports, environment variables, literal URLs,
  runtime-built URLs, file reads, and unparseable files, rather than tracing
  dynamic runtime behavior.

## What's here

| Path | Contents |
| --- | --- |
| [skills/langchain-sandbox-kit/](skills/langchain-sandbox-kit/SKILL.md) | The skill: `SKILL.md`, the inspection/generation helper, templates, references and tests. Copy it into the coding workspace's `.claude/skills/` or `.agents/skills/`; the walkthrough uses a parent workspace outside the app. |
| [examples/single-file-agent/](examples/single-file-agent/README.md) | The primary example: one `agent.py` with a Gemini model and an offline `--fake-model` mode |
| [examples/single-file-agent-kit/](examples/single-file-agent-kit/RUN.md) | The kit the skill generates for it, committed for comparison |
| [examples/ticket-triage/](examples/ticket-triage/README.md) and its `-kit` | A packaged `src/` app with data files, a runtime status URL and a denied webhook example |
| [docs/user-guide.md](docs/user-guide.md) | Skill reference: helper commands, working directories, answers file, generated files, checks |
| [docs/docs-team-handoff.md](docs/docs-team-handoff.md) | Summary for the documentation team: audience, outcomes, evidence and open decisions |

## Checks

These checks are for repository contributors changing the committed fixtures;
you do not need them to follow the main tutorial. Run them from this
repository's root in an authorized build environment. `UV_EXCLUDE_NEWER=P7D`
keeps dependency resolution at least seven days behind new package releases.
`kit-tck` is the kit-format conformance checker, not a sandbox runtime test:

```bash
export UV_EXCLUDE_NEWER=P7D
bash scripts/check-example.sh
bash scripts/check-skill.sh
bash scripts/check-single-file.sh
python3 scripts/check-doc-links.py
```

See [repository checks](docs/user-guide.md#repository-checks) for the full list
and build prerequisites (`kit-tck`, Docker, Buildx). Container probes check the
generated artifact and its launch command with networking off; they are not
evidence of sandbox policy enforcement or credential injection. Host-side native
sandbox checks are recorded in the [acceptance handoff](docs/acceptance-handoff.md).

## Supporting material

The earlier policy-QA lab in `sample/`, packaged by `langchain.yaml`, remains in
the repository as a test fixture with its own [guide](docs/policy-lab-guide.md).
Its native and live sandbox checks have not been run and are distinct from the
single-file kit's native and live pass evidence in the
[validation summary](docs/acceptance-handoff.md). The `examples/*-direct/`
directories back internal helper tests and are not part of the learning path.
