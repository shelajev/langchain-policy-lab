# Marketing brief: a policy-assistant lab for platform teams

## Audience and problem

An SBX product manager can use the [product overview](product-overview.md) to
assess the kit's developer value, then use this brief to explain the evidence
and limits. SBX means Docker Sandboxes and its runtime tooling. A LangChain
developer should start with the [README quickstart](../README.md#quickstart-without-a-paid-credential)
and [developer guide](user-guide.md) for the runnable journey.

An AI platform engineer needs a small, inspectable workflow before approving a
support assistant that handles internal policy documents. A useful first demo
should expose retrieval, citations and tool boundaries without requiring a
paid model account or real employee data.

This independent lab packages that exercise as a Docker Sandboxes v3 mixin.
Teams can add the pinned LangChain/Python runtime to an existing workload, keeping
its operating system and agent. [langchain.yaml](../langchain.yaml) declares the
mixin; [langchain.dockerfile](../langchain.dockerfile) builds its file overlay;
[langchain-context.md](../langchain-context.md) supplies coding-agent guidance.
The [sample project](../sample/) contains the assistant and checks, while
[sample/sbxenv.yaml](../sample/sbxenv.yaml) declares the pinned workload, local
mixin and workspace for the optional runtime path.

The developer first runs deterministic policy QA with citations and explicit,
bounded tools. Four synthetic Markdown policies make the initial
questions and expected answers shareable. The meal tool returns 270 USD for
a three-day Tier 1 trip; the receipt tool distinguishes 24.99 from 25 USD.

## What the evidence supports

Local Linux arm64 checks passed 49 behavioral tests, an 11-case deterministic
evaluation, source build, OCI export and 19/19 kit-tck artifact checks. A
filesystem-only probe ran the bundled interpreter on Debian 12 without system
Python, as a non-root user, with network disabled and a read-only root filesystem.
The dependency lock and image digests make the installed inputs explicit.

The mixin requests only typed agent context. It adds no credential, network,
privilege or host-sharing requests. That gives a platform reviewer a small
declaration to inspect; capabilities requested by a chosen workload still
matter. Actual composed SBX execution and policy enforcement remain an unrun
human handoff.
No inference about enterprise security or compliance follows from kit-tck.

GitHub Actions is configured to build and verify on a real Ubuntu runner,
including fresh-checkout testing. Its
[first hosted run, 37961247968](https://github.com/shelajev/langchain-policy-lab/actions/runs/37961247968)
passed. Live Gemini sample validation remains an unrun human handoff: the
extractive fake checks plumbing, while the
Gemini provider is a separately approved, potentially billable path.

## Positioning and limits

Describe it as a reproducible learning lab for policy retrieval and bounded
tools. Avoid "production-ready," "secure by default," "universal portability,"
or a claim that fake answers establish model quality. The evidenced runtime
target is Linux arm64 on Debian/glibc; hosted checks passed on Ubuntu x86-64.
Other workloads require compatibility
checks. This repository has no customer deployment evidence.

The next evaluation should test policy access control, prompt injection,
retrieval quality and citation entailment using approved data. A team adopting
it owns those decisions and its runtime policies. Review the
[verification evidence](verification-report.md) before proposing a runtime demo.

No personal or corporate author identity has been selected. This is a factual
explainer, not a Docker corporate announcement or an account of an author's
customer experience. The repository has been shared privately on GitHub; no kit image or corporate announcement has been published.
