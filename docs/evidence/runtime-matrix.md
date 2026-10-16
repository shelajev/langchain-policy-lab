# Runtime evidence matrix, 2026-10-16

| Class | Status and evidence | Exact check / host handoff |
| --- | --- | --- |
| Source/build | PASS: [baseline](baseline-2026-10-16/), [example](example-tests.txt), [helper](skill-tests.txt), [generated build](generated-kit-build.txt) | `bash scripts/check-example.sh`; `bash scripts/check-skill.sh`; `bash scripts/check-generated-kit.sh <fresh-layout>` |
| TCK | PASS: [generated TCK](generated-kit-tck.txt), pinned dev a1d110de | `kit-tck validate --verbose --layout <generated-layout> 0.1.0` |
| Container probe | PASS: [ordinary container](generated-kit-container.txt), no network, read-only, uid 1000 | `bash scripts/check-generated-container.sh` after generated-kit build |
| Actual local SBX | **NOT RUN**: sbx absent; no nested daemon/virtualization/socket bridge authorized | [H1 exact commands](../acceptance-handoff.md), starting `sbx env plan ./examples/ticket-triage-kit/sbxenv.local.yaml` |
| Actual cloud SBX | **NOT RUN**: no CLI/login/target or approved cloud-side secret/binding; no upload authorized | [H2 exact commands](../acceptance-handoff.md), starting `sbx --cloud env plan ./examples/ticket-triage-kit/sbxenv.cloud.yaml` |
| Live model | **PASS**: [one approved live call](live-model.txt) in the implementation sandbox, one synthetic ticket, gemini-2.5-flash, 60s timeout, max_tokens 256; **not local/cloud SBX acceptance** | `TRIAGE_MODEL=gemini-2.5-flash LANGSMITH_TRACING=false uv run --locked --offline python -m ticket_triage.app --ticket data/tickets/t-101.json` from examples/ticket-triage |

Build/TCK/container success is **not runtime confinement proof**. The frontend
accepted the v3 mixin and TCK checked its artifact; the Debian overlay probe ran
the fake app and exercised network-none failure. Actual shell-workload
composition, allowed Gemini injection, local/cloud effective policy and denied
boundary events remain unverified until H1/H2. No production deployment claim.

The baseline was run before implementation at aeac822, including sample tests,
kit build/TCK and filesystem probe. Each log records command, UTC and exit.
The helper's golden comparison covers the exact sanitized snapshot and hashes.
