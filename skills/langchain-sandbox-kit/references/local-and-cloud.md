# Run from the generated kit directory

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
`sbx --cloud --help` and target credential support first, then have the host
use its existing login, cloud-side secret and explicit service/domain binding.
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
