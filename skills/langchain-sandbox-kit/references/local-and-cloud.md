# Direct local execution first

Use `direct` and review its ACCESS.md/RUN.md before host approval. The pinned
official shell workload has Python, but not uv, curl or git. Its generated
setup-deps.sh downloads uv 0.9.26 from the official release, verifies SHA-256,
installs only into the sandbox user's home and runs `uv sync --locked`.

Only `workspace/` is mounted; keep the control files beside it. `.dockerignore`
does not filter direct mounts. Do not mount the raw project, parent directories,
personal skills or credential stores. The generated environment omits shared skills.

Host steps (NOT RUN here), from the generated direct directory:

```bash
sbx secret set google --sandbox single-file
sbx env plan ./sbxenv.yaml
sbx env create ./sbxenv.yaml
```

Use the actual sandbox name and provider in your output. Built-in Google uses
service `google`, GOOGLE_API_KEY/GEMINI_API_KEY placeholders and proxy injection;
this differs from service `gemini` declared by the optional generated mixin.
Only use an existing host-approved credential, never put its value into YAML.
The host must review any binding prompt; direct does not write global bindings.

Follow RUN.md's exact scoped `sbx policy allow network --sandbox NAME HOST`
and `deny` commands, including temporary bootstrap destinations. Inspect inherited
policy first. Then `sbx env exec -i ./sbxenv.yaml -- sh < setup-deps.sh` runs
setup inside the sandbox, not on the host. Verify the working directory first.
Remove temporary grants with `sbx policy rm network --sandbox NAME --resource HOST`.
Run your launch with `sbx env exec ./sbxenv.yaml -- .venv/bin/python agent.py`,
or use `sbx env run ./sbxenv.yaml` and activate the venv in the interactive shell.
Use app-specific arguments and separately approve model costs/data.

Check a deliberately denied resolvable destination against policy events and an
origin control. DNS/TLS/timeout failures alone do not prove confinement. Check
excluded files are absent without printing secret content. Clean up with
`sbx env rm ./sbxenv.yaml` and review remaining scoped rules/secrets.

The exact CLI/file syntax is documentation-verified; actual local SBX remains
NOT RUN. See the repository's direct-first tooling evidence for source URLs.

## Cloud requires a transfer, not a local mount

Cloud cannot mount workspace/. Remove local workspace/skills settings and use
the optional baked kit below (or a separately approved documented file transfer).
No upload is authorized by generating a plan. Cloud needs its own secret,
credential-domain approvals and network policy, with allowed/denied tests there.
The host reports cloud diagnose passed auth/API/subscription; that does not
establish cloud runtime behavior. Cloud SBX remains NOT RUN.

## Optional: run from the generated kit directory

Prerequisites: Docker buildx with the pinned v3 frontend, `kit-tck`, and a host
with supported Docker Sandboxes / `sbx`. Build before approving runtime access:

```bash
docker buildx build . -f NAME.yaml --progress plain --output type=cacheonly
docker buildx build . -f NAME.yaml --output type=oci,dest=/tmp/NEW-layout,tar=false
kit-tck validate --layout /tmp/NEW-layout 0.1.0
sbx version
sbx env --help
sbx env plan ./sbxenv.local.yaml
sbx env run --detach ./sbxenv.local.yaml
sbx env exec ./sbxenv.local.yaml -- sh -lc 'cd /opt/NAME/app && python -m PACKAGE.app --fake-model --ticket data/tickets/TICKET.json'
sbx env rm ./sbxenv.local.yaml
```

Replace NAME, PACKAGE and ticket with the reviewed context command. The local
workspace is the generated, sanitized kit directory, not the original app.
Review host/org defaults and other kits: unioned allows may expand access;
explicit denies win but unknown dynamic hosts cannot all be enumerated.

For cloud, use `sbx --cloud env plan/run/exec/rm ./sbxenv.cloud.yaml`. That file
omits `workspace` entirely. The app is baked into the mixin. Check
`sbx --cloud --help` and target credential support first. The host reports
`sbx --cloud diagnose` passed authentication, API reachability and subscription:
the host cloud account and API are reachable, not a crew-observed result.
Cloud runtime execution is still NOT RUN. Cloud-side secret/service/domain
binding, baking/upload approval and actual allowed/denied runs remain open.
Cloud baking may upload app content: review and approve before executing it.
Do not publish an image or create credentials just to finish a test.
See Docker's `reference/cli/sbx/env/` and `ai/sandboxes/cloud/usage/` docs.

Local and cloud credentials/policies are separate. A cloud execution is not a
production serving deployment: lifecycle, ingress, scaling, retention, audit,
availability and cost controls remain application/operator work.

Verify allowed API traffic and deliberate denied requests under the effective
policy, distinguishing boundary denial from an origin 403/DNS failure. Compare
with an approved origin control, inspect policy events, and retain redacted
results. A network-none container test or TCK is not this runtime evidence.
