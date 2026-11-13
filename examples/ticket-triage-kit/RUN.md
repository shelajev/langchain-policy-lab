# Run ticket-triage-kit in Docker Sandboxes

This directory is a generated mixin kit. It adds the reviewed app snapshot in `app/`, its locked Python
environment and the access requests in PERMISSIONS.md to Docker's `shell` agent. The `shell` agent is the
workload: it owns the sandbox user, entrypoint and session. Nothing here grants access by itself; review
PERMISSIONS.md and every prompt Docker Sandboxes shows before approving it.

Keep this directory named `ticket-triage-kit`. Its descriptor (`ticket-triage-kit.yaml`), recipe (`ticket-triage-kit.dockerfile`) and
agent context (`ticket-triage-kit-context.md`) follow the kit filename convention. Run the host commands below from
the directory that contains `ticket-triage-kit/`.

## 1. Create the sandbox

```bash
sbx run --detach shell --kit ./ticket-triage-kit --name ticket-triage-kit ./ticket-triage-kit
```

This composes the `shell` agent with this kit, mounts this generated directory (not your original project)
as the workspace, and prints the sandbox ID without opening a session.

## 2. Store the model provider secret for this sandbox only

```bash
sbx secret set google --sandbox ticket-triage-kit
```

`sbx` prompts for the value. Do not pass it with `--token`, put it in a file in this directory, or
export it into the sandbox. The kit sets a placeholder environment variable and the Docker Sandboxes proxy
adds the real key only to requests for the allowed provider host.

## 3. Open a shell and run the app

```bash
sbx run --name ticket-triage-kit
```

Inside the sandbox:

```bash
cd /opt/ticket-triage-kit/app
/opt/ticket-triage-kit/venv/bin/python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model
```

Use the kit's interpreter path as shown. Plain `python` in the `shell` agent is the system Python, which does
not have the app's dependencies.

## 4. Clean up

```bash
sbx rm ticket-triage-kit
```

`sbx rm` asks for confirmation, then removes the sandbox and the secrets scoped to it. Global secrets and
policy rules stay: check `sbx secret ls` and `sbx policy ls`.

## Optional: cloud and Docker Hub

Not verified with this kit: `sbx --cloud run --detach shell --kit ./ticket-triage-kit --name ticket-triage-kit` starts a cloud
sandbox without a workspace path. It builds the kit in Docker's cloud, so `app/` leaves your machine, and the
cloud sandbox needs its own secret. Publishing the kit to a registry such as Docker Hub shares the same app
snapshot with anyone who can pull it. Neither is needed to run locally.
