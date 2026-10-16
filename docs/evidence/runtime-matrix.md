# Runtime evidence matrix, 2026-10-16

| Class | Status and evidence | Exact check / host handoff |
| --- | --- | --- |
| Source/build | PASS: [baseline](baseline-2026-10-16/), [example](example-tests.txt), [helper](skill-tests.txt), [generated build](generated-kit-build.txt) | `bash scripts/check-example.sh`; `bash scripts/check-skill.sh`; `bash scripts/check-generated-kit.sh <fresh-layout>` |
| TCK | PASS: [generated TCK](generated-kit-tck.txt), pinned dev a1d110de | `kit-tck validate --verbose --layout <generated-layout> 0.1.0` |
| Container probe | PASS: [ordinary container](generated-kit-container.txt), no network, read-only, uid 1000 | `bash scripts/check-generated-container.sh` after generated-kit build |
| Actual local SBX | **NOT RUN**: sbx absent; no nested daemon/virtualization/socket bridge authorized | [H1 exact commands](../acceptance-handoff.md), starting `sbx env plan ./examples/ticket-triage-kit/sbxenv.local.yaml` |
| Actual cloud SBX | **NOT RUN**: the host reports `sbx --cloud diagnose` passed authentication, API reachability and subscription; the crew did not observe it. Cloud-side secret/binding, baking/upload approval and actual allowed/denied runs remain open | [H2 exact commands](../acceptance-handoff.md), starting `sbx --cloud env plan ./examples/ticket-triage-kit/sbxenv.cloud.yaml` |
| Live model | **PASS**: [one approved live call](live-model.txt) in the implementation sandbox, one synthetic ticket, gemini-2.5-flash, 60s timeout, max_tokens 256; **not local/cloud SBX acceptance** | `TRIAGE_MODEL=gemini-2.5-flash LANGSMITH_TRACING=false uv run --locked --offline python -m ticket_triage.app --ticket data/tickets/t-101.json` from examples/ticket-triage |

Build/TCK/container success is **not runtime confinement proof**. The frontend
accepted the v3 mixin and TCK checked its artifact; the Debian overlay probe ran
the fake app and exercised network-none failure. Actual shell-workload
composition, allowed Gemini injection, local/cloud effective policy and denied
boundary events remain unverified until H1/H2. No production deployment claim.

The baseline was run before implementation at aeac822, including sample tests,
kit build/TCK and filesystem probe. Each log records command, UTC and exit.
The helper's golden comparison covers the exact sanitized snapshot and hashes.

Prior [clean-checkout run](clean-checkout-2026-10-16.txt) PASS at implementation
commit 95796f18f8344940986617ff896a337da27190b1: 49 policy-lab tests, 4 ticket-triage
tests, 22 helper tests, 80 current relative links, both kit builds/TCK, both
ordinary container probes and root agent.py build/run. It used an isolated uv
cache/managed Python and ended with a clean cloned tree. That result describes
the prior commit, not the later raw-input and single-file-template changes.
Exact final-commit independent QC is still the next phase.

Round 2 adds [raw requirements to reviewed lock/build](raw-single-file.txt),
the committed single-file kit's separate [build](single-file-kit-build.txt),
[TCK 19/19](single-file-kit-tck.txt) and [container](single-file-kit-container.txt)
results, plus the [hand-edited manual forward test](manual-path-forward.md).
These are source/build/TCK/ordinary-container evidence only; local and cloud
SBX remain NOT RUN. The already approved live app test was not repeated.

CI workflow additions are preserved as a
[round-2 reviewable patch](ci-workflow-round2.patch) and under the crew handoff path;
`.github/workflows/ci.yml` itself is unchanged to respect host token scope.
The existing CI clean-checkout step will run the extended check script; no new
hosted CI run was started or claimed here.
