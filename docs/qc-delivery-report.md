# Initial independent QC and evidence-preservation handoff

Date: 2026-10-09. Run: `000000000000000018dce9089ec47888-77dc8541234fc8cc`.
Branch: `feat/langchain-enterprise-kit`.
This report preserves completed round-1 independent QC during the authorized
round-2 evidence-only revision (implementer handoff sequence 5). It is not a
verdict on the new evidence commit or a substitute for fresh exact-tip QC.

## Exact reviewed version and independent result

Initial reviewed commit: `3540a424f7d6c3db4e6b967d025f0fb8016aec38`.
Implementation base: `6bd01195855214624f11b565e182cc59a342eb75`.
Reviewer-reported initial verdict: **PASS**, round 1, settled QC sequence 4.
The reviewer recorded identical starting/finishing commits and empty Git
porcelain before and after review. All ten recorded checks passed.

`reviews/claude-qc-round-01.md` is the complete, byte-identical reviewer report
from `/home/agent/crew/qc-log.md`. Its sanitized contents include commands,
outcomes, provenance and the recovered attempt; no credentials or session
transcripts are included. Source SHA-256:
`ef6fbcc6d0430c386d6180adac1895f9a3ae5c7ebee2deac7f149b068bc1d2ad`.
The separately read, reviewer-written round-1 `/home/agent/crew/qc.json` had
SHA-256 `f771e6b1bcf5bcbd15f95140529dbe50fc023335411c817c276ee37532665af0`.
It was not modified or recreated. Its run/round/commit/verdict/check outcomes
were cross-checked against the report and settled handoff ledger.

## Actual reviewer and session provenance

The authoritative `/home/agent/crew/models` pin is `claude=claude-opus-5-5`.
The initial reviewer was Claude, session
`c7e7d572-b963-46ab-90e0-f38349a0980c.jsonl`, terminal
`term_65d6ac58269d2f`. The report identifies that session; the handoff ledger
records the same terminal for both the superseded sequence 3 and settled
sequence 4. Available session model identifiers corroborate the model pin.
No session reference was guessed, and no raw transcript was copied.

The sole implementer remains Codex, pinned `gpt-6.1-sol`, session
`rollout-2026-10-09T16-23-45-01a1217a-4e34-79a0-afbc-08e6e1dbfb59.jsonl`,
terminal `term_65d6ac4adcde2e`; sequence 5 reuses that current-run terminal.
The preserved planner/session references remain in `final-delivery.md`.

## Observed independent checks

These are checks performed by independent QC at the initial reviewed tip,
not implementer reruns in this evidence-preservation revision:

| Check | Reviewer-observed outcome |
| --- | --- |
| Pre/post-review commit and porcelain | Same exact tip, clean tree |
| `bash scripts/clean-checkout.sh` | Exit 0; fresh clone at reviewed tip, 49 tests, 11/11 eval, expected cited/refusal/tool outputs and provider imports |
| `bash scripts/check-kit.sh <fresh layout>` | Exit 0; source build, OCI export, kit-tck 19/19, docker-container BuildKit v0.29.0 |
| `bash scripts/check-filesystem.sh` | Exit 0; Debian overlay, Python 3.13.7, uid 1000, read-only, network none, no system Python, 11-case eval |
| Guide failure/boundary commands | Invalid days and missing policies each fail safely with exit 1; receipt 24.99 is false; threshold query is grounded at $25 |
| ACR realization | Version 0.2.1, realization current, exact package pin confirmed |
| Reader packet | Digest matches; all four final public drafts contained verbatim; review 07 READABLE |
| Credential patterns | No recognized token/private-key matches at reviewed HEAD; no secrets read or printed by QC |
| CI no-silent-skip audit | Real hosted runner and pinned inputs; no conditional skips, continue-on-error or ignored failures |

The fresh OCI manifest digest was
`sha256:4893ecd98119e62d04f204cf17bdea32b61d83232fb0e4abdecae45709252322`,
matching the committed delivery index. The fresh initial-tip clean checkout is
distinct from the older recovered base log in `evidence/clean-checkout-base.txt`.

## Recovered attempt and retained observation

QC sequence 3 produced only a confirmation request, no review and no evidence:
the pasted handoff was interpreted against a stale session-start dirty snapshot.
The same review phase was retried as sequence 4, which checked the actual clean
commit and produced the independent PASS. This was a recovered non-review
attempt, not a failed acceptance test or an erased prior QC verdict.

The reviewer retained a non-blocking citation-precision observation: some older
verification-report citations/digest belong to an earlier recipe without
`--no-bin`. Current-recipe evidence is `evidence/kit-delivery.txt` and
`evidence/filesystem-delivery.txt`, with the digest independently reproduced
above. The original report already scopes results to recorded versions; fresh
QC passed. No repair was requested and no optional documentation polish was
performed in this evidence-only round.

## Evidence revision checks and final boundary

Preservation checks compare the repository report byte-for-byte with the
completed crew QC log, verify its source hash, confirm crew qc.json is unchanged,
and verify staged changes are confined to delivery/QC documentation. Whitespace
and staged credential-pattern/literal scans are also checked. No implementation
or learner-facing prose changed; no build, sample or editorial review was repeated.

Observed revision results: all preservation/scope checks passed; exactly three
delivery/QC documentation paths changed. The staged credential scan covered
132 tracked files and one non-placeholder environment value with no matches
or values printed. `git diff --cached --check` and all seven preserved
`evidence/finalization-hashes.sha256` entries passed. The executable and four
public-draft diff against the initial reviewed tip was empty.

SBX composition/policy enforcement, hosted Actions and live sample-provider
validation remain unrun HUMAN handoffs, not inferred passes or blockers.
No host/SBX execution, hooks, daemon startup, publication, push, new credentials,
infrastructure/resource changes or main integration occurred in this revision.

Fresh independent Claude QC of the forthcoming evidence commit is **pending**.
The commit-stage crew status/handoff records its full clean tip. The reviewer
will write final qc.json outside the repository; this historical report does
not embed or predict that verdict. The implementer stops editing after the
evidence commit, avoiding a circular final-verdict report commit.
