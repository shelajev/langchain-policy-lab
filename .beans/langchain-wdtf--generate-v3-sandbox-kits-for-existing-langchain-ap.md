---
# langchain-wdtf
title: Generate v3 sandbox kits for existing LangChain applications
status: completed
type: task
created_at: 2026-10-15T21:58:07Z
updated_at: 2026-10-16T08:50:00Z
parent: langchain-oqr4
---

Create a reusable project-distributed skill and deterministic generator. Accept entrypoint/project dependencies; inspect without executing source; ask about unresolved capabilities; generate descriptor, recipe, environment and permission explanation. Pin inputs; prevent secret inclusion and unsafe overwrite; keep launch semantics correct. Meaningful baseline, generated artifact and adverse-input tests. Independent forward use by QC.

## Evidence

- [Skill and contract](../skills/langchain-sandbox-kit/SKILL.md): root agent.py and packaged src apps, no source execution, explicit answers, sanitized context and guarded overwrite.
- [Baseline](../docs/evidence/baseline-2026-10-16/), [helper tests](../docs/evidence/skill-tests.txt), [app tests](../docs/evidence/example-tests.txt).
- [Generated build](../docs/evidence/generated-kit-build.txt), [artifact TCK](../docs/evidence/generated-kit-tck.txt), [ordinary container](../docs/evidence/generated-kit-container.txt), [single-file build/run](../docs/evidence/single-file.txt).
- [Implementer forward smoke](../docs/evidence/skill-forward-smoke.md), not independent QC. Independent forward use remains the delivery/QC bean's acceptance requirement.
- [Golden package](../examples/ticket-triage-kit/) and [current spec decisions](../docs/evidence/spec-currency.md).
