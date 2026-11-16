---
title: Run your LangChain app in Docker Sandboxes
linkTitle: LangChain in Docker Sandboxes
description: Generate a sandbox kit for an existing LangChain app with a coding-agent skill, review its permissions, add the model key as a sandbox secret and run the app with sbx.
summary: Package an existing LangChain app as a Docker Sandboxes kit, review its access requests and run it with sbx.
tags: [ai, sandboxes, langchain, python]
params:
  time: 30 minutes
---

# Run your LangChain app in Docker Sandboxes

A LangChain app is ordinary Python, which means running it directly under your
user account gives it everything your account can reach: local files, your
shell environment, and any HTTP endpoint its code builds. Running it inside
[Docker Sandboxes](https://docs.docker.com/ai/sandboxes/) gives it a separate
environment with a workspace, network policy and credential configuration you
can review. The effective access depends on the complete sandbox configuration,
not just the kit you add.

A **kit** is how you describe that setup for one app without rewriting the app
itself. It packages the app's source files, its locked Python environment and
its requested network and credential access into a small directory of text
files. In this guide, you'll give a coding agent a kit-generation skill from
[langchain-policy-lab](https://github.com/shelajev/langchain-policy-lab), inspect
and review the permissions it proposes, and run the resulting kit with `sbx`.

In this guide, you'll learn how to:

- Set up the kit-generation skill for your coding agent without mixing up the
  agent's account and the app's model provider
- Lock an existing LangChain app's dependencies and generate a kit without
  changing or running the app
- Review the generated permissions, proxy-managed credential config and
  sandbox policy boundaries
- Store the app's model API key as a sandbox-scoped secret with `sbx secret set`
- Run the app inside the sandbox, first offline and then against Gemini, and
  verify blocked outbound requests in the policy log

## Prerequisites

- [Docker Sandboxes](https://docs.docker.com/ai/sandboxes/) with the `sbx` CLI
  on a supported host. Run `sbx run --help` and check that it lists the
  `shell` agent and the `--kit` flag.
- Docker with local Buildx installed, which `sbx` uses to build kit images (and
  which you also need if you later publish a kit to a registry).
- Git on your machine to clone the `langchain-policy-lab` repository.
- A coding agent that can read a skill folder, such as
  [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) or
  [Codex CLI](https://developers.openai.com/codex/cli), signed in with its own
  provider account. You can instead run the Python helper directly, as shown
  under [Without a coding agent](#without-a-coding-agent).
- Python 3.11 or later on your machine, for the skill's inspection and
  generation script, which needs only the standard library.
- [uv](https://docs.astral.sh/uv/getting-started/installation/) to lock the
  app's dependencies. We tested the commands with uv 0.9.26.
- A Google AI Studio [Gemini API key](https://aistudio.google.com/apikey) for the
  live run at the end. Everything before that step works without a key.
- Basic familiarity with LangChain and a terminal.

## How the pieces fit

The coding agent that builds the kit and the app that runs inside it use
separate providers and credentials:

- Your **coding agent** (Claude Code, Codex or another) reads the skill,
  inspects your app and writes the kit. It uses its own provider account and
  does not need the app's API key. This walkthrough runs it on the host; it can
  also run in a separate agent sandbox, as noted below.
- Your **LangChain app** calls its own model provider at runtime. The example
  app uses Gemini through `langchain-google-genai`. The kit keeps that choice
  and requests access to Gemini only.

A Claude Code or Codex session can generate a kit for a Gemini app, and the
other way round. The skill does not switch your app to the coding agent's
provider.

The generated kit is a **mixin**: it adds files and capabilities to a
**workload**, which supplies the operating system, user and shell. Here the
workload is Docker's built-in `shell` agent. The kit build packages your app at
`/opt/<kit-name>/app` and its locked Python environment at
`/opt/<kit-name>/venv`. Docker Sandboxes composes them with the workload and
applies the access requests when it creates the sandbox.

All setup, kit-generation and `sbx` commands in this walkthrough run on your
**host** machine, including `sbx run`, `sbx secret set`, `sbx policy log` and
`sbx rm`. Only commands explicitly marked **inside the sandbox**, such as
running `agent.py`, execute in the sandbox shell.

## Set up a working directory

On your host machine, create a working directory and clone
`langchain-policy-lab`. Instead of pointing the skill at a real app of your own
right away, copy the repository's raw example app (a single `agent.py` and an
unpinned `requirements.txt`) into a separate `my-agent` directory:

```console
$ mkdir ~/langchain-kit-demo && cd ~/langchain-kit-demo
$ git clone https://github.com/shelajev/langchain-policy-lab.git
$ cp -R langchain-policy-lab/skills/langchain-sandbox-kit/tests/fixtures/raw-agent my-agent
$ ls my-agent
agent.py  requirements.txt
```

Keeping `my-agent` outside the cloned repository lets you treat it the same way
you would treat an existing app folder of your own.

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

Unless a step explicitly changes directory or opens a shell inside the sandbox,
run all following host commands from `~/langchain-kit-demo`.

## Lock the app's dependencies

A kit build needs to reproduce the same Python environment inside the container,
so the skill requires exact versions rather than loose ranges. It expects a uv
project: `pyproject.toml` with exact direct pins, a `uv.lock` with hashes from
PyPI, and a `.python-version` file.

The example starts with only an unpinned `requirements.txt`. Step into
`my-agent` on the host, create the three uv files next to `agent.py` without
creating a local virtualenv or running the app, and then step back up to
`~/langchain-kit-demo`:

```console
$ cd my-agent
$ uv init --bare --no-workspace --name single-file-agent --python 3.13.7
$ uv python pin 3.13.7
$ uv add --no-sync 'langchain==1.4.4' 'langchain-core==1.6.9' 'langchain-google-genai==4.4.0'
$ uv lock
$ cd ..
```

Here is what those flags are doing:

- `--python 3.13.7` and `uv python pin` fix the Python version the kit builds
  with; uv downloads that interpreter inside the kit build, so it doesn't have
  to be installed on your machine.
- `--name` sets the project name written into `pyproject.toml`.
- `--bare` creates only a minimal `pyproject.toml`, `--no-workspace` keeps uv
  from attaching the app to a parent project, and `--no-sync` records the
  dependencies without creating a virtual environment.

The pinned versions here match the tested example, including the explicit
`langchain-core` pin used by its fake model. For your own
app, pick versions that you have already tested with it. If your app already
has a `uv.lock`, keep the tested lock, but check the other requirements too:
direct dependencies in `pyproject.toml` must use exact `==` pins, and an exact
`.python-version` is mandatory. A lock alone is not enough for this helper.

> [!TIP]
> If you set a uv package-age limit such as `UV_EXCLUDE_NEWER="7 days"`, uv
> records it in `uv.lock`. The generated kit carries the same setting into its
> container build, which runs `uv sync --locked`, so the build accepts the lock.

## Add the skill to your coding agent

The skill lives in `skills/langchain-sandbox-kit/`. Copy the entire folder, not
just `SKILL.md`, because `SKILL.md` relies on the helper script, templates and
references alongside it. Run this from `~/langchain-kit-demo` so the skill sits
in your workspace directory, outside `my-agent/`. The helper excludes
`.claude/` and `.agents/` even if they are inside an app; using the parent
workspace keeps the walkthrough's inputs and generated output separate:

```console
$ mkdir -p .claude/skills
$ cp -R langchain-policy-lab/skills/langchain-sandbox-kit .claude/skills/
```

That path is where Claude Code reads project skills from. For Codex, use
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
> such as `sbx secret set anthropic` for Claude, and is completely separate
> from the sandbox you create for the app later in this guide.

## Generate the kit

Start your coding agent in `~/langchain-kit-demo` on the host and ask it to use
the skill:

```text
Use the langchain-sandbox-kit skill to generate a Docker Sandboxes kit for the
LangChain app in ./my-agent. Its entrypoint is agent.py. Don't run or change the
app. Ask me about anything the inspection can't decide, write the kit to
./my-agent-kit, and then show me PERMISSIONS.md and RUN.md.
```

The agent runs the skill's helper script from `~/langchain-kit-demo` in two
stages. First it inspects the app by parsing source and dependency files as
text (it never imports or runs them) and turns anything that might need access
into a question. This app produces 12 questions; four of them look like this:

```text
- 1313c81151bf928b: env-name: LANGSMITH_TRACING; allow with reason, deny, or out-of-scope? (agent.py:14)
- 2f23ceb98c1a74c0: provider-host: generativelanguage.googleapis.com; allow with reason, deny, or out-of-scope? (pyproject.toml:8)
- 3f81b54c78a07b5d: provider-package: langchain-google-genai; allow with reason, deny, or out-of-scope? (pyproject.toml:8)
- fcdff6b3142ba65f: env-name: GOOGLE_API_KEY; allow with reason, deny, or out-of-scope? (pyproject.toml:8)
```

Each question takes one of three answers, plus a short reason:

- **allow** puts the access in the kit, for example a host in the network
  allow list or the provider's credential.
- **deny** records that you do not want the access. It adds a network deny
  when the finding resolves to a literal or provider host, or when your answer
  supplies explicit `hosts`. Other denials record intent in `PERMISSIONS.md`;
  they do not create a host deny rule by themselves.
- **out-of-scope** records that the finding needs no access of its own, such as
  a core library or an alternate environment variable name for the same key.

Here are all 12 findings for this app and the answers a developer who knows
it would give. Because both `requirements.txt` and `pyproject.toml` list
`langchain-google-genai`, the Gemini items appear once for each file. The
helper treats `langchain` itself as the core framework rather than a provider
integration, so it does not create a separate provider question for that package.
This classification is not proof that an app or its dependencies cannot use
the network.

| Finding | Where | Answer | Reason |
| --- | --- | --- | --- |
| `langchain-google-genai` (provider package) | `pyproject.toml`, `requirements.txt` | allow, credential `google` | The app uses Gemini only |
| `generativelanguage.googleapis.com` (provider host) | `pyproject.toml`, `requirements.txt` | allow | The Gemini API host |
| `GOOGLE_API_KEY` (environment variable) | `pyproject.toml`, `requirements.txt` | allow | The variable the Gemini SDK reads |
| `GEMINI_API_KEY` (environment variable) | `pyproject.toml`, `requirements.txt` | out-of-scope | An alias of the same key; one is enough |
| `langchain-core` (dependency) | `pyproject.toml` | out-of-scope | Library code, no access of its own |
| `LANGSMITH_TRACING` (environment variable) | `agent.py` line 14 | deny | Tracing stays off |
| Optional tracing (informational LangSmith finding) | `agent.py` | deny | No tracing access requested. This answer supplies no `hosts`, so it adds no explicit network deny |
| Scope confirmation | `agent.py` | allow | Confirms the app reads no files and calls nothing but Gemini |

For a provider-package finding, the answer can also select the credential
service: `google` here, or `openai` or `anthropic` for the
[other mapped providers](#choose-the-apps-model-provider). This selects a
service name, not a secret value. The agent never asks for your Gemini API key.

Scope confirmation asks you to check whether static inspection missed files
or destinations the app uses. For your own app, declare required data in the top-level
`dataPaths` list in the [answers file](https://github.com/shelajev/langchain-policy-lab/blob/main/docs/user-guide.md#the-answers-file) and review its access findings; the confirmation is not a runtime
access control.

Once you've answered, the agent writes your decisions to an answers file and
runs the generator from `~/langchain-kit-demo`:

```text
python3 .claude/skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py generate \
    --project my-agent --entrypoint agent.py --answers answers.json --out my-agent-kit
generated reviewable kit; read RUN.md and PERMISSIONS.md. No capabilities granted or runtime started
```

As the output states, this writes `./my-agent-kit` on disk and stops there: no
container image is built and no sandbox is started yet.

### Without a coding agent

If your coding agent already wrote `./my-agent-kit`, skip to
[Review the kit and its permissions](#review-the-kit-and-its-permissions).
Otherwise you can run the same two steps yourself from `~/langchain-kit-demo`
on the host. `inspect` prints the 12 questions and saves them, with their IDs,
to `inspection.json`. `generate` then reads the answers. The repository
includes reviewed answers for this example app, matching the table above, in
`langchain-policy-lab/examples/raw-agent.answers.json`:

```console
$ python3 langchain-policy-lab/skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py inspect \
    --project my-agent --entrypoint agent.py --json inspection.json
$ python3 langchain-policy-lab/skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py generate \
    --project my-agent --entrypoint agent.py \
    --answers langchain-policy-lab/examples/raw-agent.answers.json --out my-agent-kit
generated reviewable kit; read RUN.md and PERMISSIONS.md. No capabilities granted or runtime started
```

Both helper commands assume `~/langchain-kit-demo` as the working directory so
`--project my-agent`, `--out my-agent-kit`, and the script and answers paths
resolve cleanly.

Those example answers match this sample only, because each question ID is
derived from the file, line and finding. For your own app, write one decision
per question from your `inspect` output, using the format in the
[skill reference](https://github.com/shelajev/langchain-policy-lab/blob/main/docs/user-guide.md#the-answers-file).

If the inspector hits something it can't resolve statically, such as a URL
constructed at runtime, it doesn't guess. Generation stops until you name the
exact host or deny it. It also refuses source files that contain something
that looks like a secret.

## Review the kit and its permissions

Before building or launching anything, read what the generator wrote in
`./my-agent-kit`:

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

Here is what each piece does:

- `app/` is the snapshot copied into the sandbox. `agent.py` is byte-for-byte
  the original, and `requirements.txt` is left out because `uv.lock` replaces
  it. Files such as `.env`, `private/`, keys and credential files are never
  copied.
- `my-agent-kit.yaml` is the kit descriptor, `my-agent-kit.dockerfile` builds
  `app/` and its locked environment, and `my-agent-kit-context.md` provides
  run instructions for a coding-agent workload. The `shell` workload used here
  has no coding agent to read that context automatically.
- `PERMISSIONS.md` records every inspection finding with your decision and
  reason, along with what the kit does not protect against.
- `RUN.md` lists the exact `sbx` commands for this kit.
- `kit-manifest.json` records input, answer and output hashes for integrity
  checks and safe regeneration. It is generated metadata, not a permission
  decision to edit. `.dockerignore` limits what the build can copy.

The committed [single-file reference kit](https://github.com/shelajev/langchain-policy-lab/tree/main/examples/single-file-agent-kit) is generated from
`examples/single-file-agent/`, which omits `requirements.txt` and therefore has
eight findings. Your raw-example kit has 12 because both dependency files are
inspected; compare the structure, not byte-identical findings or names.

Keep the directory name the same as the descriptor's name (`my-agent-kit`). The
kit format pairs `<name>.yaml` with `<name>.dockerfile` inside a directory of
the same name.

Read `my-agent-kit.yaml` carefully. For this app, it asks for one network host
and one credential:

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

The network policy asks for one runtime host, and the credential entry asks for
the `google` secret with proxy injection. Because `proxyManaged: true` is set,
`GOOGLE_API_KEY` inside the sandbox holds a placeholder rather than your real
key; the Docker Sandboxes proxy inserts the real key into the `x-goog-api-key`
header only on outbound requests to `generativelanguage.googleapis.com`.
Setting `optional: true` lets the sandbox start even when no `google` secret
is configured yet, which is what makes the offline run in the next section
possible.

Under a **deny-by-default effective policy**, outbound destinations without a
matching allow rule are blocked, even with `deny: []`. That empty list requests
no explicit denies; it does not select allow-all mode. Docker documents this
[default network posture](https://docs.docker.com/ai/sandboxes/security/defaults/),
but configured policy can differ: the API supports both
[deny-all and allow-all modes](https://docs.docker.com/reference/api/sandboxes/latest/schemas/NetworkPolicyMode/).
Use the host-side policy preflight in the next section before interpreting
a blocked-host test.

Keep two boundary limits in mind when reviewing:

- **Requests are not exclusive grants.** When Docker Sandboxes creates the
  sandbox, it composes the kit's requests with any existing host or
  organization policy. Adding an `allow` entry does not make the resulting
  policy exclusive: other allow rules on the host or org can still widen
  access, while explicit deny rules always win.
- **Network policy does not police app behavior.** As `PERMISSIONS.md` spells
  out, the kit does not stop prompt injection, bugs inside your app code, or
  unwanted actions and costs on the model provider you allowed.

## Create the sandbox and run the app offline

Now switch from generating files to running the sandbox. Run this `sbx` command
on your **host** machine from `~/langchain-kit-demo` to build the kit and
create the sandbox:

```console
$ sbx run --detach shell --kit ./my-agent-kit --name my-agent-kit ./my-agent-kit
```

<!-- Host-verified 2026-11-13 at aa2af15 with sbx v0.53.0 (single-file-agent-kit): exit 0, kit built, sandbox created detached. No approval prompt appeared on that configured host; don't promise one. -->

Each part of that command has a specific job:

- `shell` is the workload agent: a plain shell sandbox with no coding agent in
  it.
- `--kit ./my-agent-kit` applies the local mixin directory. The flag accepts
  a directory, ZIP, Git or OCI kit reference, including published references
  such as `--kit org/my-mixin:latest`. Agent selection belongs to the first
  positional argument (`shell` here), not to the `--kit` value.
- `--name my-agent-kit` names the sandbox so the following commands can target
  it.
- `./my-agent-kit` at the end is the workspace mounted into the sandbox. Because
  the app itself runs from `/opt/my-agent-kit/app`, the workspace mount only
  needs to avoid exposing extra host files: mounting the reviewed kit
  directory keeps `my-agent` and `~/langchain-kit-demo` out of the sandbox.
- `--detach` builds the kit, creates the sandbox, and prints its ID without
  opening an interactive shell.

If `sbx` prompts you to approve anything while building the kit or creating the
sandbox, compare the prompt against `PERMISSIONS.md` before accepting.

Before opening that shell, inspect the sandbox's active policy from
`~/langchain-kit-demo` on your **host**:

```console
$ sbx policy ls my-agent-kit --wide
$ sbx policy check http --sandbox my-agent-kit https://example.com --json
```

Review the active policy rows for broad allows, then read `allowed` in the
JSON result. `"allowed": false` means the policy does not authorize this URL;
`"allowed": true` means it does. In that case, the `example.com` connection test
in the next section may connect instead of being blocked. Leave your existing
policy unchanged and use this decision to interpret that later check.
[Local presets](https://docs.docker.com/ai/governance/local/) and other applicable
rules can grant more access than this kit requests.

These are read-only checks. The [HTTP policy check](https://docs.docker.com/reference/cli/sbx/policy/check/http/)
evaluates network policy followed by HTTP policy; it makes no DNS lookup or
network request and does not prove runtime transport behavior. The later guest
request and its matching policy-log entry provide that runtime evidence.

Next, open a shell in the sandbox from `~/langchain-kit-demo` on the host:

```console
$ sbx run --name my-agent-kit
```

Your prompt is now **inside the sandbox** (the guest). Change into the app
directory inside the sandbox and run `agent.py` with the kit's Python
interpreter and `--fake-model`:

```console
$ cd /opt/my-agent-kit/app
$ /opt/my-agent-kit/venv/bin/python agent.py --fake-model
{"category":"technical","ticket_id":"T-101"}
```

You should see that single JSON line printed back with exit code 0, confirming
that the locked virtualenv and `agent.py` work inside the sandbox without an
API key or outbound network traffic.

Make sure to call `/opt/my-agent-kit/venv/bin/python` explicitly. In the
`shell` agent, bare `python` points to the system Python, which doesn't have
LangChain installed, so `python agent.py` fails with
`ModuleNotFoundError: No module named 'langchain'`. Run `exit` when you're done
to leave the sandbox shell and return to `~/langchain-kit-demo` on the host.

## Add the model secret and run against Gemini

Back on your **host** machine in `~/langchain-kit-demo`, store your Gemini API
key as a secret scoped to this sandbox only:

```console
$ sbx secret set google --sandbox my-agent-kit
```

<!-- Host-verified 2026-11-13: a sandbox-scoped google secret set after creation reached the running sandbox without restart (synthetic invalid value via stdin gave API_KEY_INVALID; removing it restored the global-backed live call). EVIDENCE LIMIT: interactive prompt text with a real key was not observed. -->

`sbx` prompts interactively for the value so the key doesn't end up in your
shell history. Avoid `--token`, which passes the secret on the command line,
and never put the key in `my-agent-kit/`, a `.env` file or a container
environment variable. Including `--sandbox` keeps the key isolated from any
other sandboxes you run; without it, `sbx` stores a global secret for all
sandboxes. If your key lives in 1Password or AWS Secrets Manager,
`sbx secret set google --sandbox my-agent-kit --ref ...` stores a
reference scoped to this sandbox instead.

Open a shell in the sandbox again from `~/langchain-kit-demo` on the host:

```console
$ sbx run --name my-agent-kit
```

Now **inside the sandbox**, run `agent.py` without `--fake-model`:

```console
$ cd /opt/my-agent-kit/app
$ /opt/my-agent-kit/venv/bin/python agent.py
```

This sends one real request to Gemini (and incurs a small API charge). The
reply is a JSON object for ticket `T-101`. Because the model chooses the
category and may include extra fields, your exact output will vary, for
example:

```json
{
  "ticket_id": "T-101",
  "category": "export",
  "description": "report export fails",
  "priority": "high"
}
```

<!-- Host-verified 2026-11-13: sample is the native sandbox output, exit 0, with the host's existing global google credential injected by the proxy (not a scoped real key); policy log showed generativelanguage.googleapis.com:443 allowed. -->

While you are still **inside the sandbox**, test a destination the kit does
not request. The expected rejection below assumes a deny-by-default effective
policy and no applicable allow for `example.com`. Allow-all mode or a broader
applicable allow changes that expectation; this kit's request alone cannot
establish the test's preconditions. Use the host preflight above to decide
whether this rejection is expected in your configuration. If SBX asks you to
approve access for this test, leave it unapproved:

```console
$ /opt/my-agent-kit/venv/bin/python -c "import urllib.request; urllib.request.urlopen('https://example.com', timeout=10)"
```

This should fail with a Python traceback (exit 1) rather than returning
silently. Exit the sandbox shell (`exit`), then check the policy log from
`~/langchain-kit-demo` on your **host** machine:

```console
$ sbx policy log my-agent-kit
```

Look for a blocked entry for `example.com`. A traceback or timeout inside the
sandbox on its own doesn't prove the network policy stopped the connection; the
entry in `sbx policy log` does.

<!-- Host-verified 2026-11-13: request failed with HTTP 403 (exit 1); policy log listed example.com:443 blocked, reason "No matching allow rule (default deny)". -->

## Choose the app's model provider

If you adapt this workflow to your own app, the skill ships with reviewed
mappings for three LangChain provider packages. It detects the package from your
dependencies and fills in the host, secret service, environment variable and
header automatically:

| Provider | LangChain package | Host | `sbx secret set` service | Environment variable | Header |
| --- | --- | --- | --- | --- | --- |
| Google Gemini (AI Studio) | `langchain-google-genai` | `generativelanguage.googleapis.com` | `google` | `GOOGLE_API_KEY` (also reads `GEMINI_API_KEY`) | `x-goog-api-key` |
| OpenAI | `langchain-openai` | `api.openai.com` | `openai` | `OPENAI_API_KEY` | `Authorization: Bearer` |
| Anthropic | `langchain-anthropic` | `api.anthropic.com` | `anthropic` | `ANTHROPIC_API_KEY` | `x-api-key` |

For an OpenAI app, the secret command becomes
`sbx secret set openai --sandbox NAME`; for an Anthropic app,
`sbx secret set anthropic --sandbox NAME`. The generated `RUN.md` always gives
you the matching command for the kit.

Other setups require manual decisions because their hosts or authentication
differ:

- **Vertex AI, Azure OpenAI and Amazon Bedrock** use different endpoints and
  cloud authentication flows and aren't covered by these three mappings.
- **OpenAI-compatible gateways and custom base URLs** need the exact gateway
  host. Don't assume an OpenAI key or `Authorization: Bearer` header works
  there.
- **Other providers.** `sbx secret set` also supports services such as `groq`,
  `mistral`, `openrouter` and `xai`, but the skill has no reviewed LangChain
  mapping for them. Add the host and credential entry to the descriptor
  yourself from the provider's documentation.
- **LangSmith tracing** has no built-in `sbx` secret service. Keep tracing off,
  as in this example, unless you package it yourself.

The skill preserves whichever provider your app already uses. If you want to
switch providers, change your app and its dependencies first, then regenerate
the kit.

## Clean up

Once you've exited the sandbox shell, remove the sandbox from your **host**
machine (from `~/langchain-kit-demo` or any host directory):

```console
$ sbx rm my-agent-kit
```

`sbx rm` asks for confirmation, then deletes the sandbox along with any
secrets scoped to it. Any global secrets or policy rules you created stay in
place (list them with `sbx secret ls` and `sbx policy ls`), as do your local
`my-agent` and `my-agent-kit` directories.

## Optional: run the kit in Docker Sandboxes cloud

`sbx --cloud run` accepts the same kit from `~/langchain-kit-demo` on the host.
Cloud sandboxes have no host workspace, so no workspace path follows the agent:

```console
$ sbx --cloud run --detach shell --kit ./my-agent-kit --name my-agent-kit
```

We haven't run this kit in cloud sandboxes, so treat this section as an
untested starting point. `sbx --cloud --help` lists the commands your CLI
supports in cloud mode. Launching with a local kit builds it in Docker's cloud,
which means the contents of `app/` leave your machine. Cloud sandboxes also
keep their own secrets and network policy, so your local secret doesn't carry
over.

<!-- EVIDENCE: not run. Cloud secret commands and kit baking are documented in CLI help only. -->

## Optional: publish the kit to Docker Hub

A kit is an OCI artifact, so you can share it through a registry. This needs
Docker with Buildx and a `docker login` to Docker Hub. Pointing `-f` at the
descriptor tells Buildx to build the kit (the descriptor's first line selects
the kit builder, which finds `my-agent-kit.dockerfile` by name). From
`~/langchain-kit-demo` on the host, change into `my-agent-kit` to build and
push both platforms in one command:

```console
$ cd my-agent-kit
$ docker buildx build . -f my-agent-kit.yaml --platform linux/amd64,linux/arm64 --push \
    -t docker.io/<your-namespace>/my-agent-kit:0.1.0
```

Others can then run `sbx run shell --kit <your-namespace>/my-agent-kit:0.1.0`.
Publishing shares everything in `app/` (your code and lock file) with anyone
who can pull the image, so verify the repository's visibility and what is
inside `app/` before pushing. The `sbx kit` command also includes `push`,
`sign` and `verify` subcommands; see `sbx kit --help` for details.

<!-- EVIDENCE: not run. No kit was pushed while preparing this guide. -->

## Conclusion

You now have an existing LangChain app packaged as a kit that requests access
only to its model provider, with the API key held by the sandbox proxy rather
than inside the sandbox (and enforced alongside any host or organization policy
in effect). The kit stays a small directory of reviewable text files that you
can regenerate when the app changes, commit next to it, or share with your
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
