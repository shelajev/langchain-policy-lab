# Run your LangChain in Docker Sandboxes

Your LangChain app should not inherit everything your laptop can reach. It
needs a model endpoint and some input files. That does not mean it needs your
home directory, every credential in your shell, or an unrestricted route to
the network. The same distinction matters when a coding agent is editing the
app and when the app itself is processing an untrusted ticket.

This tutorial packages an existing Python app as a Docker Sandboxes v3 mixin.
You inspect its resources, answer concrete permission questions, review the
package and run the app inside a sandbox. The agent-assisted example packages
ticket-triage; the manual path adapts a single-file template for your own
`agent.py`. Both produce the same kinds of reviewable kit files.

One important limit up front: the repository's offline tests, generated build,
artifact TCK and ordinary-container probe passed. One host-authorized live
Gemini call also passed inside the implementation sandbox, with one synthetic
ticket and bounded output. That is **not local/cloud SBX acceptance**. Actual
local and cloud SBX have **not run** here because `sbx` is absent.
The [host acceptance handoff](acceptance-handoff.md)
contains the remaining commands. A successful image build is useful evidence.
It is not evidence of a runtime security boundary.

## Start with an app, not a sandbox framework

If your app is a single `agent.py` plus a requirements file, keep it that way.
Inspection accepts the file directly; the [single-file example](../examples/single-file-agent/README.md)
shows the minimal supported project. Review dependency versions and build
configuration, create a normal pyproject with exact pins and a Python-version
file, then run `uv lock` as ordinary, reviewed project setup. The deterministic
helper never resolves dependencies itself or runs `agent.py` during inspection.
No package conversion or Sandbox API is required. Its launch command can remain
`python agent.py` with the same arguments.

The [ticket-triage app](../examples/ticket-triage/) reads a synthetic JSON support
ticket, runs a LangChain prompt/model/parser pipeline and prints a validated
ticket ID, category and summary. There is no Sandbox API in its code.

It also has realistic optional access: a status-page URL from
`TRIAGE_STATUS_URL`, a webhook behind `--post-webhook`, a model selected through
`TRIAGE_MODEL`, and optional LangSmith tracing. Those are precisely the choices
you do not want a packaging tool to make silently.

Use this repository checkout, uv 0.9.26, Python 3.13.7 and Docker with buildx.
Static inspection needs only Python 3.11+. Build validation additionally needs
the pinned `kit-tck`. On Linux x86_64/aarch64, from the repository root, install
project tools into a chosen scratch directory and add them to this shell's PATH.
The installer needs `curl`, `tar`, `sha256sum`, `git` and Go available; it
downloads pinned uv and builds the pinned kit-tck into that directory:

```bash
bash scripts/install-ci-tools.sh /tmp/triage-tools
export PATH="/tmp/triage-tools:$PATH"
```

On other hosts, build kit-tck from the exact spec commit in
[provenance](provenance.md). Actual sandbox steps need a supported Docker
Sandboxes host with `sbx`, not a nested daemon. No API key is needed for this
first app check, from the repo root:

```bash
bash scripts/check-example.sh
```

The script syncs the frozen dependencies, runs four deterministic tests, then
runs one fake-model request. Recorded output:

```json
{"category": "technical", "summary": "Synthetic offline classification; investigate the reported issue.", "ticket_id": "T-101"}
```

The fake mode uses a LangChain fake chat model. It tests the application's
wiring without billing a provider or claiming that a real model is correct.
Status and webhook flags still represent explicit network operations, even
with a fake model, so leave them off for the offline check.

## Why isolate the agent and the app?

A coding agent can run tools, read files and execute commands while developing
your project. Later, the application can read the same ticket data and make
model or HTTP requests without the coding agent being involved at all.
Confining only the editor misses the application's runtime access.

[Docker Sandboxes](https://docs.docker.com/ai/sandboxes/) provides microVM-based
isolation. Workspace mounts and policy still decide what crosses that boundary.
Mounting a directory exposes its contents; permitting a service lets requests
reach it. The useful question is not whether the app is in a sandbox, but
which files, destinations and credential-backed operations it can use there.

For this example, the intended answer is narrow: the synthetic ticket files
and the Gemini API host, with a separately approved runtime credential. No
status enrichment, webhook delivery or tracing. The rest of this tutorial
makes that decision visible rather than inferring permission from imports.

## Let a coding agent do the inspection

The repository includes a self-contained
[LangChain packaging skill](../skills/langchain-sandbox-kit/SKILL.md).
Ask your coding agent:

> Package my LangChain app at ./examples/ticket-triage to run in Docker Sandboxes.
> Inspect it without executing it. Ask about unresolved access and show me
> the generated package before requesting any permissions.

Point it at the skill explicitly, or copy the entire skill folder into your
own project's `.agents/skills/` for Codex or `.claude/skills/` for Claude Code.
Keep its scripts, templates and references together. No host-level skill
installation is needed, and this repository does not change personal agent
configuration. See [official discovery sources](provenance.md).

The skill runs a deterministic helper. You can run its first step yourself:

```bash
python3 skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py inspect --project examples/ticket-triage --entrypoint src/ticket_triage/app.py
```

The helper parses source and configuration without importing the application,
executing it or resolving dependencies. Findings have file:line evidence and
confidence labels. It reports provider suggestions, environment-variable names,
literal URL hosts, dynamic URLs, file reads and unknown integrations. It skips
private files and redacts secret-like literals.

Expect questions, not a complete permissions proof. Is `TRIAGE_STATUS_URL`
actually used in your deployment? Which exact host belongs there? Is tracing
on? Which model and data directory are intended? A package dependency can
suggest a provider host; it cannot prove that runtime configuration will use it.

Every current finding needs an explicit allow, deny or out-of-scope answer,
with a reason. An unresolved dynamic URL cannot become an allow rule until the
developer names its hosts. The helper will not auto-grant access, and the host
must still approve the resulting capability requests.

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

## The manual path starts from an agent.py template

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

## Run your app inside local Docker Sandboxes

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

The cloud file keeps the baked app and removes `workspace` entirely. Cloud
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

Review the effective policy, not only this mixin. Other kits and host/org
defaults can expand access. Use exact hosts, explicit denies where needed,
separate build and runtime permissions, and minimal mounted data. The helper
uses host-level `network-policy@1`; do not claim method/path filtering. More
granular @2 policy needs its own target-enforcement tests.

Proxy-managed credentials reduce secret exposure, but an allowed service still
accepts requests. A malicious instruction can ask the app to send sensitive
content to the permitted model endpoint or spend its quota. Sandboxing is not
a cure for prompt injection, and structured output is not proof of truth.

Record the actual local and cloud observations in the
[runtime matrix](evidence/runtime-matrix.md); those acceptance rows remain open.
