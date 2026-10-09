# Marketing brief: a policy-assistant lab for platform teams

## Audience and problem

An AI platform engineer needs a small, inspectable workflow before approving a
support assistant that handles internal policy documents. A useful first demo
should expose retrieval, citations and tool boundaries without requiring a
paid model account or real employee data.

This kit packages that exercise as a Docker Sandboxes v3 mixin. Teams can add
the pinned LangChain/Python runtime to an existing workload rather than replace
the agent environment. Four synthetic Markdown policies make the initial
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
matter. Actual SBX composition and policy enforcement remain a HUMAN check.
No inference about enterprise security or compliance follows from kit-tck.

GitHub Actions is configured to build and verify on a real Ubuntu runner,
including fresh-checkout testing. Its first hosted run passed. Live model
validation is also pending: the extractive fake checks plumbing, while the
Gemini provider is a separately approved, potentially billable path.

## Positioning and limits

Describe it as a reproducible learning lab for policy retrieval and bounded
tools. Avoid "production-ready," "secure by default," "universal portability,"
or a claim that fake answers establish model quality. The evidenced runtime
target is Linux arm64 on Debian/glibc; other workloads require compatibility
checks. This repository has no customer deployment evidence.

The next evaluation should test policy access control, prompt injection,
retrieval quality and citation entailment using approved data. A team adopting
it owns those decisions and its runtime policies. Start with the
[guide](user-guide.md), then review the [verification evidence](verification-report.md).

No personal or corporate author identity has been selected. This is a factual
explainer, not a Docker corporate announcement or an account of an author's
customer experience. The repository has been shared privately on GitHub; no kit image or corporate announcement has been published.
