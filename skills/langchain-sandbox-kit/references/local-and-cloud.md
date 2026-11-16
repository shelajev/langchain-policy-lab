# Running the generated kit

The generated `RUN.md` is the source of truth for one kit. This page walks
through why its steps sit in that order, where each command runs, and what each
step actually proves (and does not prove).

## Composition

`sbx run shell --kit ./NAME` composes Docker's built-in `shell` agent (the
workload) with your generated mixin kit. `sbx run --help` documents both the
`shell` agent and `--kit` for a local mixin directory, while the kit-v3
authoring guide documents `sbx run ./<workload> --kit ./<kit> .` for composed
mixins. Run the launch command on the host from the parent directory that holds
`NAME/`. The trailing `./NAME` argument is the sandbox workspace: mount only the
generated kit directory, never your original project directory, parent
directories, or credential stores. Inside the container, the app runs from its
baked copy under `/opt/NAME/app`.

Keep the output directory named after the descriptor stem (`NAME/NAME.yaml` and
`NAME/NAME.dockerfile`), matching the layout expected by the kit authoring
guide.

## Order of host steps

1. `sbx run --detach shell --kit ./NAME --name NAME ./NAME` (on the host)
   creates the sandbox and prints its ID. Docker Sandboxes reads the local kit
   directory and applies its network and credential requests. Read
   `PERMISSIONS.md` and check your host or organization defaults before
   accepting any approval prompt: adding an allow request does not make the
   composed sandbox policy exclusive (other grants can widen access, while
   explicit denies win).
2. `sbx secret set SERVICE --sandbox NAME` (on the host) binds the app's runtime
   provider key to that sandbox. Run it after step 1 so the `--sandbox` target
   already exists. `sbx` prompts interactively for the key; avoid `--token`,
   which `sbx` itself warns is less secure because it lands in shell history.
   `--ref` (1Password or AWS Secrets Manager) and `--command` store a secret
   reference instead of a literal value; keep `--sandbox NAME` on those
   alternatives too. Keep in mind that this is the app's
   runtime provider key, independent of your coding agent's model or account.
   Apps with an offline or `--fake-model` mode can run before step 2 because
   they need no secret.
3. `sbx run --name NAME` (on the host) attaches an interactive shell inside the
   sandbox guest. Change into `/opt/NAME/app`, then run the exact
   `/opt/NAME/venv/bin/python ...` command in `RUN.md`; do not assume the shell
   starts in the app directory or use plain `python`. The kit's credential entry exposes a placeholder
   in the app's environment variable (for example `GOOGLE_API_KEY`), and the
   proxy rewrites the outbound header with the real key only for requests to the
   allowed provider host.
4. `sbx rm NAME` (on the host) removes the sandbox when you are done. Review any
   remaining sandbox-scoped secrets and `sbx policy ls` rules afterwards.

## Checking the boundary

Seeing an allowed LLM provider request succeed does not prove that everything
else is blocked. To check the boundary, try a deliberately denied but resolvable
destination from inside the sandbox, then confirm a matching denial in
`sbx policy log NAME`, run on the host. First confirm the same destination
resolves and responds normally from the host; then compare that with the guest
request and logged denial. DNS, TLS or timeout failures alone do not prove a
sandbox-policy block. Also verify inside the
sandbox that `.env` and private files are absent, without printing secret
values. Keep test layers separate: `docker buildx`, `kit-tck`, and plain
container runs do not count as sandbox runtime policy evidence.

## Cloud (optional)

`sbx --cloud run` accepts a kit reference and has no host workspace path, so
use `sbx --cloud run --detach shell --kit ./NAME --name NAME`. Baking a mixin
with build content creates a fresh cloud sandbox and uploads the kit's content,
including `app/`, to Docker's cloud. Cloud sandboxes need their own secrets,
network approvals, and allow/deny verification because local secrets and local
policy rules do not carry over. Check `sbx --cloud --help` for the verbs your
CLI supports. Cloud sandboxes are optional, unrun unless you execute and
verify them yourself, and are not a production serving deployment (lifecycle,
ingress, scaling, retention, audit, and cost remain your application's
responsibility).

## Publishing (optional)

A kit is an OCI artifact. The kit-v3 guide publishes both platforms in one
invocation from the same build that produced the verified kit (run on the host
from inside `NAME/`):

```bash
docker buildx build . -f NAME.yaml --platform linux/amd64,linux/arm64 --push \
  -t docker.io/ORG/NAME:0.1.0 -t docker.io/ORG/NAME:latest
```

Current `sbx kit --help` also lists `pack`, `push`, `sign`, and `verify`; check
their `--help` output before using them. Once published, others run
`sbx run shell --kit ORG/NAME:0.1.0`. Publishing is optional and unrun unless
you perform it, and it distributes both the app snapshot and its access
requests, so review your data, licensing, and repository visibility first.

## Pre-checks without a sandbox

Run these checks on the host from inside the generated `NAME/` kit directory,
with Docker Buildx and `kit-tck` from the `docker/sandbox-kit-spec` repository
installed:

```bash
docker buildx build . -f NAME.yaml --output type=cacheonly
docker buildx build . -f NAME.yaml -t NAME:0.1.0 --output type=oci,dest=/tmp/NAME-layout,tar=false
kit-tck validate --layout /tmp/NAME-layout 0.1.0
```

The `-t NAME:0.1.0` tag sets the OCI layout's reference name; `kit-tck` looks up
its `0.1.0` argument against that reference and fails with `not found` if the
tag is omitted.

Authoritative specification: `github.com/docker/sandbox-kit-spec` at the pin in
[capabilities](capabilities.md). Docker docs: `docs.docker.com/ai/sandboxes/`.
