# Run your LangChain app in Docker Sandboxes

This repository contains a coding-agent skill that generates a
[Docker Sandboxes](https://docs.docker.com/ai/sandboxes/) kit for an existing
LangChain app, and a learning path that walks through it with a single-file
example. The kit adds your unchanged app, its locked Python environment and
reviewed network and credential requests to Docker's `shell` agent, so `sbx`
can run the app with only the access it needs.

**Start here:** [Run your LangChain app in Docker Sandboxes](docs/run-your-langchain-in-docker-sandboxes.md)

The guide covers, in order:

1. Giving your coding agent the skill, and keeping the coding agent's provider
   separate from your app's model provider (Gemini, OpenAI, Anthropic, others).
2. Locking the app's dependencies and generating the kit.
3. Reviewing `PERMISSIONS.md`, the descriptor and `RUN.md`.
4. Creating the sandbox with `sbx run shell --kit` and running the app offline.
5. Storing the app's key with `sbx secret set` and running it against the model.
6. Optionally, Docker Sandboxes cloud and publishing the kit to Docker Hub.

## What's here

| Path | Contents |
| --- | --- |
| [skills/langchain-sandbox-kit/](skills/langchain-sandbox-kit/SKILL.md) | The skill: `SKILL.md`, the inspection/generation helper, templates, references and tests. Copy the whole folder into your project's `.claude/skills/` or `.agents/skills/`. |
| [examples/single-file-agent/](examples/single-file-agent/README.md) | The primary example: one `agent.py` with a Gemini model and an offline `--fake-model` mode |
| [examples/single-file-agent-kit/](examples/single-file-agent-kit/RUN.md) | The kit the skill generates for it, committed for comparison |
| [examples/ticket-triage/](examples/ticket-triage/README.md) and its `-kit` | A packaged `src/` app with data files, a runtime status URL and a webhook |
| [docs/user-guide.md](docs/user-guide.md) | Skill reference: helper commands, answers file, generated files, checks |
| [docs/docs-team-handoff.md](docs/docs-team-handoff.md) | Summary for the documentation team: audience, outcomes, evidence and open decisions |

The helper needs only Python 3.11+. It reads the app as text and never runs
it, and it never grants access by itself: every network host and credential in
a kit comes from a decision the developer made and wrote down with a reason.

## Checks

```bash
export UV_EXCLUDE_NEWER=P7D
bash scripts/check-example.sh
bash scripts/check-skill.sh
bash scripts/check-single-file.sh
python3 scripts/check-doc-links.py
```

See [repository checks](docs/user-guide.md#repository-checks) for the full list.
Container probes check the generated artifact and its launch command; they are
not evidence of sandbox policy enforcement. The [acceptance handoff](docs/acceptance-handoff.md)
lists the host-side sandbox checks.

## Supporting material

The earlier policy-QA lab in `sample/`, packaged by `langchain.yaml`, remains
as a test fixture with its own [guide](docs/policy-lab-guide.md). The
`examples/*-direct/` directories back internal helper tests and are not part of
the learning path. The [validation summary](docs/acceptance-handoff.md) records
the native sandbox checks.
