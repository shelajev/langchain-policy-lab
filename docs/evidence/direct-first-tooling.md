# Direct-first tooling verification

Fetched 2026-10-16 UTC. Documentation verification is not runtime execution.
Local and cloud SBX remain **NOT RUN**. No daemon, login or sbx installation
was attempted. Optional v0.48.0 scratch binary inspection was not needed;
the command syntax below was read in current official documentation.

## Official sources read

- https://docs.docker.com/ai/sandboxes/get-started/
- https://docs.docker.com/ai/sandboxes/agents/
- https://docs.docker.com/reference/cli/sbx/run/
- https://docs.docker.com/reference/cli/sbx/create/
- https://docs.docker.com/reference/cli/sbx/exec/
- https://docs.docker.com/reference/cli/sbx/env/
- https://docs.docker.com/reference/cli/sbx/env/exec/
- https://docs.docker.com/ai/sandboxes/configuration/environment-files
- https://docs.docker.com/reference/cli/sbx/policy/allow/network/
- https://docs.docker.com/reference/cli/sbx/policy/deny/network/
- https://docs.docker.com/reference/cli/sbx/policy/rm/network/
- https://docs.docker.com/reference/cli/sbx/secret/set/
- https://docs.docker.com/ai/sandboxes/configuration/credentials
- https://docs.docker.com/ai/sandboxes/security/defaults/

The environment-file URL ending in `/index.md` returned 404; the canonical
HTML page above was read instead. No 403 was encountered.

## 1. Workload and dependency setup

`sbx run` lists `shell` among available agents. Environment-file documentation
says: “set `agent` to the workload's name” when using v3. Use the existing
published `docker/sbx-kit-shell:1.0.0` workload, pinned at
`sha256:367c9a4b3fd550f777e1d57cc53550afb4a1385055d79111acf6f996272ff6de`.
No generated mixin or hypothetical Python kit is needed.

Read-only registry inspection, pull and an ordinary `--network none` container
probe are recorded in [shell-image.txt](shell-image.txt). `/usr/bin/python3`
exists; `uv`, `git` and `curl` were not found. OS is Docker Hardened Images,
Debian 13 trixie. This is **container evidence**, not an SBX run.

Install uv 0.9.26 into `$HOME/.local/bin` **inside the sandbox**, from the official
GitHub release archive, checking its SHA-256 before extracting only `uv`.
The bundled `direct-setup.txt` uses Python's standard library, so it does not
require curl or git. Checksums match the existing reviewed CI installer:
x86_64 `30ccbf0a66dc8727a02b0e245c583ee970bdafecf3a443c1686e1b30ec4939e8`;
aarch64 `f71040c59798f79c44c08a7a1c1af7de95a8d334ea924b47b67ad6b9632be270`.
Then `uv sync --locked` installs the project's pinned interpreter and dependencies.
Source is never run on the host. SBX bootstrap itself is **NOT RUN** here.

## 2. Network and credentials without a mixin

No network key is documented in the environment-file field reference. Do not
invent one. Use sandbox-scoped host commands after creating the environment:

```bash
sbx policy allow network --sandbox single-file generativelanguage.googleapis.com
sbx policy deny network --sandbox single-file example.com
sbx policy ls
sbx secret set google --sandbox single-file
```

The policy reference verifies `--sandbox` for allow, deny and removal. Deny wins
over allow. Inspect inherited local/org rules: an allow list is not an exclusive
policy if broader inherited grants exist. Do not change global defaults.
Temporarily allow bootstrap hosts `github.com`, `release-assets.githubusercontent.com`,
`pypi.org`, `files.pythonhosted.org`; remove those scoped rules after setup with
`sbx policy rm network --sandbox single-file --resource HOST`.

The built-in credential service is **google**, not the optional kit's **gemini**
service. Credentials docs map google to `GOOGLE_API_KEY`/`GEMINI_API_KEY` and
`generativelanguage.googleapis.com`. A shell/custom-template client can use a
`proxy-managed` placeholder; the proxy injects the real header. The Google
API-key header is `x-goog-api-key`. The generated direct environment sets the
placeholder only, never a real key. Store an existing approved key interactively
on the host before creation. Do not obtain a new credential for this task.

Environment `bindings.SERVICE.apiKey.domains` is documented, but modifies global
binding approvals; no new binding is generated for the built-in google route.
Whether a particular host's shell composition needs additional binding approval
is **UNVERIFIED** until `sbx env plan` and the host runtime check. Stop on an
unapproved binding request rather than silently widening access.

## 3. Workspace limitation

Use `workspace: ./workspace` in a sibling environment directory. The docs say
relative workspace paths resolve from the environment file. No workspace exclude
field is documented. `.dockerignore` alone does not filter a bind mount.
Mount only a sanitized allowlisted snapshot, retaining original relative layout;
never mount the raw project or a parent directory. Keep environment, answers,
access report and setup script outside the mounted snapshot. Set
`sandboxOptions.skills: off` to omit the shared skills store.

`sbx env plan FILE`, `sbx env create FILE`, `sbx env run FILE`,
`sbx env exec -i FILE -- sh`, and `sbx env rm FILE` are documented. Exec's `-i`
keeps stdin open, allowing reviewed setup commands to be supplied without
mounting the control files. Cloud cannot mount this workspace: baking/copying
requires a separate approved transfer and cloud-side secrets/policy.
