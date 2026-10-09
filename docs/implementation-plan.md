# Current implementation plan

Run `000000000000000018dcd9b9d5da52d8-f628885e0369bb1d`, round 1, implementer.
The original supplied plan was the first repository edit, before implementation;
it is preserved verbatim in `initial-planner-plan.md`. This current plan replaces
its illustrative versions, invalid grammar/commands and broad portability claims.
Observed outcomes belong in `verification-report.md`, not this plan.

## Audience and shape

Deliver a learning lab for enterprise Python/AI platform teams: ingest four
synthetic policies, retrieve source passages, inspect section/chunk citations,
invoke bounded read-only LangChain tools, evaluate grounded/unsupported/failure
paths, and optionally select an explicitly approved live provider. Default
execution must need no paid API key. Do not claim production readiness.

Use `kind: mixin`: teams can add tooling to an existing agent workload without
replacing its entrypoint, user or workdir. Ship managed CPython 3.13.7 **and** its
locked environment under `/opt/langchain`. Request only `agent-context@1`.
No network, credential, privilege, resource, cache volume, sharing or lifecycle
capability is necessary for the installed deterministic sample.

The interpreter is a GNU/glibc build, not a self-contained operating system.
Claim only observed native Linux arm64 Debian 12 compatibility. An amd64
Ubuntu hosted job checks the second target when run. Do not assert musl/Alpine,
scratch execution, macOS/Windows or arbitrary minimal-base compatibility.

## Implementation sequence and acceptance

1. Create `feat/langchain-enterprise-kit`; save this plan before implementation.
   Preserve the supplied planner draft, then record implementation adjustments.
2. Recover official create-kit-v3 skill at
   `a1d110de252bcc3cb2fa6d47fe37137a1a328b97`, its recipes, normative spec,
   applicable capability references/schemas and official environment example.
   Record hashes/source paths. No migration: the repository was empty.
3. Use ACR 0.2.1 to install/realize
   `github:shelajev/blog-writer@61844184d925b9f925951241a0d476db7c193e7e`
   for Codex and Claude Code. Track `agents.yaml` and `.agents/registry.lock`,
   ignore generated caches/native skill trees. Run `env -u GH_TOKEN acr check`.
4. Create travel, expenses, remote work and security Markdown policies with
   synthetic thresholds and section metadata. Reject invalid/empty input.
5. Implement real `Document`, `BaseRetriever`, LCEL prompt/model/parser and
   `langchain.tools.tool` usage. Default fake extracts retrieved content, not
   canned answers. Validate citation IDs and return explicit unsupported or
   sanitized failure outputs. Bound read-only meal/receipt tools with Pydantic.
6. Pin verified releases: LangChain 1.4.4, core 1.6.9, Pydantic 2.14.0,
   pytest 8.4.2, hatchling 1.27.0. Gemini integration 4.4.0 is an optional
   dependency. Lock transitive wheels/sdists with uv 0.9.26. Save exact API
   implementation-file hashes and official release/source provenance.
7. Author companion descriptor/recipe/context. Digest-pin frontend and uv
   image, install managed Python, use `uv sync --locked --all-extras --no-dev
   --no-editable`, copy full prefix to scratch, normalize ownership, enforce
   declared LangChain version against installed metadata. Final PATH is a
   static additive field; never copy a venv without its interpreter.
8. Verify the official sbx release/help inside the sandbox without invoking a
   daemon. Author a supported environment with a digest-pinned shell workload
   and `../` mixin; mount only the project. No environment lifecycle hooks:
   those run on the **host**, not as in-sandbox postCreate tests.
9. Add runnable GitHub Actions on `ubuntu-24.04`. Fetch official checksum-pinned
   uv; fetch exact kit-spec commit and build kit-tck with Go 1.26.8. Use a
   pinned Docker-container BuildKit builder. Required checks must fail on
   failures, not skip or use `continue-on-error`. Do not invent SBX runners.
10. Execute separate verification layers, retaining exact commands/output:
    - `bash scripts/check-sample.sh`: offline/fake tests, evaluation and CLI
      tools, plus optional provider import only (no live-provider claims).
    - `docker buildx build . -f langchain.yaml --output type=cacheonly`:
      strict source validation **and** content build, not a schema-only check.
    - `bash scripts/check-kit.sh <fresh-layout>`: source build, OCI directory
      export, `kit-tck validate --layout <fresh-layout> 1.4.4`.
    - `bash scripts/check-filesystem.sh`: non-SBX filesystem/dependency probe
      on a pinned no-system-Python Debian base, network none, uid 1000,
      read-only. Manually supply PATH; do not call this assembled composition.
    - `bash scripts/clean-checkout.sh`: clone committed files locally, isolated
      cache/managed interpreter, locked installs, tests and CLI journey.
11. Through blog-writer's scoped non-blog route, write README quickstart, full
    guide, factual marketing brief and proposed outline. Neutral identity;
    preserve evidence boundaries, limitations and optional author gates.
12. Run the installed `sweep.py --mode final` on each public artifact. Record
    contextual hits and preservation comparison. Run `fresh-reader.py` with
    complete reader drafts and `--audience <UTF-8-brief-file>`, no private/source
    context or prior reviews. Read findings, repair substantive gaps, and
    rerun statelessly. Report unavailable review honestly if necessary.
13. Commit locally, run clean-checkout against committed implementation, add
    final evidence/report commit and ensure clean porcelain. Update crew
    status/escalations and stop editing for independent QC. No pushes.

## Optional HUMAN checks, never acceptance blockers

On an already functioning human-controlled sbx environment, v0.47.0 help
supports `sbx env plan sample/sbxenv.yaml`, `sbx env run --detached
sample/sbxenv.yaml` and `sbx env exec sample/sbxenv.yaml -- <command>`.
The human owns approval, actual composition/merged PATH/launch verification,
network deny tests and cleanup. Do not execute host code, bridge a host daemon,
start nested SBX infrastructure or claim policy enforcement from builds.
The optional live sample requires explicit provider selection, approval and an
existing approved credential; editorial Gemini calls are a separate review.

## Justified adjustments from the supplied plan

- Removed unused langchain-community instead of installing it decoratively.
- Added a locked build-dependency group and uv build constraints so isolated
  hatchling builds do not float their transitive tooling.
- Made provider integration optional for the local sample; bundle it in the
  kit so live access never requires a create-time dependency installer.
- Corrected credential schema assumptions (`phase`, nested proxy-managed
  injection; no fictitious `apiKey.env`) by requesting no unnecessary grant.
- Corrected environment `agent` to the reference-derived `sbx-kit-shell` handle;
  removed fictitious in-sandbox environment postCreate tests.
- Replaced nonexistent helper paths/string audience arguments with installed
  helper paths and a real audience file. No identity/persona setup is needed
  for a neutral scoped guide or outline proposal.
- Replaced invalid `sbx run <mixin>` and `--kit <sample>` examples with verified
  environment commands; a mixin alone is not a workload.
- Upstream go.mod has replace directives: `go install @commit` rejects it.
  Exact-commit source checkout plus `go build -mod=readonly` respects the
  upstream module graph and is the CI installation path.
- Pin uv's official checksums and image digest, frontend digest, probe base,
  shell workload digest and CI BuildKit digest. Treat hosted execution as
  pending until an actual Actions run exists.
- Use `uv python install --no-bin` so the isolated clean-checkout interpreter
  does not leave user-bin launchers pointing into a removed temporary directory.
