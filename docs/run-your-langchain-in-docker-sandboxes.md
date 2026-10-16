# Run your LangChain in Docker Sandboxes

Your LangChain app should not inherit everything your laptop can reach. It
needs a model endpoint and some input files. That does not mean it needs your
home directory, every credential in your shell, or an unrestricted route to
the network. The same distinction matters when a coding agent is editing the
app and when the app itself is processing an untrusted ticket.

This tutorial packages an existing Python app as a Docker Sandboxes v3 mixin.
You inspect its resources, answer concrete permission questions, review the
package and run the app inside a sandbox. There is an agent-assisted path and
an equivalent manual path. Both use the same ticket-triage app and files.

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
the pinned `kit-tck`; the [guide](user-guide.md) shows its user-local installer.
Actual sandbox steps need a supported Docker Sandboxes host with `sbx`, not a
nested daemon. No API key is needed for this first command, from the repo root:

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

> Package my LangChain app at ./ticket-triage to run in Docker Sandboxes.
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

## The manual path uses the same kit

You do not need a coding agent or a generator to understand the result. The
[committed kit](../examples/ticket-triage-kit/) is the exact golden output of
the same app and reviewed answers. Copy it to a new directory to work manually:

```bash
cp -R examples/ticket-triage-kit /tmp/manual-ticket-triage-kit
cd /tmp/manual-ticket-triage-kit
```

Inspect `app/` against the existing example, then review
`ticket-triage.yaml`, `ticket-triage.dockerfile`, `PERMISSIONS.md` and both
environment files. For another app, replace the sanitized source/lock/data
and adjust the paths, provides name, capabilities and context command together.
Do not copy its answers as your own.

The descriptor's important distinction is `kind: mixin`. Its runtime network
request allows `generativelanguage.googleapis.com`, denies the example webhook
and status hosts, and requests an optional proxy-managed runtime credential.
The credential names `GOOGLE_API_KEY` for the SDK's in-sandbox sentinel and
rewrites `x-goog-api-key` only for that allowed domain. The real credential
belongs at the boundary, not in the app snapshot.

The Dockerfile starts from the digest-pinned uv image, installs exact Python
3.13.7, uses `uv sync --locked --no-dev --no-editable`, and copies the result
into a scratch overlay at `/opt/ticket-triage`. The frozen lock includes
transitive artifact hashes and pinned build constraints. Runtime policy does
not govern the earlier image-build downloads; those are a separate supply-chain
surface to review.

A mixin does not own `ENTRYPOINT`, `CMD`, runtime user or `sbx@1`. The pinned
shell workload in each environment file owns launch and identity. The context
file explains how to run the app; it does not run it automatically.

Build the manual copy and validate its artifact:

```bash
docker buildx build . -f ticket-triage.yaml --progress plain --output type=cacheonly
docker buildx build . -f ticket-triage.yaml --progress plain -t ticket-triage:0.1.0 --output type=oci,dest=/tmp/manual-triage-layout,tar=false
kit-tck validate --verbose --layout /tmp/manual-triage-layout 0.1.0
```

Use a fresh layout path. Back at the repository root,
`bash scripts/check-generated-kit.sh /tmp/another-fresh-layout` also probes the
overlay in a network-none, read-only, nonroot Debian container. That verifies
application/filesystem compatibility with that probe base, not the actual SBX
workload composition or its network boundary. Those remain host checks.

## Run your app inside local Docker Sandboxes

On the approved host, from the repository root:

```bash
sbx env plan ./examples/ticket-triage-kit/sbxenv.local.yaml
sbx env run --detach ./examples/ticket-triage-kit/sbxenv.local.yaml
sbx env exec ./examples/ticket-triage-kit/sbxenv.local.yaml -- sh -lc 'cd /opt/ticket-triage/app && python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model'
```

For your generated or manual copy, use its absolute environment-file path.
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

Acceptance also needs deliberate negative tests. Under the same composition,
try status enrichment to `example.com`, direct HTTP to the denied destinations,
and the webhook flag. Check that `.env` and private data are absent. Retain
boundary events, not just error text. The illustrative `.invalid` webhook can
fail DNS even with no policy at all; an origin 403 can also resemble a boundary
403. The handoff includes resolvable-origin controls and expected exits.

## Cloud changes the resources, not the app

The cloud file keeps the baked app and removes `workspace` entirely. Cloud
cannot mount the host directory. With approved upload/baking, existing login
and compatible target support:

```bash
sbx --cloud env plan ./examples/ticket-triage-kit/sbxenv.cloud.yaml
sbx --cloud env run --detach ./examples/ticket-triage-kit/sbxenv.cloud.yaml
sbx --cloud env exec ./examples/ticket-triage-kit/sbxenv.cloud.yaml -- sh -lc 'cd /opt/ticket-triage/app && python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model'
```

The target needs its own secret and explicit domain approval for a live call.
Repeat allowed and denied checks there. A local success would not prove cloud
credential support, policy or cleanup. These cloud commands were not executed
in the implementation environment, and no image was published or app uploaded.

Clean up each environment using the same account, target and file paths:

```bash
sbx --cloud env rm ./examples/ticket-triage-kit/sbxenv.cloud.yaml
sbx env rm ./examples/ticket-triage-kit/sbxenv.local.yaml
```

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
