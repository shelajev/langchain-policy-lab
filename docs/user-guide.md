# Package an existing LangChain app

Use a normal Python app, inspect its resources, and review its Docker Sandboxes
packaging before you grant access. The coding-agent example uses ticket-triage;
the manual path adapts a single-file kit for your own `agent.py`. Neither app
needs a Sandbox API in its code.

## Prerequisites

Run commands from this repository root unless stated. You need Python 3.11+
for the stdlib helper; uv 0.9.26 and Python 3.13.7 for the example; Docker with
buildx for packaging; and `kit-tck` built from the pinned spec. On Linux
x86_64/aarch64, install project tools in a chosen scratch directory:

```bash
bash scripts/install-ci-tools.sh /tmp/triage-tools
export PATH="/tmp/triage-tools:$PATH"
```

On another host, build kit-tck from the exact commit in [provenance](provenance.md).
No key is needed for offline tests. Actual runtime needs a supported host with
Docker Sandboxes and `sbx`. Do not start a nested daemon inside a sandbox.
The implementation environment lacked `sbx`: local/cloud commands below are a
host handoff, not observed success. One separately authorized live-model call
passed inside that implementation environment, not local/cloud SBX acceptance.
See [the matrix](evidence/runtime-matrix.md).

### Already have agent.py?

Start with your file, without restructuring it. The helper accepts a root
Python entrypoint as well as a packaged app:

```bash
python3 skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py inspect --project examples/single-file-agent --entrypoint agent.py
```

For your own project, substitute its directory and entrypoint. If it only has
requirements, review those dependencies and any build configuration, create a
normal `pyproject.toml` with intended exact pins and `.python-version`, then run
`uv lock` in an approved development environment. Preserve `agent.py`; no
Sandbox API or `src/` migration is required. Choose `python agent.py` (plus its
existing arguments) as the reviewed launch command. See the
[single-file fixture](../examples/single-file-agent/README.md).

## 1. Check the existing app

```bash
bash scripts/check-example.sh
```

This syncs the frozen lock, runs four offline tests and one fake-model request.
Observed output:

```json
{"category": "technical", "summary": "Synthetic offline classification; investigate the reported issue.", "ticket_id": "T-101"}
```

The fake model checks pipeline wiring, not answer quality. Optional status fetch
and webhook flags are not enabled. LangSmith tracing is left off. A live run
requires separate provider-use approval and an existing runtime credential.

## 2. Inspect without executing input

```bash
python3 skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py inspect --project examples/ticket-triage --entrypoint src/ticket_triage/app.py
```

Inspection parses Python AST, TOML and lock metadata, without imports, resolvers
or project subprocesses. Findings carry IDs, file:line evidence and
declared/inferred/unresolved confidence. URL evidence reveals hosts only, not
paths or embedded credentials. Secret-like source literals are redacted and
block packaging. `.env`, private/key files and ignored paths are excluded.

The report asks about Gemini, model selection, status enrichment, webhook,
tracing, data reads and test-only sockets. All findings require decisions.
Static inspection cannot prove that runtime config or a plugin will not need
other resources. Ask the developer about their full intended use.

For another app, change project and entrypoint. Supported generation layout:
root Python files or packaged `src/`, exact direct pins, `pyproject.toml`, hashed
public-PyPI `uv.lock` and exact `.python-version`. Requirements-only input can
be inspected; generation needs reviewed lock setup first. Custom registries, optional
dependency selections and VCS/path dependencies need manual packaging. Resolve
locks yourself in an approved environment; the helper never executes a resolver.

## 3. Answer resource questions

Read the [worked answers](../examples/ticket-triage.answers.json) and
[answer contract](../skills/langchain-sandbox-kit/references/answers.schema.md).
Each finding ID has an action and reason. Stale IDs fail generation. The example
explicitly allows Gemini and requests service `gemini` at runtime only. It
denies status/webhook destinations and tracing, declares `data/tickets` as data,
and confirms `gemini-2.5-flash`. These are app-specific developer choices.

Dynamic URLs need named hosts before an allow decision. Wildcard/IP access
requires an explicit broad-access exception and is flagged; prefer exact hosts.
Do not put credential values into answers, reasons or reports.

For the assisted path, ask your agent to read the
[skill](../skills/langchain-sandbox-kit/SKILL.md) and perform steps 2 through 4:

> Package my LangChain app at ./ticket-triage to run in Docker Sandboxes. Inspect
> first and ask which resources I want it to use. Do not grant access automatically.

For automatic discovery in your own repo, copy the whole skill directory into
`.agents/skills/` for Codex or `.claude/skills/` for Claude Code. No personal host
installation is needed. Manual use below bypasses the agent, not the review.

## 4. Generate a separate build context

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

## 5. Adapt the single-file template manually

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

## 6. Run the app inside local SBX

On the approved host, from the repository root:

```bash
sbx env plan ./examples/ticket-triage-kit/sbxenv.local.yaml
sbx env run --detach ./examples/ticket-triage-kit/sbxenv.local.yaml
sbx env exec ./examples/ticket-triage-kit/sbxenv.local.yaml -- sh -lc 'cd /opt/ticket-triage/app && python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model'
```

For your generated `/tmp` copy, substitute its absolute environment-file path.
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

## 7. Adapt for cloud and clean up

```bash
sbx --cloud env plan ./examples/ticket-triage-kit/sbxenv.cloud.yaml
sbx --cloud env run --detach ./examples/ticket-triage-kit/sbxenv.cloud.yaml
sbx --cloud env exec ./examples/ticket-triage-kit/sbxenv.cloud.yaml -- sh -lc 'cd /opt/ticket-triage/app && python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model'
sbx --cloud env rm ./examples/ticket-triage-kit/sbxenv.cloud.yaml
sbx env rm ./examples/ticket-triage-kit/sbxenv.local.yaml
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
and subscription; the host cloud account and API are reachable. The crew did
not observe that diagnosis. Cloud runtime execution is still **NOT RUN**;
cloud-side secrets/bindings, upload/baking approval and actual allowed/denied
runs remain open. Cloud cannot mount your host workspace;
the app is already baked in. No cloud upload ran here. Repeat the same
allowed/denied checks; local acceptance is not cloud acceptance. Keep the same
account/endpoint/file paths for cleanup. This is cloud execution, not production
serving with ingress, autoscaling, durability or availability guarantees.

## Conclusion

Reviewable packaging preserves the app and makes access choices visible.
Acceptance still requires actual local/cloud observations. Allowed APIs can
spend money and retain data; isolation does not fix prompt injection or model
correctness. See the [tutorial](run-your-langchain-in-docker-sandboxes.md),
[evidence matrix](evidence/runtime-matrix.md), [source pins](provenance.md) and
[supporting policy lab](policy-lab-guide.md) for the next level of detail.
