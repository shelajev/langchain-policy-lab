# Run your LangChain in Docker Sandboxes

Your LangChain app is ordinary Python. You can run its existing `agent.py` in a
shell sandbox without converting it into a custom kit or moving it into `src/`.
First decide which files and services it may use. Then mount a sanitized copy,
install its reviewed dependencies inside the sandbox, and launch the same app.

## Why isolate the agent and the app?

A coding agent can run tools, read files and execute commands while developing
your project. Later, the application can read the same data and make model or
HTTP requests without the coding agent being involved at all. Confining only
the editor misses the application's runtime access.

[Docker Sandboxes](https://docs.docker.com/ai/sandboxes/) provides microVM-based
isolation. Workspace mounts and policy still decide what crosses that boundary.
Mounting a directory exposes its contents; permitting a service lets requests
reach it. The useful question is which files, destinations and credential-backed
operations the app can use there.

For this example, allow only the Gemini API for synthetic ticket classification.
Leave tracing off. Do not expose `.env`, keys or private data. The shell workload
runs the app; a coding agent is optional assistance, not the thing being deployed.

## Run your existing app in a sandbox

You need this repository checkout, Python 3.11+ for the inspector, and uv 0.9.26
for lock preparation. Actual sandbox commands need a supported Docker Sandboxes
host with `sbx`. Docker buildx and kit-tck are needed only for optional packaging
checks, not for direct local execution. All `sbx` commands below are **host
steps, NOT RUN here**; local and cloud runtime acceptance remains open.

Start from the [raw fixture](../skills/langchain-sandbox-kit/tests/fixtures/raw-agent/):
just `agent.py` and `requirements.txt`. It classifies a synthetic ticket using
LangChain and Gemini, or a nonbillable fake model. From the repository root:

```bash
cp -R skills/langchain-sandbox-kit/tests/fixtures/raw-agent /tmp/my-agent
cd /tmp/my-agent
uv init --bare --no-workspace --name single-file-agent --python 3.13.7
uv python pin 3.13.7
uv add --no-sync 'langchain==1.4.4' 'langchain-core==1.6.9' 'langchain-google-genai==4.4.0'
uv lock
cd -
```

Use fresh paths. These commands add dependency metadata without changing or
running `agent.py`. For an existing project, review its metadata/build backend
first; do not blindly initialize it again. Choose compatible exact versions
for your app rather than adopting this example's pins. Keep your lock and
Python pin with the app. The [single-file example](../examples/single-file-agent/README.md)
explains these constraints.

### Manual: prepare only the files the app needs

Before copying, read the script and requirements. Confirm the model and exact
provider host, custom base URLs, tracing, subprocesses, files and any other
network operations. For this fixture: `python agent.py`, Gemini
`generativelanguage.googleapis.com`, model `gemini-2.5-flash`, no tracing and no
private data. A Python file cannot prove complete permissions; confirm runtime
configuration with the developer.

Make a separate control directory and an explicit allowlisted workspace. Do not
copy the whole project and hope `.dockerignore` filters a mount: it does not.
For this fixture, from the repository root:

```bash
mkdir -p /tmp/manual-agent-direct/workspace
cp /tmp/my-agent/agent.py /tmp/my-agent/pyproject.toml /tmp/my-agent/uv.lock /tmp/my-agent/.python-version /tmp/manual-agent-direct/workspace/
cp skills/langchain-sandbox-kit/templates/direct-setup.txt /tmp/manual-agent-direct/setup-deps.sh
```

For your app, retain its relative package layout and copy only reviewed source,
lock/config and required data files. Never include `.env`, `private/`, keys,
`.venv`, caches, VCS or agent hook/config directories. Review the copy before
mounting it; even an innocent-looking data file can contain secrets.

Write `/tmp/manual-agent-direct/sbxenv.yaml`:

```yaml
schemaVersion: "1"
name: manual-agent-direct
agent: sbx-kit-shell
kits:
  - docker/sbx-kit-shell:1.0.0@sha256:367c9a4b3fd550f777e1d57cc53550afb4a1385055d79111acf6f996272ff6de
workspace: ./workspace
sandboxOptions:
  skills: off
env:
  GOOGLE_API_KEY: proxy-managed
  LANGSMITH_TRACING: "false"
```

This selects an official shell workload, not an app-specific mixin. It has
Python but no uv, curl or git. The reviewed `setup-deps.sh` uses Python's standard
library to download uv 0.9.26, verifies the archive checksum, installs only uv
into the sandbox user's home, then runs `uv sync --locked`. Read it before use;
it runs **inside** the sandbox. Supported architectures are Linux x86_64/aarch64.
The dependency install can run package build hooks inside the sandbox.

Keep the environment and setup script outside `workspace/`. Disabling shared
skills omits that extra mount. The placeholder is not a credential; never put
an actual key in this YAML.

### With a coding agent: inspect, ask, then direct

Ask your coding agent to read [the repository skill](../skills/langchain-sandbox-kit/SKILL.md):

> Run my existing LangChain app at /tmp/my-agent in Docker Sandboxes. Inspect
> agent.py without executing it, ask about unresolved access, preserve its layout,
> and prepare a direct-run plan before requesting permissions. A reusable kit is optional.

The skill is self-contained: keep its scripts, templates and references together.
For discovery in your own project, copy the folder into
`.agents/skills/langchain-sandbox-kit/` (Codex) or
`.claude/skills/langchain-sandbox-kit/` (Claude Code), not a host-global directory.
You can run the same deterministic steps yourself from the repository root:

```bash
python3 skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py inspect --project /tmp/my-agent --entrypoint agent.py --json /tmp/my-agent-inspection.json
python3 skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py direct --project /tmp/my-agent --entrypoint agent.py --answers examples/raw-agent.answers.json --out /tmp/my-agent-direct
```

The answers above match this unchanged fixture and metadata only. For your app,
answer every finding with an explicit allow, deny or out-of-scope decision and
reason using the [answer contract](../skills/langchain-sandbox-kit/references/answers.schema.md).
Ask about exact dynamic URLs and optional tracing; do not auto-allow imports.
Include required data/config paths explicitly. Missing or stale answers stop
with exit 2; unsafe inputs with 3; unsafe overwrite with 4.

Review `ACCESS.md`, `RUN.md`, `setup-deps.sh`, manifest hashes and `workspace/`.
The helper never imports source, resolves dependencies, starts a sandbox or
grants access. It refuses secret-like literals and unsafe/incomplete scans.
Use a fresh output directory outside the app. `--force` only replaces unchanged
helper-owned output, never your edits.

### Host: create, configure access, then run

The following commands use the **manual** directory. If you used the helper,
follow its `RUN.md` instead: use `/tmp/my-agent-direct/sbxenv.yaml` and sandbox
name `single-file` consistently, not `manual-agent-direct`.

On your approved host, use an existing approved Google credential. The direct
route uses Docker's built-in service **google**, not the optional kit's **gemini**
service. `sbx secret set` prompts on the host; do not print the value or put it
in an argument. Inspect existing scoped secrets and effective policy first.

```bash
sbx secret set google --sandbox manual-agent-direct
sbx env plan /tmp/manual-agent-direct/sbxenv.yaml
sbx env create /tmp/manual-agent-direct/sbxenv.yaml
sbx policy ls
sbx policy allow network --sandbox manual-agent-direct generativelanguage.googleapis.com
sbx policy deny network --sandbox manual-agent-direct example.com
sbx policy allow network --sandbox manual-agent-direct github.com,release-assets.githubusercontent.com,pypi.org,files.pythonhosted.org
sbx env exec /tmp/manual-agent-direct/sbxenv.yaml -- pwd
sbx env exec -i /tmp/manual-agent-direct/sbxenv.yaml -- sh < /tmp/manual-agent-direct/setup-deps.sh
```

Review the environment plan before approving. The mounted workspace should be
its working directory; check `pwd` and the expected `pyproject.toml` before
setup. The proxy injects the Google API key as `x-goog-api-key` for the approved
API domain. If the plan requests an additional credential-domain binding, stop
for host review; this shell composition's binding prompt has not been exercised
here. Environment bindings can affect other sandboxes and must not be silently added.

The four temporary destinations let uv and the pinned Python/dependencies be
downloaded. After setup, remove those scoped grants and inspect effective policy:

```bash
sbx policy rm network --sandbox manual-agent-direct --resource github.com,release-assets.githubusercontent.com,pypi.org,files.pythonhosted.org
sbx policy ls
sbx env exec /tmp/manual-agent-direct/sbxenv.yaml -- .venv/bin/python agent.py --fake-model
```

Expected offline result: `{"category": "technical", "ticket_id": "T-101"}`.
This runs the existing app inside the sandbox, without billing a model. You can
also attach with `sbx env run /tmp/manual-agent-direct/sbxenv.yaml`, activate
`.venv/bin/activate` in that shell, then run `python agent.py --fake-model`.

## Verify allowed and denied operations

For a real allowed call, separately approve the synthetic input, model budget
and timeout. The fixture selects `gemini-2.5-flash` with bounded output:

```bash
sbx env exec /tmp/manual-agent-direct/sbxenv.yaml -- python3 -c "import subprocess; subprocess.run(['.venv/bin/python', 'agent.py'], timeout=60, check=True)"
sbx env exec /tmp/manual-agent-direct/sbxenv.yaml -- python3 -c "import urllib.request; urllib.request.urlopen('https://example.com', timeout=10)"
sbx policy log
```

The first should return a valid category, using the approved Gemini host. The
second must be rejected by policy for `example.com`, with a matching boundary
event. Confirm the origin is reachable from an approved host-side control first.
DNS, TLS, timeout or an origin's own 403 is not proof of a sandbox policy denial.
Check `.env`, `private/` and credentials are absent without printing their content.
Inspect inherited local/org rules: adding one allow does not cancel broader
grants, and an org deny cannot be bypassed with a local allow.

Local SBX allowed/denied checks are **NOT RUN** here. The unchanged fixture has
passed a read-only, nonroot, network-none ordinary container probe on the pinned
shell image; that does not establish SBX policy or credential injection.

When finished, review the destroy plan:

```bash
sbx env rm /tmp/manual-agent-direct/sbxenv.yaml
```

Review remaining sandbox-scoped policy/secret entries and remove only this run's
entries. Cleanup must not alter shared bindings or unrelated sandbox access.

## Optional: package a reusable kit

A reusable kit packages the environment, dependencies and policy for repeatable
distribution or cloud baking. It is not required to run each LangChain file.
The larger [ticket-triage example](../examples/ticket-triage/README.md) exercises
`src/` layout, data files and optional status/webhook access. Its worked answers
are fixture-specific; keep those optional destinations denied.

## Generate packaging you can review

The [worked answers](../examples/ticket-triage.answers.json) allow only Gemini
for model use, request service `gemini` at runtime, deny the webhook/status
destinations and leave tracing off. They name synthetic `data/tickets` as
input and confirm `gemini-2.5-flash`. They are not a policy template for every
LangChain app. For your app, write answers after discussing its findings.

```bash
python3 skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py generate --project examples/ticket-triage --entrypoint src/ticket_triage/app.py --answers examples/ticket-triage.answers.json --out /tmp/my-ticket-triage-kit
python3 skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py explain --manifest /tmp/my-ticket-triage-kit/kit-manifest.json
```

Use a fresh output directory outside the app. Nonempty output is refused;
`--force` is allowed only for an unchanged helper-owned tree, not arbitrary
developer edits. The input app is untouched.

The directory contains a descriptor, Dockerfile, context instructions, local
and cloud environment files, a permission summary and a hash manifest. The
`app/` subtree is a sanitized snapshot: source, pinned project/lock/Python
files and explicitly declared data. The generated `.dockerignore` is an
allowlist for that snapshot. Never build from the original app directory just
because its `.dockerignore` looks plausible.

The helper supports root Python files and packaged `src/` projects with exact direct pins, a hashed
public-PyPI uv lock and an exact Python version. It refuses unsupported locks,
custom dependency sources, unsafe paths and incomplete scans. Requirements-only
input needs reviewed lock setup before generation. This deliberate limit is preferable to running
an arbitrary resolver while trying to inspect untrusted input.

Secret-like literals block generation. Acknowledgement is not permission to
bake a key into an image. Remove the secret from source and rotate any real key
that was exposed through normal operator procedures. Keep `.env`, private
directories and credential files out of snapshots, reports and build contexts.

Before approving the generated kit for runtime, build and TCK-check that copy.
These checks are separate from environment creation, not an assumption that
`sbx env run` has validated your artifact:

```bash
(
  cd /tmp/my-ticket-triage-kit
  docker buildx build . -f ticket-triage.yaml --progress plain --output type=cacheonly
  docker buildx build . -f ticket-triage.yaml --progress plain -t ticket-triage:0.1.0 --output type=oci,dest=/tmp/generated-triage-layout,tar=false
  kit-tck validate --verbose --layout /tmp/generated-triage-layout 0.1.0
)
```

Use a fresh layout path. The subshell leaves you at the repository root.
Continue to the local host handoff, or take the manual route instead.

### Manual reusable kit from an agent.py template

For a root `agent.py`, start from the
[single-file kit](../examples/single-file-agent-kit/). It is a template, not
your app or your answers. The [ticket-triage kit](../examples/ticket-triage-kit/)
is the larger `src/` example. No helper is needed for this manual route.
From the repository root, copy the template to a new directory:

```bash
cp -R examples/single-file-agent-kit /tmp/manual-agent-kit
cd /tmp/manual-agent-kit
mv single-file.yaml manual-agent.yaml
mv single-file.dockerfile manual-agent.dockerfile
mv single-file-context.md manual-agent-context.md
```

Use `manual-agent` consistently below, or replace it everywhere with your name.
Make these edits before building:

1. **`app/`**: remove the example files and put your own unchanged `agent.py`,
   `pyproject.toml`, `uv.lock` and `.python-version` here, plus required data.
   If you only have requirements, first use the verified
   [raw-script lock commands](../examples/single-file-agent/README.md#starting-with-just-agentpy-and-requirementstxt)
   in your app directory, choosing compatible exact versions. Never copy `.env`,
   private files or keys.
2. **`manual-agent.yaml`**: set `displayName: manual-agent`, `version: "0.1.0"`
   and `provides: ["manual-agent@0.1.0"]`. Change
   `agent-context@1`'s `config.contentFile` to `./manual-agent-context.md`.
   Under `network-policy@1`, edit `config.runtime.allow` and `deny` to exact
   provider/other hosts you approve or forbid; no URL paths or blanket wildcard.
   The template allows `generativelanguage.googleapis.com`. See the
   [provider host table](../skills/langchain-sandbox-kit/references/capabilities.md).
   Under `credential@1`, change `config.service`, `phase: runtime`,
   `apiKey.name`, and `apiKey.inject`'s `domain`, `header` and `format` for your
   provider, or remove that capability if no key is needed. Gemini uses service
   `gemini`, sentinel `GOOGLE_API_KEY`, domain `generativelanguage.googleapis.com`,
   header `x-goog-api-key`, format `"%s"` and `proxyManaged: true`. Keep real keys
   out of YAML; the host binds the service separately. `optional: true` permits
   the offline fake run without a key.
3. **`manual-agent.dockerfile`**: replace every `/opt/single-file` with
   `/opt/manual-agent`. Set both Python `3.13.7` occurrences to your exact
   `.python-version`. `COPY app/ ./` already includes your allowed data; if you
   change that layout, adjust this COPY and the final overlay COPY together.
   Keep the pinned base and locked install; image-build downloads are separate
   from runtime network policy.
4. **`.dockerignore`**: keep the initial `**` and allow only your files, for
   example `!app/agent.py`, `!app/pyproject.toml`, `!app/uv.lock`,
   `!app/.python-version`, explicit data files, and `!manual-agent-context.md`.
   Remove old entries; do not replace this with `!**`.
5. **`manual-agent-context.md`**: set the app directory and your launch command,
   for example `cd /opt/manual-agent/app && python agent.py`. This is guidance,
   not automatic execution: the shell workload owns entrypoint, user and
   `sbx@1`; `sbx env exec` launches the app after composition.
6. **`sbxenv.local.yaml` / `sbxenv.cloud.yaml`**: change `name: manual-agent`
   and the `kits` app path if it is no longer `./`. Keep the pinned shell kit.
   Local `workspace: .` is only the sanitized kit; cloud has no `workspace`.
7. **`PERMISSIONS.md`**: replace the example decisions and reasons with yours,
   including every allow/deny, selected model, data, tracing, credential and
   launch command. Static inspection is not proof of complete permissions.
8. **`kit-manifest.json`**: delete it. Manual edits make the helper's hashes
   stale. This route does not call the helper, `explain` or `generate --force`;
   helper-owned overwrite checks are not part of manual maintenance.

Build your edited copy and validate its artifact, using a fresh layout path:

```bash
docker buildx build . -f manual-agent.yaml --progress plain --output type=cacheonly
docker buildx build . -f manual-agent.yaml --progress plain -t manual-agent:0.1.0 --output type=oci,dest=/tmp/manual-agent-layout,tar=false
kit-tck validate --verbose --layout /tmp/manual-agent-layout 0.1.0
```

Verify your edits against your app, not the repository's original probe: the
build succeeds, TCK passes, and a network-none/read-only/uid1000 container probe
of your overlay runs `python agent.py --fake-model` (or your own offline command)
from `/opt/manual-agent/app`, with no `.env`, private data or keys in the image.
Use the [guide's container recipe](user-guide.md#probe-your-manual-overlay).
That checks filesystem compatibility, not actual SBX confinement or credential
injection. Those remain host checks.

### Host: run the optional kit locally

On the approved host, from the repository root:

```bash
sbx env plan /tmp/my-ticket-triage-kit/sbxenv.local.yaml
sbx env run --detach /tmp/my-ticket-triage-kit/sbxenv.local.yaml
sbx env exec /tmp/my-ticket-triage-kit/sbxenv.local.yaml -- sh -lc 'cd /opt/ticket-triage/app && python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model'
```

These paths use the generated and validated copy. The repository's
`examples/ticket-triage-kit` is a prepackaged reference, not this output directory.
If you chose another output path, change it on every command. For the manual single-file copy,
use this alternative host handoff instead (also NOT RUN here):

```bash
sbx env plan /tmp/manual-agent-kit/sbxenv.local.yaml
sbx env run --detach /tmp/manual-agent-kit/sbxenv.local.yaml
sbx env exec /tmp/manual-agent-kit/sbxenv.local.yaml -- sh -lc 'cd /opt/manual-agent/app && python agent.py --fake-model'
```

Use your own offline arguments if your script differs from the fixture.
Review the plan before approval. It selects the v3 shell workload and app
mixin, and mounts only the sanitized kit directory. `env exec` is the part
that runs your LangChain app in the sandbox. Starting a coding agent is not a
substitute for this command.

Fake mode needs no credential. For a real request, the host must bind an
existing `gemini` service credential to the exact API injection domain, then
approve one bounded model call. A host `GEMINI_API_KEY` variable alone is not
that binding. The [handoff](acceptance-handoff.md) explains private overrides,
cloud separation and the exact live command. Do not put real keys into YAML,
image layers, shell arguments or evidence.

Acceptance also needs deliberate negative tests. For ticket-triage, under the
same composition, try status enrichment to `example.com`, direct HTTP to denied
destinations, and the webhook flag. Those flags do not exist in the single-file
fixture; for your own app, test its applicable operations against a deliberately
forbidden host. Check that `.env` and private data are absent. Retain
boundary events, not just error text. The illustrative `.invalid` webhook can
fail DNS even with no policy at all; an origin 403 can also resemble a boundary
403. The handoff includes resolvable-origin controls and expected exits.

## Cloud changes the resources, not the app

For the optional kit, the cloud file keeps the baked app and removes `workspace` entirely. Cloud
cannot mount the host directory. The host reports `sbx --cloud diagnose` passed
authentication, API reachability and subscription: the host cloud account and
API are reachable. The crew did not observe that diagnosis. Cloud runtime
execution is still **NOT RUN**; cloud-side secret/binding, approval to bake or
upload, and the actual allowed/denied runs remain open. On the approved host:

```bash
sbx --cloud env plan /tmp/my-ticket-triage-kit/sbxenv.cloud.yaml
sbx --cloud env run --detach /tmp/my-ticket-triage-kit/sbxenv.cloud.yaml
sbx --cloud env exec /tmp/my-ticket-triage-kit/sbxenv.cloud.yaml -- sh -lc 'cd /opt/ticket-triage/app && python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model'
```

For the manual single-file copy, use the matching cloud handoff instead:

```bash
sbx --cloud env plan /tmp/manual-agent-kit/sbxenv.cloud.yaml
sbx --cloud env run --detach /tmp/manual-agent-kit/sbxenv.cloud.yaml
sbx --cloud env exec /tmp/manual-agent-kit/sbxenv.cloud.yaml -- sh -lc 'cd /opt/manual-agent/app && python agent.py --fake-model'
```

The target needs its own secret and explicit domain approval for a live call.
Repeat allowed and denied checks there. A local success would not prove cloud
credential support, policy or cleanup. These cloud commands were not executed
in the implementation environment, and no image was published or app uploaded.

Clean up each environment using the same account, target and file paths:

```bash
sbx --cloud env rm /tmp/my-ticket-triage-kit/sbxenv.cloud.yaml
sbx env rm /tmp/my-ticket-triage-kit/sbxenv.local.yaml
```

For the manual alternative, remove `/tmp/manual-agent-kit/sbxenv.cloud.yaml`
with `sbx --cloud env rm` and `/tmp/manual-agent-kit/sbxenv.local.yaml` with
`sbx env rm` instead.

Running a job in cloud isolation is not production serving deployment. You
still need ingress, lifecycle management, scaling, durability, auditing,
availability and cost controls appropriate to the application.

## Keep the boundary honest

Review the effective policy, not only your access plan. Other kits and host/org
defaults can expand access. Use exact hosts, explicit denies where needed,
separate build and runtime permissions, and minimal mounted data. The helper
uses host-level `network-policy@1` only in the optional kit; do not claim method/path filtering. More
granular @2 policy needs its own target-enforcement tests.

Proxy-managed credentials reduce secret exposure, but an allowed service still
accepts requests. A malicious instruction can ask the app to send sensitive
content to the permitted model endpoint or spend its quota. Sandboxing is not
a cure for prompt injection, and structured output is not proof of truth.

Verify allowed and denied operations on each target before relying on its boundary.
