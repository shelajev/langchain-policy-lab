---
# langchain-iz3b
title: Verify permissions and local/cloud runtime journeys
status: in-progress
type: task
created_at: 2026-10-15T21:58:07Z
updated_at: 2026-10-16T09:06:11Z
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
