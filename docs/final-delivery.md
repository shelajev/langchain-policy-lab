# Resumed delivery and independent QC handoff

Historical policy-lab delivery record. For the current existing-app workflow,
see the [README](../README.md), [article](run-your-langchain-in-docker-sandboxes.md)
and [current evidence matrix](evidence/runtime-matrix.md). This earlier record
does not close the current local/cloud runtime acceptance or independent QC.

Date: 2026-10-09. Branch: `feat/langchain-enterprise-kit`.
Run: `000000000000000018dce9089ec47888-77dc8541234fc8cc`, round 1,
implementation handoff sequence 2.
Preserved base: `6bd01195855214624f11b565e182cc59a342eb75`.

## Delivered scope

The existing implementation supplies a pinned LangChain Kits-v3 mixin, managed
Python and locked dependencies, synthetic-policy support assistant, citations,
bounded read-only tools, credential-free deterministic evaluation, optional
approved Gemini integration, sbx environment file, local checks and authored CI.
README/user guide describe the developer journey. Marketing brief and proposed
blog outline explore positioning without production-readiness or publication
claims. The original plan, references, implementation and evidence are preserved.

Finalization retains the reviewed kit-tck/sbx definitions and matching sweep
outputs. Alias-only Dockerfile/check-script changes were discarded; they did
not fix behavior and would unnecessarily change previously verified inputs.
No code, dependency, descriptor, workflow or execution command changed.

## Evidence and delta checks

`evidence/finalization-delta-check.txt` records resumed hash/input association,
shell syntax, reader-packet matching, scanner reproduction and staged credential
checks. `evidence/clean-checkout-base.txt` preserves the interrupted run's real
successful committed-checkout output, naming the full base tip. The executable
inputs remain identical to that version; this is not claimed as a fresh run.
Prior 49 tests, 11-case evaluation, source build, OCI export, 19/19 kit-tck and
Debian arm64 filesystem probe remain the evidence for their recorded versions.

Final editorial state: review 07 READABLE; final scanner outputs match the
reviewed README/guide. Contextual hits are retained with dispositions, not
misrepresented as a clean sweep. Optional PATH consistency clarification is
not implemented: both example commands already use the same directory.
No further model review or public-prose polishing was warranted.

## Actual resumed role references

Authoritative pins come from `/home/agent/crew/models`, corroborated by selected
session metadata/model identifiers and the current crew status. Only identifiers
are copied; no credentials, prompt bodies or raw session transcripts are stored.

| Role | Pinned model | Actual session reference |
| --- | --- | --- |
| Planner (pi) | `google/gemini-3.8-flash` | `2026-10-09T16-23-18-559Z_01a12179-e31e-75eb-bb22-fbcbb2ab2fa9.jsonl` |
| Implementer (codex) | `gpt-6.1-sol` | `rollout-2026-10-09T16-23-45-01a1217a-4e34-79a0-afbc-08e6e1dbfb59.jsonl` |
| Independent QC (claude) | `claude-opus-5-5` | `c7e7d572-b963-46ab-90e0-f38349a0980c.jsonl` |

The current implementation handoff names terminal `term_65d6ac4adcde2e`;
the settled planner handoff names `term_65d6ac3fc46bbd`. These are observed
current-run ledger references, not guessed replacements or editorial models.
Existence/model association is not evidence that independent QC has passed.

## Unrun checks and final boundary

Actual assembled SBX composition, merged PATH/workload behavior and policy
enforcement remain optional HUMAN checks with an already provisioned daemon.
Hosted GitHub Actions have not run. Live sample-provider validation has not run.
None is an acceptance blocker for this deliverable or silently called a pass.
No host execution, daemon startup, publication, push, new credentials, hook
permission, infrastructure/resource modification or local main integration
occurred during resumed finalization. Host owns any eventual main integration.

Independent Claude QC is pending. The exact clean delivery tip is reported in
the commit-stage crew status and implementer handoff, not self-embedded here.
The implementer stops editing after committing. If independent QC evidence is
not yet durable, only a subsequent authorized revise round may preserve its
sanitized report and must obtain fresh QC of that new exact tip. No `qc.json`
or self-declared QC verdict is written by the implementer.

## Subsequent initial QC and evidence-preservation revision

The pending status above records the original pre-QC handoff. Independent
Claude subsequently reported round-1 PASS at exact commit
`3540a424f7d6c3db4e6b967d025f0fb8016aec38`, with fresh observed checks.
`qc-delivery-report.md` and `reviews/claude-qc-round-01.md` preserve that result,
actual provenance and the recovered confirmation-only attempt. This authorized
round-2 revision changes evidence only. Fresh independent QC of the new exact
tip remains pending; the initial PASS is not claimed for the evidence commit.
