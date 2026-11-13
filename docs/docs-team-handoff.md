# Docs team handoff: LangChain apps in Docker Sandboxes

This repository is ready for a publication review of one learning path. This
page says what the path teaches, what was checked and how, and what still
needs a decision from the product or platform side before it goes live.

## Canonical page

[Run your LangChain app in Docker Sandboxes](run-your-langchain-in-docker-sandboxes.md)
is a single page in the docs.docker.com guide shape (front matter,
objectives, prerequisites, built-up sections, conclusion, further reading),
about 3,000 words. Everything else in the repository supports it:

- [skills/langchain-sandbox-kit/](../skills/langchain-sandbox-kit/SKILL.md): the
  skill the guide tells readers to copy into their coding agent
- [examples/single-file-agent/](../examples/single-file-agent/README.md) and its
  generated [kit](../examples/single-file-agent-kit/RUN.md): the worked example
- [user-guide.md](user-guide.md): the skill reference linked from the guide

The earlier direct-run path (sandbox without a kit) is gone from the guide,
README and skill description. Its helper subcommand and fixtures remain only
as internal regression tests.

## Audience and prerequisites

Python developers with an existing LangChain app and a coding agent (Claude
Code, Codex or similar), who have Docker Sandboxes installed but have never
written a kit. The guide assumes basic LangChain, Git, a shell and the `sbx`
CLI; it explains uv, kits, mixins and workloads where they first appear. A
Gemini API key is needed only for the last run.

## Learning outcomes

After the guide, a reader can:

1. Tell the coding agent's provider and login apart from the app's model
   provider and key, for Gemini, OpenAI, Anthropic and other providers.
2. Lock an app's dependencies and generate a kit with the skill, answering the
   inspector's access questions with allow, deny or out-of-scope.
3. Read the generated descriptor's network and credential requests and
   `PERMISSIONS.md`.
4. Create the sandbox with `sbx run --detach shell --kit ./my-agent-kit ...`,
   run the app offline, store the key with `sbx secret set google --sandbox ...`
   and run it against the model.
5. Know what cloud sandboxes and publishing to Docker Hub would involve.

## What was checked, by evidence class

| Evidence | Result |
| --- | --- |
| Skill helper unit tests (32), skill frontmatter validator | Pass |
| The guide's own journey: raw app, `uv lock` under a 7-day package-age limit, inspect, generate | Pass; the generated kit builds |
| Kit build with buildx and `kit-tck` conformance (19 checks) for the single-file and ticket-triage kits | Pass |
| Composition probe: kit overlay on the pinned `docker/sbx-kit-shell` image, network off, read-only, uid 1000, running the `RUN.md` command | Pass, prints `{"category":"technical","ticket_id":"T-101"}`; plain `python` fails without the app's dependencies, which is why the guide uses the kit's interpreter path |
| One live Gemini call from the build environment through an existing proxy (not a sandbox) | First attempt failed: truncated reply. After the example's generation settings were fixed (`thinking_budget=0`, JSON response type), the retest returned parseable JSON for `T-101` |
| `sbx` command syntax | Checked against `sbx` v0.53.0 help for `run`, `exec`, `rm`, `secret`, `policy`, `kit` and `--cloud` |
| Fresh-reader review (Gemini 4 Hydrogen), three passes | Instruction blockers found and fixed after each pass: who runs which command, answer meanings and the full decision table, host versus sandbox steps, repository links, the empty deny list. Optional suggestions were not all applied |
| Native sandbox run on a host (`sbx` v0.53.0, `aa2af15`) | **Pass.** All 11 current kit files matched on the host. Kit build and create (no approval prompt appeared), offline run, private-file exclusion, live run through the proxy with the host's existing global `google` credential, blocked `example.com` in the policy log, and cleanup all passed. A post-creation sandbox-scoped secret was shown to take effect without restart using a synthetic invalid value; a real key was not entered at the interactive prompt. Historical: `sbx kit inspect --offline` exits 1 (offline loader limitation, not a validation result), and the first launch exited 125 on host Buildx client configuration before approval |
| Cloud sandboxes, Docker Hub publishing | Not run; documentation only |

The container probe and the guest live call show that the artifact and the app
work. Sandbox network policy, proxy credential injection and the `sbx` build of
a local kit come from the native run recorded in
[acceptance-handoff.md](acceptance-handoff.md). The guide source carries a
comment on each sandbox step saying how it was verified; `<!-- VERIFY -->`
remains on the repository location, the real-key prompt text, cloud and Hub.

## Decisions for product and platform owners

- **Repository home.** The guide links `github.com/shelajev/langchain-policy-lab`.
  Decide the public location of the skill and example before publishing.
- **Approval prompts and secret prompt text.** No approval prompt appeared in
  the host run, so the guide says only what to do if one appears. The
  interactive `sbx secret set` prompt was not exercised with a real key; decide
  whether to capture it before publishing.
- **Local kit directories.** `sbx run --kit ./dir` builds the kit through the
  host's Docker Buildx; the first host launch failed until the Buildx client
  plugin was available. Confirm the supported host setup to state as a
  prerequisite.
- **Cloud.** The guide marks the cloud section as not run with this kit. Decide
  whether to keep it, and what cloud secret and network commands to document.
- **Provider coverage.** The skill maps Gemini (AI Studio), OpenAI and
  Anthropic. Vertex AI, Azure OpenAI, Bedrock, gateways and other `sbx` secret
  services (`groq`, `mistral`, `openrouter`, `xai`) are described as manual.
- **Experimental surface.** `sbx kit` and `--kit` are marked experimental in
  the CLI. Decide how the page labels that.

## Publication boundaries

Nothing has been published: no Hub image, no docs page, no cloud sandbox. The
guide uses synthetic data and one example key-holder flow. Examples in
`examples/` contain no secrets; the helper refuses secret-like literals and
never copies `.env` or private files into a kit.
