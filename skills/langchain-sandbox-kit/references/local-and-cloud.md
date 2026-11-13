# Running the generated kit

The generated `RUN.md` is the source of truth for one kit. This page explains
why its steps are in that order and what each one does and does not prove.

## Composition

`sbx run shell --kit ./NAME` composes Docker's built-in `shell` agent (the
workload) with the generated mixin. `sbx run --help` documents both the `shell`
agent and `--kit` for a local mixin directory; the kit-v3 authoring guide
documents `sbx run ./<workload> --kit ./<kit> .` for composed mixins. The
trailing `./NAME` is the workspace: mount the generated kit directory, never the
original project, parent directories or credential stores. The app itself runs
from the baked copy under `/opt/NAME/app`.

Keep the output directory named after the descriptor stem (`NAME/NAME.yaml`,
`NAME/NAME.dockerfile`), the layout the kit authoring guide uses.

## Order of host steps

1. `sbx run --detach shell --kit ./NAME --name NAME ./NAME` creates the sandbox
   and prints its ID. Docker Sandboxes resolves the local kit directory and
   applies its network and credential requests; answer any approval prompt only
   after reading PERMISSIONS.md. Read it first
   and inspect host or organization defaults: unioned allows from other sources
   can widen access, while explicit denies win.
2. `sbx secret set SERVICE --sandbox NAME` stores the provider key for that one
   sandbox. Run it after the sandbox exists so the scope names a real sandbox.
   `sbx` prompts for the value. Avoid `--token`, which `sbx` itself marks less
   secure because it lands in shell history. `--ref` (1Password or AWS Secrets
   Manager) and `--command` store a secret source instead of a value.
3. `sbx run --name NAME` re-attaches a shell. Run the app with
   `/opt/NAME/venv/bin/python`. The kit's credential entry sets the app's
   environment variable (for example `GOOGLE_API_KEY`) to a placeholder; the
   proxy adds the real key only on requests to the allowed provider host.
4. `sbx rm NAME` removes the sandbox. Review remaining sandbox-scoped secrets
   and `sbx policy ls` rules afterwards.

An app with a fake or offline mode can run before step 2; it needs no secret.

## Checking the boundary

Allowed provider traffic working is not proof that other traffic is blocked.
Try a deliberately denied but resolvable destination, then confirm a matching
denial in the policy log (`sbx policy log`) and an origin control from the host.
DNS, TLS or timeout failures alone do not prove confinement. Check that `.env`
and private files are absent without printing secret content. Build, kit-tck and
container checks are not sandbox runtime evidence.

## Cloud (optional)

`sbx --cloud run` accepts a kit reference and has no host workspace, so no path
follows the agent: `sbx --cloud run --detach shell --kit ./NAME --name NAME`.
Baking a mixin with build content creates a fresh cloud sandbox and sends the
kit's content, including `app/`, to Docker's cloud. Cloud sandboxes need their
own secrets, network approvals and allowed/denied checks; local secrets and
policy do not carry over. Check `sbx --cloud --help` for the verbs your CLI
supports. Cloud is not a production serving deployment: lifecycle, ingress,
scaling, retention, audit and cost remain application work.

## Publishing (optional)

A kit is an OCI artifact. The kit-v3 guide publishes with the same build that
produced the verified kit, both platforms in one invocation:

```bash
docker buildx build . -f NAME.yaml --platform linux/amd64,linux/arm64 --push \
  -t docker.io/ORG/NAME:0.1.0 -t docker.io/ORG/NAME:latest
```

Current `sbx kit --help` also lists `pack`, `push`, `sign` and `verify`; check
their help before using them. Others then run `sbx run shell --kit ORG/NAME:0.1.0`.
Publishing distributes the app snapshot and its access requests: review the
data, licensing and repository visibility first.

## Pre-checks without a sandbox

From the kit directory, with Docker buildx and `kit-tck` from the
docker/sandbox-kit-spec repository:

```bash
docker buildx build . -f NAME.yaml --output type=cacheonly
docker buildx build . -f NAME.yaml -t NAME:0.1.0 --output type=oci,dest=/tmp/NAME-layout,tar=false
kit-tck validate --layout /tmp/NAME-layout 0.1.0
```

The `-t NAME:0.1.0` tag sets the layout's reference name; `kit-tck` resolves
the `0.1.0` argument against it and fails with `not found` without the tag.

Authoritative specification: github.com/docker/sandbox-kit-spec at the pin in
[capabilities](capabilities.md). Docker docs: docs.docker.com/ai/sandboxes/.
