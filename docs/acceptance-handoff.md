# Host acceptance: local, cloud and live model

**NOT RUN in the implementation sandbox.** `sbx` is absent. Do not install a
nested daemon, bridge a Docker socket, change global policy or run generated
source directly on the host to compensate. The source/build, TCK and container
results in [the matrix](evidence/runtime-matrix.md) are different evidence.

Run these from the repository root on the approved host. Prerequisites:
supported Docker Sandboxes, buildx, host approval of the reviewed mixin, and
existing provider access if a real call is approved. Keep the generated kit
unchanged while capturing evidence. Commands here are the current documented
grammar, not a claim that the target accepted them.

## H1 direct variant: existing app, no generated mixin

**NOT RUN.** First use `direct` as shown in the tutorial/README and review its
ACCESS.md, RUN.md, setup-deps.sh, workspace and manifest. Below uses the
ready-locked single-file example, output `/tmp/my-agent-direct`, name `single-file`.
Do not mount the raw app or controls. No live app call is repeated by the crew.

```bash
python3 skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py direct --project examples/single-file-agent --entrypoint agent.py --answers examples/single-file-agent.answers.json --out /tmp/my-agent-direct
sbx secret set google --sandbox single-file
sbx env plan /tmp/my-agent-direct/sbxenv.yaml
sbx env create /tmp/my-agent-direct/sbxenv.yaml
sbx policy ls
sbx policy allow network --sandbox single-file generativelanguage.googleapis.com
sbx policy deny network --sandbox single-file example.com
sbx policy allow network --sandbox single-file github.com,release-assets.githubusercontent.com,pypi.org,files.pythonhosted.org
sbx env exec /tmp/my-agent-direct/sbxenv.yaml -- pwd
sbx env exec -i /tmp/my-agent-direct/sbxenv.yaml -- sh < /tmp/my-agent-direct/setup-deps.sh
sbx policy rm network --sandbox single-file --resource github.com,release-assets.githubusercontent.com,pypi.org,files.pythonhosted.org
sbx policy ls
sbx env exec /tmp/my-agent-direct/sbxenv.yaml -- .venv/bin/python agent.py --fake-model
sbx env exec /tmp/my-agent-direct/sbxenv.yaml -- sh -c 'test ! -e .env && test ! -e private'
```

Use only an existing approved host credential. Built-in service `google` uses
GOOGLE_API_KEY/GEMINI_API_KEY placeholders and x-goog-api-key proxy injection;
the optional kit below uses its separately declared `gemini` service. The
host must review any unexpected binding prompt; this shell interaction remains
UNVERIFIED. No global binding is generated. Check working directory before setup.
Inspect inherited policy/credentials; one narrow allow is not an exclusive policy.

If separately approved for this host target, one bounded synthetic live request:

```bash
sbx env exec /tmp/my-agent-direct/sbxenv.yaml -- python3 -c "import subprocess; subprocess.run(['.venv/bin/python', 'agent.py'], timeout=60, check=True)"
```

Expected fake JSON: category technical, ticket_id T-101. Expected real result:
valid category from gemini-2.5-flash, max output 256, wall timeout 60s. This host
target test has NOT RUN; the earlier approved implementation-sandbox live call
does not prove this composition or authorize an additional unattended call.

Negative check and origin control (only run after host approves these destinations):

```bash
curl --connect-timeout 5 --max-time 10 -I https://example.com
sbx env exec /tmp/my-agent-direct/sbxenv.yaml -- python3 -c "import urllib.request; urllib.request.urlopen('https://example.com', timeout=10)"
sbx policy log
sbx env rm /tmp/my-agent-direct/sbxenv.yaml
```

Require a matching policy-denied boundary event; timeout, DNS, TLS or an origin
403 is insufficient. Record actual status/exit, effective policy and workload,
source hash, exclusion checks and cleanup. Do not record secrets. Inspect and
remove only this run's leftover scoped rules/secrets; do not prune shared bindings.
For an interactive session, `sbx env run /tmp/my-agent-direct/sbxenv.yaml`.
Cloud cannot mount this workspace: use the optional kit path in H2 only after
host-approved baking/transfer and separate cloud-side policy/secret setup.

## H1 optional kit: local SBX, fake first

```bash
sbx version
sbx env --help
sbx env run --help
sbx env exec --help
sbx ls
sbx env plan ./examples/ticket-triage-kit/sbxenv.local.yaml
sbx env run --detach ./examples/ticket-triage-kit/sbxenv.local.yaml
sbx env exec ./examples/ticket-triage-kit/sbxenv.local.yaml -- sh -lc 'cd /opt/ticket-triage/app && python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model'
sbx env exec ./examples/ticket-triage-kit/sbxenv.local.yaml -- sh -lc 'test ! -e /opt/ticket-triage/app/.env && test ! -e /opt/ticket-triage/app/private'
```

Expected fake output is JSON with `ticket_id: T-101`, category `technical`, and
a clearly synthetic summary. Record effective policy and composition, including
workload defaults and host/org rules. The file mounts only the sanitized kit
workspace; it does not expose the original app or host home directory.

### Credential preparation and allowed check (requires separate H3 approval)

Use the host's **existing** service `gemini` credential and binding approved for
`generativelanguage.googleapis.com`. For this third-party mixin, an explicit
injection-domain approval is required. The descriptor names `GOOGLE_API_KEY`
as the in-sandbox sentinel and rewrites `x-goog-api-key`. Do not pass the real
key with `--env`, place it in YAML, or paste it into evidence. A host shell's
`GEMINI_API_KEY` does not automatically bind that service.

The shape below is illustrative **only if the host must prepare a separate,
private override** using an already-approved vault reference. It is not a
checked-in secret or an instruction to create credentials. Choose the actual
reference with the operator; never copy this placeholder literally:

```yaml
secrets:
  gemini:
    ref: op://EXISTING_APPROVED_VAULT/EXISTING_ITEM/api-key
    snapshot: true
bindings:
  gemini:
    apiKey:
      domains: [generativelanguage.googleapis.com]
```

Such an override changes host-scoped/global resources and needs separate host
review; when used, pass its absolute private path after the committed file on
**every** plan/run/exec/rm command. It must stay outside shared workspaces and
the repo. Recreate an existing sandbox after credential/kit changes. Do not
prune global bindings without checking their other users.

Once the host has confirmed the binding and approved one model call:

```bash
sbx env exec -e TRIAGE_MODEL=gemini-2.5-flash -e LANGSMITH_TRACING=false ./examples/ticket-triage-kit/sbxenv.local.yaml -- sh -lc 'cd /opt/ticket-triage/app && python -m ticket_triage.app --ticket data/tickets/t-101.json'
```

Expected: valid JSON citing T-101 and evidence of allowed Gemini traffic, without
printing credentials. If the SDK/proxy integration fails, retain the redacted
failure; do not broaden policy or substitute fake output as live success.

### Denied checks, in the same composed sandbox

```bash
sbx env exec -e TRIAGE_STATUS_URL=https://example.com ./examples/ticket-triage-kit/sbxenv.local.yaml -- sh -lc 'cd /opt/ticket-triage/app && python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model --status'
sbx env exec ./examples/ticket-triage-kit/sbxenv.local.yaml -- python -c 'import httpx; httpx.get("https://example.com", timeout=5).raise_for_status()'
sbx env exec ./examples/ticket-triage-kit/sbxenv.local.yaml -- python -c 'import httpx; httpx.get("https://status.example.invalid", timeout=5).raise_for_status()'
sbx env exec ./examples/ticket-triage-kit/sbxenv.local.yaml -- sh -lc 'cd /opt/ticket-triage/app && python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model --post-webhook'
```

Expected: nonzero status, status CLI exit 2 without URL/key details; no completed
webhook POST. `hooks.example.invalid` and `status.example.invalid` deliberately
do not resolve publicly. Their DNS failures alone **do not prove policy
denial**. Capture boundary events identifying the denied host; `example.com`
provides a resolvable-origin control. If host rules allow it, record FAIL and
resolve the policy with the host, not by silently calling it secure. Do not
send real customer data to any control endpoint. Retain a separately approved
outside-boundary origin check to distinguish origin 403 from boundary 403.

```bash
sbx env rm ./examples/ticket-triage-kit/sbxenv.local.yaml
```

## H2: cloud SBX

The host reports that `sbx --cloud diagnose` passed authentication, API
reachability and subscription: the host cloud account and API are reachable.
This is host-reported diagnosis, not a crew observation or runtime acceptance.
Cloud runtime execution is still **NOT RUN**. What remains is explicit approval
for cloud baking/upload of the sanitized app, a separately approved cloud-side
Gemini secret/binding, and the actual allowed/denied runs. The crew did not log in, create
credentials, upload content or publish images. Check target support for v3 kit
credentials before proceeding. No host mount is present in this cloud file.

```bash
sbx --cloud --help
sbx --cloud env --help
sbx --cloud env plan ./examples/ticket-triage-kit/sbxenv.cloud.yaml
sbx --cloud env run --detach ./examples/ticket-triage-kit/sbxenv.cloud.yaml
sbx --cloud env exec ./examples/ticket-triage-kit/sbxenv.cloud.yaml -- sh -lc 'cd /opt/ticket-triage/app && python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model'
sbx --cloud env exec ./examples/ticket-triage-kit/sbxenv.cloud.yaml -- sh -lc 'test ! -e /opt/ticket-triage/app/.env && test ! -e /opt/ticket-triage/app/private'
```

After a separate host approval for cloud live usage, run the allowed check and
all four denied checks with the same expected exits, boundary-event and
origin-control requirements:

```bash
sbx --cloud env exec -e TRIAGE_MODEL=gemini-2.5-flash -e LANGSMITH_TRACING=false ./examples/ticket-triage-kit/sbxenv.cloud.yaml -- sh -lc 'cd /opt/ticket-triage/app && python -m ticket_triage.app --ticket data/tickets/t-101.json'
sbx --cloud env exec -e TRIAGE_STATUS_URL=https://example.com ./examples/ticket-triage-kit/sbxenv.cloud.yaml -- sh -lc 'cd /opt/ticket-triage/app && python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model --status'
sbx --cloud env exec ./examples/ticket-triage-kit/sbxenv.cloud.yaml -- python -c 'import httpx; httpx.get("https://example.com", timeout=5).raise_for_status()'
sbx --cloud env exec ./examples/ticket-triage-kit/sbxenv.cloud.yaml -- python -c 'import httpx; httpx.get("https://status.example.invalid", timeout=5).raise_for_status()'
sbx --cloud env exec ./examples/ticket-triage-kit/sbxenv.cloud.yaml -- sh -lc 'cd /opt/ticket-triage/app && python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model --post-webhook'
```

If using a private cloud override, consistently
include it on every command, separate from any local override. Then:

```bash
sbx --cloud env rm ./examples/ticket-triage-kit/sbxenv.cloud.yaml
```

This runs an app in cloud isolation; it does not establish production serving,
ingress, autoscaling, SLOs, durability, audit retention or cost controls.

## H3: live model in the implementation sandbox

**PASS after explicit host authorization**, using the existing proxy-managed
route only. [Exact evidence](evidence/live-model.txt): one synthetic T-101 ticket,
`gemini-2.5-flash`, max_tokens 256, 60s timeout, no retry. Result category was
technical and cited T-101. No credentials were copied or created.
This was an app call inside the implementation sandbox, not a new local/cloud
SBX composition test. It does not close H1/H2 or prove denied-operation policy.
The editorial key was not treated as blanket permission: the task leader's
separate bounded authorization was required and recorded before the call.

## Paste results here after host execution

For each class record UTC time, exact commit, host/CLI version, target local or
cloud, commands and exit codes, redacted JSON, effective policy/binding names
(not values), allowed request evidence, denied boundary events, origin control,
secret-file absence and cleanup. Update the runtime matrix and local runtime
bean only after actual observation. Independent exact-commit QC remains separate.
