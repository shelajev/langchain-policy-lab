# Existing LangChain app to a reviewed sandbox kit

The primary workflow is inspect → developer decisions → generate → build/check
→ run locally → adapt for cloud → verify allowed and denied operations. This
repository ships an agent skill, static helper and normal ticket-triage app.
Manual and assisted paths share the same v3 mixin and environment files.

Private files are excluded from a separate context. Capabilities have reasons
and evidence; unknown resources need answers and no access is auto-granted.
The workload owns launch; `sbx env exec` runs the app inside it. Cloud uses baked
files, no host mount and separate secrets/policy. Allowed services still have
side effects; isolation does not solve prompt injection or answer correctness.

Build/TCK/offline container checks and one separately approved live app call in
the implementation sandbox pass. Actual local/cloud SBX remain NOT RUN:
[matrix](evidence/runtime-matrix.md). No production serving
claim is made. Start with the [guide](user-guide.md) or
[article](run-your-langchain-in-docker-sandboxes.md). The
[policy lab](policy-lab-guide.md) remains a supporting fixture.
