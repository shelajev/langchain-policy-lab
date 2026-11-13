---
title: Run your LangChain app in Docker Sandboxes
linkTitle: LangChain in Docker Sandboxes
description: Generate a sandbox kit for an existing LangChain app with a coding-agent skill, review its permissions, add the model key as a sandbox secret and run the app with sbx.
summary: Package an existing LangChain app as a reviewed Docker Sandboxes kit and run it with only the access it needs.
tags: [ai, sandboxes, langchain, python]
params:
  time: 30 minutes
---

# Run your LangChain app in Docker Sandboxes

A LangChain app is ordinary Python, but at runtime it reads files, calls a model
provider with an API key and can make any other HTTP request its code builds.
Running it on your machine gives it everything your user account can reach.
[Docker Sandboxes](https://docs.docker.com/ai/sandboxes/) runs it in an
isolated sandbox instead, where you decide which files it sees, which hosts it
can reach and which credentials it can use.

A **kit** describes that setup for one app: the app's files, its locked Python
environment and the network and credential access it needs. In this guide, a
coding agent writes the kit for you with a skill from the
[langchain-policy-lab](https://github.com/shelajev/langchain-policy-lab) repository, you review it, and `sbx` runs it.

In this guide, you'll learn how to:

- Give your coding agent the kit-generation skill, separately from the model
  provider your app uses
- Generate a kit for an existing LangChain app without changing the app
- Review the generated permissions and launch instructions
- Store the app's model API key as a sandbox secret with `sbx secret set`
- Run the app in a sandbox, first offline and then against the real model

## Prerequisites

- [Docker Sandboxes](https://docs.docker.com/ai/sandboxes/) with the `sbx` CLI
  on a supported host. Run `sbx run --help` and check that it lists the
  `shell` agent and the `--kit` flag.
- A coding agent that can read a skill folder, such as
  [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) or
  [Codex CLI](https://developers.openai.com/codex/cli), signed in with its own
  provider account.
- Python 3.11 or later on your machine, for the skill's inspection and
  generation script, which needs only the standard library.
- [uv](https://docs.astral.sh/uv/getting-started/installation/) to lock the
  app's dependencies. We tested the commands with uv 0.9.26.
- A Google AI Studio [Gemini API key](https://aistudio.google.com/apikey) for the
  live run at the end. Everything before that step works without a key.
- Basic familiarity with LangChain and a terminal.

## How the pieces fit

Two different AI tools appear in this guide, and they use separate providers
and separate keys:

- Your **coding agent** (Claude Code, Codex or another) reads the skill, inspects
  your app and writes the kit. It uses whatever provider it is signed in to.
  It does not run in the app's sandbox and never needs the app's key.
- Your **LangChain app** calls its own model provider at runtime. The example
  app uses Gemini through `langchain-google-genai`. The kit keeps that choice
  and asks for access to Gemini only.

A Claude Code or Codex session can generate a kit for a Gemini app, and the
other way round. The skill does not switch your app to the coding agent's
provider.

The generated kit is a **mixin**. Docker's built-in `shell` agent is the
**workload**: it provides the sandbox's operating system, user and shell. The
mixin adds your app under `/opt/<kit-name>/app`, a Python environment built from
your lock file under `/opt/<kit-name>/venv`, and the network and credential
requests that Docker Sandboxes applies when it creates the sandbox.

## Set up a working directory

Clone the langchain-policy-lab repository next to the app you want to
package. We use its raw example app, a single `agent.py` with a `requirements.txt`,
in place of your own app:

```console
$ mkdir ~/langchain-kit-demo && cd ~/langchain-kit-demo
$ git clone https://github.com/shelajev/langchain-policy-lab.git
$ cp -R langchain-policy-lab/skills/langchain-sandbox-kit/tests/fixtures/raw-agent my-agent
$ ls my-agent
agent.py  requirements.txt
```

<!-- VERIFY: final public location of this repository before publication. -->

`agent.py` classifies a synthetic support ticket. With `--fake-model` it uses
LangChain's `FakeListChatModel` and never calls a provider; without it, it calls
`gemini-2.5-flash`:

```python
if args.fake_model:
    os.environ["LANGSMITH_TRACING"] = "false"
    model = FakeListChatModel(responses=['{"category":"technical","ticket_id":"T-101"}'])
else:
    model = init_chat_model("gemini-2.5-flash", model_provider="google_genai", max_output_tokens=256, thinking_budget=0, response_mime_type="application/json")
```

`thinking_budget=0` turns off Gemini 2.5's thinking tokens, which would
otherwise use up the 256-token output limit, and `response_mime_type` asks
Gemini for plain JSON instead of a Markdown code block.

All the commands that follow run from `~/langchain-kit-demo`, unless a step
says to change directory.

## Lock the app's dependencies

A kit has to build the same Python environment every time, so the skill needs
exact versions. It accepts a uv project: `pyproject.toml` with exact direct
pins, a `uv.lock` with hashes from PyPI, and a `.python-version` file. The
example has only an unpinned `requirements.txt`. We create the three project
files with uv, next to `agent.py`, without changing or running the app:

```console
$ cd my-agent
$ uv init --bare --no-workspace --name single-file-agent --python 3.13.7
$ uv python pin 3.13.7
$ uv add --no-sync 'langchain==1.4.4' 'langchain-core==1.6.9' 'langchain-google-genai==4.4.0'
$ uv lock
$ cd ..
```

`--python 3.13.7` and `uv python pin` set the Python version the kit builds
with; uv downloads that interpreter inside the kit build, so it doesn't have to
be installed on your machine. `--name` is the project name written into
`pyproject.toml`. `--bare` creates only a minimal `pyproject.toml`, `--no-workspace` keeps uv
from attaching the app to a parent project, and `--no-sync` records the
dependencies without creating a virtual environment. The versions are the ones
we chose for this example. For your own app, pick versions that you have
tested with it. If your app already has a uv lock, keep it.

> [!TIP]
> If you set a uv package-age limit such as `UV_EXCLUDE_NEWER="7 days"`, uv
> records it in `uv.lock`. The generated kit carries the same setting into its
> container build, which runs `uv sync --locked`, so the build accepts the lock.

## Add the skill to your coding agent

The skill is the folder `skills/langchain-sandbox-kit/`. Copy the whole folder,
because `SKILL.md` relies on the helper script, templates and references next
to it. Put it in the directory where you run your coding agent, not inside the
app:

```console
$ mkdir -p .claude/skills
$ cp -R langchain-policy-lab/skills/langchain-sandbox-kit .claude/skills/
```

That is the location Claude Code reads project skills from. For Codex, use
`.agents/skills/` instead of `.claude/skills/` in both commands. For another
agent, point it at `langchain-policy-lab/skills/langchain-sandbox-kit/SKILL.md`
in your prompt.

Sign in to your coding agent the way you usually do. Claude Code uses your
Anthropic account or `ANTHROPIC_API_KEY`, Codex uses your OpenAI account or
`OPENAI_API_KEY`, and Gemini CLI uses your Google account or a Gemini key.
That login is only for the coding agent.

> [!NOTE]
> You can also run the coding agent itself in a sandbox, for example with
> `sbx run claude` or `sbx run codex`. That sandbox gets the agent's own key,
> such as `sbx secret set anthropic` for Claude. It is separate from the
> sandbox you create for the app later in this guide.

## Generate the kit

Start your coding agent in `~/langchain-kit-demo` and ask it to use the skill:

```text
Use the langchain-sandbox-kit skill to generate a Docker Sandboxes kit for the
LangChain app in ./my-agent. Its entrypoint is agent.py. Don't run or change the
app. Ask me about anything the inspection can't decide, write the kit to
./my-agent-kit, and then show me PERMISSIONS.md and RUN.md.
```

The agent runs the skill's helper script for you, in two steps. First it
inspects the app. The inspector parses the source and dependency files as
text, never imports or runs them, and turns everything that might need access
into a question. This app produces 12 questions; four of them look like this:

```text
- 1313c81151bf928b: env-name: LANGSMITH_TRACING; allow with reason, deny, or out-of-scope? (agent.py:14)
- 2f23ceb98c1a74c0: provider-host: generativelanguage.googleapis.com; allow with reason, deny, or out-of-scope? (pyproject.toml:8)
- 3f81b54c78a07b5d: provider-package: langchain-google-genai; allow with reason, deny, or out-of-scope? (pyproject.toml:8)
- fcdff6b3142ba65f: env-name: GOOGLE_API_KEY; allow with reason, deny, or out-of-scope? (pyproject.toml:8)
```

Each question takes one of three answers, with a reason:

- **allow** puts the access in the kit, for example a host in the network
  allow list or the provider's credential.
- **deny** records that the app must not use it. A denied finding that names
  a host puts that host in the kit's deny list; other denials are recorded in
  `PERMISSIONS.md` and get no access.
- **out-of-scope** records that the finding needs no access of its own, such as
  a core library or a second name for the same key.

Here are all 12 findings for this app and the answers a developer who knows
it would give. `requirements.txt` lists `langchain` and
`langchain-google-genai`, so the Gemini items appear once for it and once for
`pyproject.toml`. The inspector doesn't ask about `langchain` itself, because
the core package makes no network calls of its own.

| Finding | Where | Answer | Reason |
| --- | --- | --- | --- |
| `langchain-google-genai` (provider package) | `pyproject.toml`, `requirements.txt` | allow, credential `google` | The app uses Gemini only |
| `generativelanguage.googleapis.com` (provider host) | `pyproject.toml`, `requirements.txt` | allow | The Gemini API host |
| `GOOGLE_API_KEY` (environment variable) | `pyproject.toml`, `requirements.txt` | allow | The variable the Gemini SDK reads |
| `GEMINI_API_KEY` (environment variable) | `pyproject.toml`, `requirements.txt` | out-of-scope | An alias of the same key; one is enough |
| `langchain-core` (dependency) | `pyproject.toml` | out-of-scope | Library code, no access of its own |
| `LANGSMITH_TRACING` (environment variable) | `agent.py` line 14 | deny | Tracing stays off |
| LangSmith tracing (`api.smith.langchain.com`, suggested by the inspector) | `agent.py` | deny | Tracing stays off; the kit never allows this host, so its deny list stays empty |
| Scope confirmation | `agent.py` | allow | Confirms the app reads no files and calls nothing but Gemini |

The agent never asks for the key itself.

The agent then writes your decisions to an answers file and generates the kit.
You don't need to run anything here; the agent's last command looks like this
and prints:

```text
python3 .claude/skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py generate \
    --project my-agent --entrypoint agent.py --answers answers.json --out my-agent-kit
generated reviewable kit; read RUN.md and PERMISSIONS.md. No capabilities granted or runtime started
```

### Without a coding agent

If your coding agent already wrote `./my-agent-kit`, skip to
[Review the kit and its permissions](#review-the-kit-and-its-permissions).
Otherwise you can run the same two steps yourself from `~/langchain-kit-demo`.
`inspect` prints the 12 questions and saves them, with their IDs, to
`inspection.json`. `generate` then reads the answers. The repository includes
reviewed answers for this example app, matching the table above, in
`langchain-policy-lab/examples/raw-agent.answers.json`:

```console
$ python3 langchain-policy-lab/skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py inspect \
    --project my-agent --entrypoint agent.py --json inspection.json
$ python3 langchain-policy-lab/skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py generate \
    --project my-agent --entrypoint agent.py \
    --answers langchain-policy-lab/examples/raw-agent.answers.json --out my-agent-kit
generated reviewable kit; read RUN.md and PERMISSIONS.md. No capabilities granted or runtime started
```

Those answers match this example only, because each question ID is derived
from the file, line and finding. For your own app, write one decision per
question from your `inspect` output, using the format in the
[skill reference](https://github.com/shelajev/langchain-policy-lab/blob/main/docs/user-guide.md#the-answers-file).

If the inspector finds something it can't resolve, such as a URL built at
runtime, it doesn't guess. Generation stops until you name the exact host or
deny it. It also refuses source files that contain something that looks like
a secret.

## Review the kit and its permissions

The generated directory contains:

```text
my-agent-kit/
├── .dockerignore
├── PERMISSIONS.md
├── RUN.md
├── app/
│   ├── .python-version
│   ├── agent.py
│   ├── pyproject.toml
│   └── uv.lock
├── kit-manifest.json
├── my-agent-kit-context.md
├── my-agent-kit.dockerfile
└── my-agent-kit.yaml
```

- `app/` is the snapshot that goes into the sandbox. `agent.py` is
  byte-for-byte the original, and `requirements.txt` is left out because the
  lock replaces it. Files such as `.env`, `private/`, keys and credential files
  are never copied.
- `my-agent-kit.yaml` is the kit descriptor. `my-agent-kit.dockerfile` builds
  `app/` and its locked environment, and `my-agent-kit-context.md` tells the
  agent in the sandbox how to run the app.
- `PERMISSIONS.md` lists every inspection finding with your decision and reason.
- `RUN.md` has the `sbx` commands for this kit.

Keep the directory name the same as the descriptor's name (`my-agent-kit`). The
kit format pairs `<name>.yaml` with `<name>.dockerfile` in a directory of the
same name.

Read the descriptor carefully. It asks for one network host and one credential:

```yaml
  - type: com.docker.sandbox/network-policy@1
    config:
      runtime:
        allow: ["generativelanguage.googleapis.com"]
        deny: []
  - type: com.docker.sandbox/credential@1
    optional: true
    config:
      service: google
      phase: runtime
      apiKey:
        name: GOOGLE_API_KEY
        proxyManaged: true
        inject:
          - domain: generativelanguage.googleapis.com
            header: x-goog-api-key
            format: "%s"
```

The network policy asks for one host at runtime. The credential entry asks for
the `google` secret and says how to use it: inside the sandbox,
`GOOGLE_API_KEY` holds a placeholder rather than your key, and the Docker
Sandboxes proxy puts the real key in the `x-goog-api-key` header only on
requests to `generativelanguage.googleapis.com`. `optional: true` lets the
sandbox start without the secret, which is what makes the offline run below
possible.

These are requests, not grants. Docker Sandboxes applies them when you create
the sandbox, combined with any host or organization policy. Other allow rules
can widen access, and explicit deny rules always win. `PERMISSIONS.md` also
lists what the kit does not protect against, such as prompt injection and
side effects on the provider you allowed.

## Create the sandbox and run the app offline

Create a sandbox from the `shell` agent with your kit added:

```console
$ sbx run --detach shell --kit ./my-agent-kit --name my-agent-kit ./my-agent-kit
```

<!-- Host-verified 2026-11-13 at aa2af15 with sbx v0.53.0 (single-file-agent-kit): exit 0, kit built, sandbox created detached. No approval prompt appeared on that configured host; don't promise one. -->

- `shell` is the agent. It's a plain shell sandbox with no coding agent in it.
- `--kit ./my-agent-kit` adds your kit. A local kit path has to start with `./`
  or `../`; a bare name means an agent or a sandbox.
- `--name my-agent-kit` names the sandbox, so the next steps can refer to it.
- The last argument is the workspace mounted into the sandbox. The app itself
  runs from its copy in `/opt/my-agent-kit/app`, so the workspace only needs to
  be harmless: we mount the generated kit directory, which holds only reviewed
  files, rather than `my-agent` or `~/langchain-kit-demo`.
- `--detach` creates the sandbox and prints its ID without opening a session.

If `sbx` asks you to approve anything while it builds the kit and creates the
sandbox, compare the request with `PERMISSIONS.md` before you accept.

Open a shell in the sandbox:

```console
$ sbx run --name my-agent-kit
```

Inside the sandbox, run the app with the kit's interpreter and the app's
offline flag:

```console
$ cd /opt/my-agent-kit/app
$ /opt/my-agent-kit/venv/bin/python agent.py --fake-model
{"category":"technical","ticket_id":"T-101"}
```

Use the full interpreter path. In the `shell` agent, `python` is the system
Python, which doesn't have LangChain installed, so `python agent.py` fails with
`ModuleNotFoundError: No module named 'langchain'`. Exit the shell when the
offline run works.

## Add the model secret and run against Gemini

Store your Gemini key as a secret for this sandbox only:

```console
$ sbx secret set google --sandbox my-agent-kit
```

<!-- Host-verified 2026-11-13: a sandbox-scoped google secret set after creation reached the running sandbox without restart (synthetic invalid value via stdin gave API_KEY_INVALID; removing it restored the global-backed live call). VERIFY: interactive prompt text with a real key was not observed. -->

`sbx` prompts for the value, so the key doesn't end up in your shell history.
Don't use `--token`, which takes the value on the command line, and don't put
the key in `my-agent-kit/`, a `.env` file or an environment variable passed to
the sandbox. `--sandbox` keeps the secret out of your other sandboxes; without
it, `sbx` stores the secret for all sandboxes. If your key lives in 1Password or
AWS Secrets Manager, `sbx secret set google --ref ...` stores a reference
instead.

Open a shell in the sandbox again:

```console
$ sbx run --name my-agent-kit
```

Inside the sandbox, run the app without `--fake-model`:

```console
$ cd /opt/my-agent-kit/app
$ /opt/my-agent-kit/venv/bin/python agent.py
```

This makes one real Gemini call and costs a small amount. The reply is a JSON
object for ticket `T-101`. The model chooses the category and may add fields, so
the exact text varies, for example:

```json
{
  "ticket_id": "T-101",
  "category": "export",
  "description": "report export fails",
  "priority": "high"
}
```

<!-- Host-verified 2026-11-13: sample is the native sandbox output, exit 0, with the host's existing global google credential injected by the proxy (not a scoped real key); policy log showed generativelanguage.googleapis.com:443 allowed. -->

To confirm that the sandbox blocks other destinations, still inside the
sandbox, request a host the kit doesn't allow:

```console
$ /opt/my-agent-kit/venv/bin/python -c "import urllib.request; urllib.request.urlopen('https://example.com', timeout=10)"
```

The command fails with a Python traceback instead of succeeding with no output. Exit the
sandbox shell, then check the policy log on your machine:

```console
$ sbx policy log my-agent-kit
```

Look for a blocked entry for `example.com`. A DNS error or a timeout on its own
doesn't prove the policy blocked the request; the log entry does.

<!-- Host-verified 2026-11-13: request failed with HTTP 403 (exit 1); policy log listed example.com:443 blocked, reason "No matching allow rule (default deny)". -->

## Choose the app's model provider

The skill has reviewed mappings for three LangChain provider packages. It
detects the package from your dependencies and fills in the host, secret
service, environment variable and header:

| Provider | LangChain package | Host | `sbx secret set` service | Environment variable | Header |
| --- | --- | --- | --- | --- | --- |
| Google Gemini (AI Studio) | `langchain-google-genai` | `generativelanguage.googleapis.com` | `google` | `GOOGLE_API_KEY` (also reads `GEMINI_API_KEY`) | `x-goog-api-key` |
| OpenAI | `langchain-openai` | `api.openai.com` | `openai` | `OPENAI_API_KEY` | `Authorization: Bearer` |
| Anthropic | `langchain-anthropic` | `api.anthropic.com` | `anthropic` | `ANTHROPIC_API_KEY` | `x-api-key` |

For an OpenAI app, the secret step is `sbx secret set openai --sandbox NAME`;
for an Anthropic app, `sbx secret set anthropic --sandbox NAME`. The generated
`RUN.md` always shows the right one.

Other setups need a manual decision, because hosts and authentication differ:

- **Vertex AI, Azure OpenAI and Amazon Bedrock** use different hosts and
  cloud authentication. They aren't covered by these mappings.
- **OpenAI-compatible gateways and custom base URLs** need the exact gateway
  host. Don't assume an OpenAI key or header works there.
- **Other providers.** `sbx secret set` also has services such as `groq`,
  `mistral`, `openrouter` and `xai`, but the skill has no reviewed LangChain
  mapping for them. Add the host and credential entry to the descriptor
  yourself from the provider's documentation.
- **LangSmith tracing** has no built-in `sbx` secret service. Keep tracing off,
  as in this example, unless you package it yourself.

The skill keeps the provider your app already uses. If you want a different
provider, change the app and its dependencies first, then generate the kit
again.

## Clean up

Make sure you've exited the sandbox shell, then remove the sandbox from your
machine:

```console
$ sbx rm my-agent-kit
```

`sbx rm` asks for confirmation, then removes the sandbox and the secrets scoped
to it. Secrets and policy rules you created globally stay; list them with
`sbx secret ls` and `sbx policy ls`.

## Optional: run the kit in Docker Sandboxes cloud

`sbx --cloud run` accepts the same kit. Cloud sandboxes have no host
workspace, so no path follows the agent:

```console
$ sbx --cloud run --detach shell --kit ./my-agent-kit --name my-agent-kit
```

We haven't run this kit in cloud sandboxes, so treat this section as a
starting point. `sbx --cloud --help` lists the commands your CLI supports in
cloud mode. A launch with a local kit builds it in Docker's cloud, which means
the contents of `app/` leave your machine. Cloud sandboxes also keep their own
secrets and network policy; your local secret doesn't carry over.

<!-- VERIFY: not run. Cloud secret commands and kit baking are documented in CLI help only. -->

## Optional: publish the kit to Docker Hub

A kit is an OCI artifact, so you can share it through a registry. This needs
Docker with Buildx and a `docker login` to Docker Hub. Pointing `-f` at the
descriptor makes Buildx build the kit (the descriptor's first line selects the
kit builder, which finds `my-agent-kit.dockerfile` by name). Build and push both
platforms in one command from the kit directory:

```console
$ cd my-agent-kit
$ docker buildx build . -f my-agent-kit.yaml --platform linux/amd64,linux/arm64 --push \
    -t docker.io/<your-namespace>/my-agent-kit:0.1.0
```

Others can then run `sbx run shell --kit <your-namespace>/my-agent-kit:0.1.0`.
Publishing shares your app's code and lock file with anyone who can pull the
image, so check the repository's visibility and what's in `app/` first. The
`sbx kit` command also has `push`, `sign` and `verify` subcommands; see
`sbx kit --help`.

<!-- VERIFY: not run. No kit was pushed while preparing this guide. -->

## Conclusion

You now have an existing LangChain app running in a sandbox that can reach
only its model provider, with the API key held by the proxy rather than in the
sandbox. The kit is a small directory of reviewable text files that you can
regenerate after you change the app, commit next to it, or publish for your
team.

The skill, the example app and the generated example kit are in the
[langchain-policy-lab repository](https://github.com/shelajev/langchain-policy-lab).

## Further reading

- [Skill reference](https://github.com/shelajev/langchain-policy-lab/blob/main/docs/user-guide.md): inspection,
  answers, exit codes and the repository's check scripts
- [Docker Sandboxes documentation](https://docs.docker.com/ai/sandboxes/)
- [The `shell` agent](https://docs.docker.com/ai/sandboxes/agents/shell/)
- [Sandbox kit specification](https://github.com/docker/sandbox-kit-spec)
- [LangChain chat model integrations](https://python.langchain.com/docs/integrations/chat/)
