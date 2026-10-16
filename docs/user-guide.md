# Run an existing LangChain app

Keep your existing Python layout. Start with direct execution in the official
shell workload; package a reusable kit only when you need repeatable distribution
or cloud baking. LangChain needs no Sandbox API in its source.

## Prerequisites

Run commands from the repository root. Inspection needs Python 3.11+; lock
preparation uses uv 0.9.26. Runtime needs an approved supported Docker Sandboxes
host with `sbx`. No nested daemon, socket mount or host-global configuration
change is needed. All `sbx` commands here are **host steps, NOT RUN here**.

## 1. Preserve the raw app and prepare its lock

For the raw fixture, use a fresh directory:

```bash
cp -R skills/langchain-sandbox-kit/tests/fixtures/raw-agent /tmp/my-agent
cd /tmp/my-agent
uv init --bare --no-workspace --name single-file-agent --python 3.13.7
uv python pin 3.13.7
uv add --no-sync 'langchain==1.4.4' 'langchain-core==1.6.9' 'langchain-google-genai==4.4.0'
uv lock
cd -
```

This leaves `agent.py` unchanged and adds metadata. For your own app, inspect
existing metadata/build backends before tooling and choose compatible exact
pins. Do not initialize over an existing project blindly. See
[dependency constraints](../skills/langchain-sandbox-kit/references/dependencies.md).
Lock creation resolves packages; it does not run your app.

## 2. Inspect, ask and prepare direct access

```bash
python3 skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py inspect --project /tmp/my-agent --entrypoint agent.py --json /tmp/my-agent-inspection.json
python3 skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py direct --project /tmp/my-agent --entrypoint agent.py --answers examples/raw-agent.answers.json --out /tmp/my-agent-direct
```

These answers match only this raw fixture after the commands above. The
ready-locked `examples/single-file-agent` uses its own answers file instead.
For your app, use the [answer contract](../skills/langchain-sandbox-kit/references/answers.schema.md):
every finding needs allow, deny or out-of-scope plus a reason. Confirm exact
provider/custom base-URL hosts, model, tracing, file/config paths and optional
side effects. Never auto-grant from imports or leave an unknown dynamic URL
allowed. Static inspection is not a complete permission proof.

A coding agent can do these steps using [the bundled skill](../skills/langchain-sandbox-kit/SKILL.md).
Ask it to run your existing app, preserve layout, inspect without executing,
ask unresolved questions and prepare `direct`, not require a new kit.

Review ACCESS.md, RUN.md, setup-deps.sh, sbxenv.yaml, direct-manifest.json and
workspace/. No runtime starts automatically. Only sanitized selected files are
copied, retaining relative layout. Add required data/config paths explicitly.
Excluded .env/private/key/venv/cache files must stay out of the snapshot.
Use new output outside the app; exit 2 means missing/stale answers, 3 unsafe
input, 4 unsafe overwrite. `--force` only replaces unchanged owned output.

## 3. Manual alternative, without the helper

Read `agent.py` and dependencies and make the same decisions yourself: for this
fixture only the Gemini API, model gemini-2.5-flash, no tracing/private data.
Copy only needed files, not the whole project. From the repository root:

```bash
mkdir -p /tmp/manual-agent-direct/workspace
cp /tmp/my-agent/agent.py /tmp/my-agent/pyproject.toml /tmp/my-agent/uv.lock /tmp/my-agent/.python-version /tmp/manual-agent-direct/workspace/
cp skills/langchain-sandbox-kit/templates/direct-setup.txt /tmp/manual-agent-direct/setup-deps.sh
```

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

For another project, retain its package layout and explicitly copy reviewed
source, metadata and data. Never mount raw projects or parent directories.
`.dockerignore` is not a mount filter. Keep controls outside workspace/ and omit
shared skills. Read setup-deps.sh: it uses the workload's Python to fetch and
verify uv 0.9.26 for x86_64/aarch64, installs into the sandbox user's home and
runs `uv sync --locked`. No curl or git is required. Package build hooks run
inside the sandbox, not on the host.

## 4. Host: create and run the unchanged app

These commands use the manual directory/name. Assisted users follow their
RUN.md instead, consistently using `/tmp/my-agent-direct/sbxenv.yaml` and
sandbox `single-file`. Do not combine the two names.

Use an existing approved host credential, not a new key. The direct built-in
service is `google` (GOOGLE_API_KEY/GEMINI_API_KEY, x-goog-api-key header for
`generativelanguage.googleapis.com`), unlike optional kit service `gemini`.
The YAML holds a sentinel, never the real value. Inspect existing secrets and
policy first; `secret set` prompts securely on the host.

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
sbx policy rm network --sandbox manual-agent-direct --resource github.com,release-assets.githubusercontent.com,pypi.org,files.pythonhosted.org
sbx policy ls
sbx env exec /tmp/manual-agent-direct/sbxenv.yaml -- .venv/bin/python agent.py --fake-model
```

Review the plan before approval. Verify exec starts in the mounted workspace
with the expected pyproject.toml. Setup runs inside SBX using stdin, not as a host
script. Stop on unexpected binding requests: that approval interaction remains
unverified on this shell composition. Do not silently modify global bindings.
After setup remove bootstrap grants; inspect inherited policy because other
local/org rules can broaden or deny access independently of this plan.

Expected offline output: `{"category": "technical", "ticket_id": "T-101"}`.
For an interactive shell use `sbx env run /tmp/manual-agent-direct/sbxenv.yaml`,
activate `.venv/bin/activate`, then run `python agent.py --fake-model`.

## 5. Host: verify allowed and denied operations

Approve the input, model cost and timeout before the real call:

```bash
sbx env exec /tmp/manual-agent-direct/sbxenv.yaml -- python3 -c "import subprocess; subprocess.run(['.venv/bin/python', 'agent.py'], timeout=60, check=True)"
sbx env exec /tmp/manual-agent-direct/sbxenv.yaml -- python3 -c "import urllib.request; urllib.request.urlopen('https://example.com', timeout=10)"
sbx policy log
sbx env rm /tmp/manual-agent-direct/sbxenv.yaml
```

The allowed call should produce a valid category. The second request should be
rejected by policy; confirm a matching event and a reachable host-side origin
control. DNS/TLS/timeouts and origin HTTP errors are not confinement proof.
Check excluded files are absent without printing secrets. Review cleanup and
remaining scoped policy/secrets; leave shared bindings and unrelated rules alone.
Actual local/cloud SBX remains NOT RUN. Container checks alone cannot prove
proxy injection or SBX policy.

## Optional: reusable kit packaging

A kit distributes reusable environment, dependencies and policy. It is not a
LangChain conversion. The remaining sections preserve the larger ticket-triage
worked example and a fully manual single-file kit alternative. For the assisted
kit commands, first inspect ticket-triage and review its separate fixture answers:

```bash
python3 skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py inspect --project examples/ticket-triage --entrypoint src/ticket_triage/app.py
```

Optional builds need Docker buildx and pinned kit-tck. On Linux x86_64/aarch64,
with curl, tar, sha256sum, git and Go available:

```bash
bash scripts/install-ci-tools.sh /tmp/triage-tools
export PATH="/tmp/triage-tools:$PATH"
```

### Generate a separate kit build context

```bash
python3 skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py generate --project examples/ticket-triage --entrypoint src/ticket_triage/app.py --answers examples/ticket-triage.answers.json --out /tmp/my-ticket-triage-kit
python3 skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py explain --manifest /tmp/my-ticket-triage-kit/kit-manifest.json
```

Choose a new path outside the project. Existing nonempty output exits 4.
`--force` replaces only an unchanged helper-owned tree, never developer edits or
unowned files. Source input is not modified. Review the output:

| Artifact | Review |
| --- | --- |
| `ticket-triage.yaml` | v3 mixin, agent context, runtime allow/deny and credential request |
| `ticket-triage.dockerfile` | Pinned uv base/Python, locked install, scratch overlay |
| `app/`, `.dockerignore` | Selected snapshot with explicit context allowlist |
| `sbxenv.local.yaml` | Pinned shell workload and only the sanitized kit workspace |
| `sbxenv.cloud.yaml` | Same baked app with no host mount |
| `PERMISSIONS.md` | Reasons, evidence, excluded paths and boundaries |
| `kit-manifest.json` | Input, answers and output hashes |

The original ignore file is not reused as the build context policy. The helper
always removes private files even if that file would include them, and applies
additional project ignore rules conservatively. Symlinks and incomplete scans
block generation. Secret-like source must be removed, not acknowledged into an
image. Only root Python files, `src/`, lock/config and declared data are copied.

### Adapt the single-file kit template manually

No helper is needed on this path. The
[single-file kit](../examples/single-file-agent-kit/) is a template, not your
app or your answers; the [ticket-triage kit](../examples/ticket-triage-kit/)
shows a larger packaged `src/` app. From the repository root:

```bash
cp -R examples/single-file-agent-kit /tmp/manual-agent-kit
cd /tmp/manual-agent-kit
mv single-file.yaml manual-agent.yaml
mv single-file.dockerfile manual-agent.dockerfile
mv single-file-context.md manual-agent-context.md
```

Use `manual-agent` consistently, or replace it everywhere with your own name:

1. `app/`: remove the example files; copy your unchanged `agent.py`,
   `pyproject.toml`, `uv.lock`, `.python-version` and required data, never `.env`
   or private files. For requirements-only input, first run the
   [raw-script lock commands](../examples/single-file-agent/README.md#starting-with-just-agentpy-and-requirementstxt)
   in your app, after choosing compatible exact versions.
2. `manual-agent.yaml`: edit `displayName`, `version` and
   `provides: ["manual-agent@0.1.0"]`; set `agent-context@1`'s
   `config.contentFile: ./manual-agent-context.md`. Under `network-policy@1`,
   edit `config.runtime.allow` / `deny` to your exact hosts. Use the
   [provider host table](../skills/langchain-sandbox-kit/references/capabilities.md).
   Change `credential@1`'s `config.service`, `phase: runtime`, `apiKey.name`
   and `apiKey.inject` domain/header/format for your provider, or remove it for
   a keyless app. Gemini's template is service `gemini`, sentinel
   `GOOGLE_API_KEY`, `proxyManaged: true`, domain
   `generativelanguage.googleapis.com`, header `x-goog-api-key`, format `"%s"`.
   `optional: true` supports the offline run. No real key belongs here.
3. `manual-agent.dockerfile`: change every `/opt/single-file` to
   `/opt/manual-agent` and both `3.13.7` values to your exact Python pin.
   `COPY app/ ./` already includes allowlisted data. If you move data outside
   that tree, change the build COPY and final overlay COPY accordingly.
4. `.dockerignore`: retain `**` and explicit `!app/agent.py`,
   `!app/pyproject.toml`, `!app/uv.lock`, `!app/.python-version`, your data files
   and `!manual-agent-context.md`. Remove stale entries; never use `!**`.
5. `manual-agent-context.md`: use your launch command, for example
   `cd /opt/manual-agent/app && python agent.py`. The workload owns launch,
   identity and `sbx@1`; this context is guidance, not an entrypoint.
6. `sbxenv.local.yaml` / `sbxenv.cloud.yaml`: set `name: manual-agent`,
   update the app `kits` path if not `./`, and retain the pinned shell workload.
   Only local has `workspace: .`, pointing to the sanitized kit.
7. `PERMISSIONS.md`: replace every example allow/deny reason, model, data,
   tracing and credential decision, and the launch command, with your own.
8. Delete `kit-manifest.json`: manual edits invalidate helper hashes.
   This route uses neither the helper nor `explain` / `generate --force`;
   its overwrite checks do not apply.

Build and TCK-check the edited copy with a fresh layout path:

```bash
docker buildx build . -f manual-agent.yaml --progress plain --output type=cacheonly
docker buildx build . -f manual-agent.yaml --progress plain -t manual-agent:0.1.0 --output type=oci,dest=/tmp/manual-agent-layout,tar=false
kit-tck validate --verbose --layout /tmp/manual-agent-layout 0.1.0
```

### Probe your manual overlay

Still in `/tmp/manual-agent-kit`, load the overlay and compose an ordinary
Debian probe. It is not the SBX shell workload. The commands below assume your
app has the fixture's `--fake-model` mode; replace only that command with your
own offline invocation if needed. Do not run generated app source on the host.

```bash
docker buildx build . -f manual-agent.yaml --progress plain -t manual-agent:probe-overlay --load
docker build -t manual-agent:probe -f - . <<'DOCKERFILE'
FROM manual-agent:probe-overlay AS overlay
FROM debian:bookworm-slim@sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587
COPY --from=overlay /opt/manual-agent /opt/manual-agent
ENV PATH="/opt/manual-agent/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
DOCKERFILE
docker run --rm --network none --read-only --user 1000:1000 -e PYTHONDONTWRITEBYTECODE=1 manual-agent:probe sh -eu -c '
  cd /opt/manual-agent/app
  python agent.py --fake-model
  test -z "$(find /opt/manual-agent -name .env -o -name private -o -name id_rsa)"
'
```

Verify that the build succeeds, TCK passes, your own command produces its
expected offline output, and only reviewed source/dependencies/data appear in
the image. The path check is not a general secret detector: inspect the
allowlist and source for embedded keys too. Filesystem compatibility and absent
private files do not prove SBX policy, credential injection or microVM confinement.

### Check the packaged example instead

For the generated ticket-triage copy from step 4, rather than your manual app:

```bash
cd /tmp/my-ticket-triage-kit
docker buildx build . -f ticket-triage.yaml --progress plain --output type=cacheonly
docker buildx build . -f ticket-triage.yaml --progress plain -t ticket-triage:0.1.0 --output type=oci,dest=/tmp/new-triage-layout,tar=false
kit-tck validate --verbose --layout /tmp/new-triage-layout 0.1.0
```

Use a fresh layout. Version 0.1.0 identifies the app kit, not LangChain itself.
The [committed golden kit](../examples/ticket-triage-kit/) is byte-compared in
helper tests. Back at the repository root, run:

```bash
bash scripts/check-skill.sh
bash scripts/check-generated-kit.sh /tmp/another-fresh-triage-layout
```

The latter builds/exports, runs TCK and probes the overlay in an ordinary Debian
container: no network, read-only root, uid 1000. It verifies fake execution,
private-file absence and clean network failure. These recorded checks pass.
They do not establish microVM confinement, credential injection or effective SBX
policy. Actual shell-workload composition remains part of host acceptance.

### Host: run the optional kit inside local SBX

On the approved host, from the repository root:

```bash
sbx env plan /tmp/my-ticket-triage-kit/sbxenv.local.yaml
sbx env run --detach /tmp/my-ticket-triage-kit/sbxenv.local.yaml
sbx env exec /tmp/my-ticket-triage-kit/sbxenv.local.yaml -- sh -lc 'cd /opt/ticket-triage/app && python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model'
```

These commands use the copy generated and validated above. The repository's
`examples/ticket-triage-kit` is a prepackaged reference, not that output path.
If you chose a different output directory, change it on every command.
For the manual single-file kit, use this alternative host handoff instead,
with your own offline arguments if they differ (NOT RUN here):

```bash
sbx env plan /tmp/manual-agent-kit/sbxenv.local.yaml
sbx env run --detach /tmp/manual-agent-kit/sbxenv.local.yaml
sbx env exec /tmp/manual-agent-kit/sbxenv.local.yaml -- sh -lc 'cd /opt/manual-agent/app && python agent.py --fake-model'
```

The mixin adds app files and capabilities; the workload owns entrypoint, user
and `sbx@1`. Starting a sandbox is not starting the app: `env exec` runs it.
The optional credential means fake mode needs no secret. A real call needs an
existing, explicitly approved `gemini` service binding, not just a host env var.
Do not put the key into YAML or argv. Follow the [host handoff](acceptance-handoff.md)
for credential preparation, allowed and denied operations, boundary events and
origin controls; its status/webhook flags apply only to ticket-triage, not your
single-file app. A failed request alone is not proof of policy denial.

## Cloud and cleanup

```bash
sbx --cloud env plan /tmp/my-ticket-triage-kit/sbxenv.cloud.yaml
sbx --cloud env run --detach /tmp/my-ticket-triage-kit/sbxenv.cloud.yaml
sbx --cloud env exec /tmp/my-ticket-triage-kit/sbxenv.cloud.yaml -- sh -lc 'cd /opt/ticket-triage/app && python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model'
sbx --cloud env rm /tmp/my-ticket-triage-kit/sbxenv.cloud.yaml
sbx env rm /tmp/my-ticket-triage-kit/sbxenv.local.yaml
```

For the manual single-file kit, use its paths and launch command instead:

```bash
sbx --cloud env plan /tmp/manual-agent-kit/sbxenv.cloud.yaml
sbx --cloud env run --detach /tmp/manual-agent-kit/sbxenv.cloud.yaml
sbx --cloud env exec /tmp/manual-agent-kit/sbxenv.cloud.yaml -- sh -lc 'cd /opt/manual-agent/app && python agent.py --fake-model'
sbx --cloud env rm /tmp/manual-agent-kit/sbxenv.cloud.yaml
sbx env rm /tmp/manual-agent-kit/sbxenv.local.yaml
```

The host reports `sbx --cloud diagnose` passed authentication, API reachability
and subscription; the host cloud account and API are reachable. That host-reported
diagnosis was not independently verified for this walkthrough. Cloud runtime execution is still **NOT RUN**;
cloud-side secrets/bindings, upload/baking approval and actual allowed/denied
runs remain open. Cloud cannot mount your host workspace;
the app is already baked in. No cloud upload ran here. Repeat the same
allowed/denied checks; local acceptance is not cloud acceptance. Keep the same
account/endpoint/file paths for cleanup. This is cloud execution, not production
serving with ingress, autoscaling, durability or availability guarantees.

## Conclusion

Direct execution preserves the app and makes access choices visible; reusable packaging is optional.
Acceptance still requires actual local/cloud observations. Allowed APIs can
spend money and retain data; isolation does not fix prompt injection or model
correctness. See the [tutorial](run-your-langchain-in-docker-sandboxes.md), [source pins](provenance.md) and
[supporting policy lab](policy-lab-guide.md) for the next level of detail.
