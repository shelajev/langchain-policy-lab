# Proposed blog outline

Working angle: **Follow a policy answer from a Markdown section to its citation**.
Audience: Python developers and AI platform engineers evaluating internal
support assistants. This proposes a post; it is not an approved new-blog draft.
For the existing product story, read the [product overview](product-overview.md)
and [marketing brief](marketing-brief.md). The [README quickstart](../README.md#quickstart-without-a-paid-credential)
and [developer guide](user-guide.md) provide the runnable journey.

1. Open with the Tier 1 meal question and its synthetic `$90` passage. Show the
   source, section and chunk ID before discussing an LLM.
2. Trace ingestion and lexical retrieval into the LangChain prompt/model/parser
   pipeline. Explain why the offline extractive fake is useful and what it
   cannot validate.
3. Run the three-day meal tool and the receipt boundary at `$25`. Explain the
   strict input limits and explicit, read-only invocation.
4. Ask an unsupported pet question and inspect its empty citations. Show how
   malformed model output and invalid IDs fail rather than return a guess.
5. Package the exercise as a v3 mixin with its own interpreter. Use the observed
   source build, OCI export, kit-tck and Debian filesystem probe as distinct
   evidence; explain the remaining glibc and composition constraints.
   Distinguish the descriptor (`langchain.yaml`), file-overlay recipe
   (`langchain.dockerfile`) and agent guidance (`langchain-context.md`) from the
   policy-QA project in `sample/`. Explain how `sample/sbxenv.yaml` declares the
   pinned shell workload, local mixin and repository workspace. The mixin's
   agent-context request grants no model access, credentials or extra mounts.
6. Close with the decisions a platform team still owns: approved data and
   provider access, runtime policy tests, access control and realistic evaluation.

Use the repository's [guide](user-guide.md) and [verification report](verification-report.md)
as reader-visible supporting evidence. Do not invent a customer story, personal
failure anecdote or deployment results.
[Hosted workflow run 37961247968](https://github.com/shelajev/langchain-policy-lab/actions/runs/37961247968)
passed; that is execution evidence, separate from the workflow definition.
Actual composed SBX execution and live Gemini sample validation remain unrun
human handoffs. The credential-free deterministic journey does not establish
live-model quality or runtime policy enforcement.

## Pending author gates

- Select and approve a personal and/or explicitly chosen corporate identity.
- Agree on the post's angle and outline with that author.
- Run the pinned blog-writer package's full new-blog workflow, including its
  identity/voice evidence gates, if a finished post is requested.
- Approve publication destination and any product/security claims separately.

These optional gates do not block the kit, sample or neutral guide. No post or
kit image has been published. The repository has been shared privately on GitHub.
