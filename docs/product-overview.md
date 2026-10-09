# A LangChain developer journey with Docker Sandboxes kits

An enterprise developer wants to build an assistant that answers questions about
travel and expenses. Before using real company documents or connecting a paid
model, they need a small project where they can inspect the retrieved sources,
exercise tools, and check whether changes break expected behavior.

This repository provides that project and packages its development dependencies
as a Docker Sandboxes v3 kit. It lets an SBX product manager examine a concrete
example of what a framework-specific kit could offer to developers.

## The kit and the project serve different purposes

The **LangChain kit** supplies the environment: Python 3.13.7, locked LangChain
dependencies, a bundled copy of the sample, and instructions for the coding
agent. Its descriptor is [langchain.yaml](../langchain.yaml), and its build recipe
is [langchain.dockerfile](../langchain.dockerfile).

It is a **mixin kit**. A workload supplies the base operating system and agent;
the LangChain mixin adds the framework and project tools to that workload. The
developer can keep their chosen workload while adding LangChain support. This
example uses a pinned shell workload in [sample/sbxenv.yaml](../sample/sbxenv.yaml).
The recipe targets Linux with glibc; compatibility with other bases needs checking.

The **sample project** supplies the exercise: four fictional company policy
documents, a LangChain retrieval pipeline, cited answers, two expense tools, and
tests. It gives the developer something useful to build on after the environment
is available. The kit contains the sample, and the repository also exposes its
source under [sample/](../sample/) for editing and testing.

The **guide** explains the experience step by step. It starts with a local Python
run, which has been verified, then describes the separately unrun SBX composition
path. Read [the developer guide](user-guide.md) for commands and expected outputs.

## Follow the developer's first task

The developer asks, “What is the Tier 1 meal allowance?” The application reads the
synthetic policy documents, retrieves relevant sections, and returns the $90 daily
allowance with the source file, section, and chunk identifier. The developer can
open the cited document and compare the answer with the source.

Next, they calculate a three-day trip's meal allowance. A bounded LangChain tool
returns $270. Another tool checks the fictional $25 receipt threshold. These
tools calculate results from explicit inputs; they do not submit expenses or
modify a company system.

Then the developer asks a question the documents cannot answer. The example pet
question returns an unsupported result without citations. Invalid tool inputs
also fail. These cases let the developer inspect failure behavior alongside the
successful answer.

The developer runs an evaluation suite and tests before changing the project.
They can then change a policy, retrieval behavior, or tool and rerun the checks.
The default model copies retrieved text deterministically, so the exercise needs
no API key and produces repeatable outputs. It tests the LangChain pipeline and
citation handling; a real model's answer quality needs a separate evaluation.

Once provider access is approved, the guide offers an optional Gemini path.
Adapting the project to real enterprise data would also require decisions about
document access, retrieval quality, prompt injection, and runtime policy. Those
are adoption work, rather than capabilities demonstrated by this sample.

## Where SBX fits into that journey

The intended sandbox path is to combine the shell workload and LangChain mixin
using `sample/sbxenv.yaml`, mount the project workspace, and work on the sample
inside that environment. The kit supplies the pinned Python environment instead
of requiring the developer to assemble it inside each workload.

The mixin requests only agent context: packaged guidance for the agent. It does
not itself request network access, credentials, privilege, or extra host mounts.
The selected workload and runtime policies still determine the complete sandbox's
access. The sample's local Python quickstart can be tried independently of SBX.

For a product demonstration, the next step is to launch that composed environment
with an available SBX daemon, verify its interpreter and workspace behavior, and
check runtime policy enforcement. The environment declaration's CLI grammar was
checked against official SBX help, but this composed runtime demonstration has
not been executed.

## What a product manager can assess today

The repository contains a built and verified kit artifact recipe, a working
sample, a developer guide, and an automated verification workflow. Independent
QC passed 49 tests, 11 evaluation cases, 19 kit conformance checks, and a Debian
filesystem probe using the bundled interpreter. The
[first hosted workflow](https://github.com/shelajev/langchain-policy-lab/actions/runs/37961247968)
also passed. See [verification evidence](verification-report.md) and
[independent QC](qc-delivery-report.md) for the scope of those results.

This gives a concrete artifact set for discussing framework-specific kits:
what environment the kit should install, what starter project helps a developer
get moving, and what guide and checks make that project understandable. It does
not yet demonstrate a published kit installation or the full SBX runtime journey.
There is no Docker Hub release, real customer deployment, or live-model quality
result.

For sharing the idea, the [marketing brief](marketing-brief.md) explains the
audience and supported claims. The [blog outline](blog-outline.md) proposes a
developer article; it is an outline, not a finished post. Start with this overview
for the product story and use the guide for the hands-on developer story.
