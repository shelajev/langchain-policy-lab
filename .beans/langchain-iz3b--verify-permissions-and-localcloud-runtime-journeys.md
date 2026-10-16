---
# langchain-iz3b
title: Verify permissions and local/cloud runtime journeys
status: in-progress
type: task
created_at: 2026-10-15T21:58:07Z
updated_at: 2026-10-16T09:43:44Z
parent: langchain-oqr4
---

Verify generated artifacts and application behavior; exercise intended access and denied access where runtime is available. Use existing approved routes only. Distinguish build/TCK, container probes, local SBX, cloud SBX and live provider evidence. No daemon bridge, host execution of crew code, new credentials, nested virtualization or infrastructure repair. Preserve executable handoff for unavailable checks; report required acceptance gaps honestly.

## Evidence

- [Separated runtime matrix](../docs/evidence/runtime-matrix.md), [exact host handoff](../docs/acceptance-handoff.md).
- PASS: source/build, artifact TCK and network-none ordinary container; not runtime-confinement proof.
- PASS: [one explicitly authorized live app call](../docs/evidence/live-model.txt), existing implementation sandbox route, one synthetic ticket, pinned model/timeout/output; not new local/cloud SBX acceptance.
- [ ] Actual local SBX composition, proxy credential injection and allowed/denied boundary events: NOT RUN, sbx absent; host H1.
- [ ] Actual cloud SBX: NOT RUN. The host reports `sbx --cloud diagnose` passed authentication, API reachability and subscription; host cloud account/API reachable, not crew-observed. Cloud-side secret/binding, baking/upload approval and actual allowed/denied events remain open; H2.
- [ ] Current executable sbx help and target-specific policy/composition support: host verification remains required.

- Direct-first delta: [official shell/tooling inspection](../docs/evidence/direct-first-tooling.md), [raw source/container probe](../docs/evidence/direct-first-container.txt) and [manual snapshot container check](../docs/evidence/direct-first-manual.txt) PASS in their separate classes. No source executed on host.
- [ ] H1 direct variant in the [host handoff](../docs/acceptance-handoff.md): actual local SBX setup, google proxy injection, allowed call, policy-denied event/origin control and cleanup remain NOT RUN. Shell binding prompt is UNVERIFIED until host review.
- [ ] H2 remains NOT RUN: host-reported diagnose PASS is preserved; separate cloud-side secret/binding, transfer/baking approval and actual runtime checks remain required. No live application model call repeated.
