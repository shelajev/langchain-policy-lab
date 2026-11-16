# Run single-file-agent-kit in Docker Sandboxes

This directory is a generated mixin kit. It adds the reviewed app snapshot in `app/`, its locked Python
environment, and the access requests in PERMISSIONS.md to Docker's `shell` agent. The `shell` agent is the
workload: it owns the sandbox user, entrypoint, and session. Generated files grant no permissions by
themselves, and allow requests do not form an exclusive allowlist under composed policy; review
PERMISSIONS.md and every prompt Docker Sandboxes shows before approving it.

Keep this directory named `single-file-agent-kit`. Its descriptor (`single-file-agent-kit.yaml`), recipe (`single-file-agent-kit.dockerfile`), and
agent context (`single-file-agent-kit-context.md`) follow the kit filename convention. Run all host `sbx` commands below
from the parent directory that contains `single-file-agent-kit/`.

## 1. Create the sandbox

```bash
sbx run --detach shell --kit ./single-file-agent-kit --name single-file-agent-kit ./single-file-agent-kit
```

Run this on your host. It composes the `shell` agent with this kit, mounts this generated directory (not
your original project) as the sandbox workspace, and prints the sandbox ID without opening a shell.

## 2. For live use: store the model provider secret for this sandbox only

```bash
sbx secret set google --sandbox single-file-agent-kit
```

Skip this step for an offline or fake-model run that needs no key. Otherwise run it on your host; `sbx` prompts for the provider key. Do not pass it with `--token`, write it
into a file in this directory, or export it into the sandbox. The kit sets only a placeholder sentinel
environment variable inside the sandbox, and the Docker Sandboxes proxy injects the selected header
only on supported matching requests to the configured provider host.

## 3. Open a shell and run the app

```bash
sbx run --name single-file-agent-kit
```

Run the command above on your host to open a shell. Choose a mode before running app commands inside the guest:

The reviewed command has no `--fake-model` flag and may call a live provider. If the app documents `--fake-model` (as this repository's single-file example does), this is an offline alternative:
```bash
cd /opt/single-file-agent-kit/app
/opt/single-file-agent-kit/venv/bin/python agent.py --fake-model
```
Use that alternative only if the app supports it. Otherwise use the reviewed command below after completing the secret step and approving any live call. These are alternatives: do not run both just because both are shown.

Reviewed launch command:

```bash
cd /opt/single-file-agent-kit/app
/opt/single-file-agent-kit/venv/bin/python agent.py
```

Compare results with the app's own documented offline check before attempting live use. Fake-model checks and live prerequisites are documented for the [single-file example](https://github.com/shelajev/langchain-policy-lab/tree/main/examples/single-file-agent) and [ticket-triage example](https://github.com/shelajev/langchain-policy-lab/tree/main/examples/ticket-triage). A successful process exit alone does not establish answer quality.

Run `exit` to leave the guest shell before host cleanup.

Use the kit's interpreter path as shown. Plain `python` in the `shell` agent is the system Python, which does
not have the app's dependencies.

## 4. Clean up

```bash
sbx rm single-file-agent-kit
```

Run this on your host. `sbx rm` asks for confirmation, then removes the sandbox and its sandbox-scoped
secrets. Global secrets and policy rules persist across runs; check them with `sbx secret ls` and `sbx policy ls`.

## Optional: cloud and Docker Hub

Not run or verified with this kit: `sbx --cloud run --detach shell --kit ./single-file-agent-kit --name single-file-agent-kit` starts a cloud
sandbox without a local workspace mount. It builds the kit in Docker's cloud, so `app/` leaves your machine,
and the cloud sandbox needs its own separate secret and policy. Publishing the kit to a registry such as Docker
Hub shares the same `app/` snapshot with anyone who can pull it. Neither option is needed to run locally.
