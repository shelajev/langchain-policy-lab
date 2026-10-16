# Specification currency: 2026-10-16

Read-only checks in the implementation sandbox:

```text
git ls-remote https://github.com/docker/sandbox-kit-spec.git HEAD
e223cd4c52be3407ffecb5208777289c07583360 HEAD
```

Cloned that HEAD into scratch and fetched the existing pin
`a1d110de252bcc3cb2fa6d47fe37137a1a328b97`. Compared both normative
`docs/spec/capabilities/com.docker.sandbox/network-policy@1.md` and
`credential@1.md`: no diff. Read current `skills/create-kit-v3/SKILL.md` and
SPEC-v3 sections 3.4 and 5.3. Sources:

- https://github.com/docker/sandbox-kit-spec
- https://docs.docker.com/reference/cli/sbx/env/
- https://docs.docker.com/reference/cli/sbx/env/exec/
- https://docs.docker.com/ai/sandboxes/configuration/environment-files/
- https://docs.docker.com/ai/sandboxes/cloud/usage/
- https://api.github.com/repos/docker/sbx-releases/releases/latest

Decision: retain the existing frontend, workload, uv base and TCK pins. Use
`network-policy@1`, because this workflow requests host-level access. @2 also
exists but is mutually exclusive and requires runtime-specific verification of
method/path bounds. This work makes no @2 enforcement claim.
`credential@1`: service + runtime phase; optional apiKey with name,
proxyManaged and inject domain/header/format. The injection domain must be
explicitly allowed. Host environment names alone do not provision a binding.

The app overlay is always a mixin, with no `sbx@1` or lifecycle. Workload owns
identity and launch. Context uses contentFile. The shell workload is selected
by its reference-derived handle `sbx-kit-shell`, alongside the mixin.

`command -v sbx`: absent. **Current executable help NOT RUN**: no installed CLI;
no daemon or global install was attempted. Previous `sbx-help.txt` is v0.47.0
historical evidence, not a fresh run. The official latest release API reports
v0.48.0, published 2026-10-13T12:29:44Z. No release binary was executed in this
round. Current CLI docs establish these forms (not observed runtime output):

```text
sbx env plan ./sbxenv.local.yaml
sbx env run --detach ./sbxenv.local.yaml
sbx env exec ./sbxenv.local.yaml -- COMMAND ARG...
sbx --cloud env plan ./sbxenv.cloud.yaml
sbx --cloud env run --detach ./sbxenv.cloud.yaml
sbx --cloud env exec ./sbxenv.cloud.yaml -- COMMAND ARG...
```

Current environment docs support local source kits in cloud baking, require
no workspace/additionalWorkspaces/clone mounts in cloud, separate cloud secrets
and explicit injection-domain approvals, and same target/account/files for
subsequent commands. Host must verify help and target capability support before
executing the [acceptance handoff](../acceptance-handoff.md). No cloud baking or
upload was performed here.
