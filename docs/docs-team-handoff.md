# Docs team handoff: LangChain apps in Docker Sandboxes

This page is the public entrypoint and readiness summary for the LangChain-in-Docker-Sandboxes learning path. It maps the repository components, separates automated CI checks from manual historical observations, and lists the product and platform decisions still open before documentation or image publication.

Docker Sandboxes is abbreviated SBX here; `sbx` is its CLI. The source repository is public at `https://github.com/shelajev/langchain-policy-lab` (source baseline `d51cc029`). No Docker Docs page has been published, no kit image has been pushed to Docker Hub, and no cloud sandbox has been run.

A kit packages a filesystem overlay and requested capabilities. This kit is a **mixin**: it adds the app and its Python environment to the `shell` **workload**, which supplies the sandbox's user, entrypoint and shell session. At runtime, SBX applies network rules composed from kit requests and existing local or organization policies; an allow request does not revoke other grants, and denies win. By SBX proxy design and the declared credential binding, the proxy holds the real provider key and injects it only into supported matching requests, while the guest SDK is configured with a placeholder. This is a platform/descriptor design statement: the historical run did not directly inspect guest environment values; its runtime evidence is the authenticated call and scoped-secret override described below. Ordinary container probes and OCI format checks do not exercise that native runtime policy/proxy layer.

## Learning path and repository map

The primary learning path is one page in docs.docker.com structure:

- [Run your LangChain app in Docker Sandboxes](run-your-langchain-in-docker-sandboxes.md): the canonical guide, teaching the end-to-end kit workflow on a single page.
- [skills/langchain-sandbox-kit/](../skills/langchain-sandbox-kit/SKILL.md) and [user-guide.md](user-guide.md): the coding-agent skill and its reference page.
- [examples/single-file-agent/](../examples/single-file-agent/README.md) and [single-file-agent.answers.json](../examples/single-file-agent.answers.json): the primary example app (`init_chat_model`, `FakeListChatModel`, and `langchain-google-genai`) and recorded inspector answers.
- [examples/single-file-agent-kit/](../examples/single-file-agent-kit/RUN.md): the kit generated from that example.

The coding agent authors the kit wherever the project is available in its authorized environment (on the host or in a separate authoring sandbox). It is not installed into the runtime `shell` workload by this mixin. `NAME-context.md` packages run guidance for compositions that do have a coding agent; with `shell`, no coding agent reads it automatically, so the human follows `RUN.md`. Its authoring login is independent of the app SDK's runtime provider credential.

Tooling and generated artifact roles:

- Alongside the copied app, dependency files and agent context, a generated kit directory contains `NAME.yaml` (the capability descriptor requesting network hosts and proxy secrets), `NAME.dockerfile` (the image overlay), `kit-manifest.json` (output SHA-256 hashes), `PERMISSIONS.md`, and `RUN.md`.
- [sbx_langchain_kit.py](../skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py) provides `inspect`, `generate` and `explain` for the kit workflow, plus contributor-only `direct`, which writes a filtered workspace, `sbxenv.yaml` (consumed by `sbx env`) and access/run files for running without a generated mixin image. `inspect` statically reads app files and reports access questions; `generate` uses reviewed answers to write the kit; `explain` checks the permission-summary hash against `kit-manifest.json` and prints that summary (it does not compare the descriptor). These are distinct from the Docker Sandboxes CLI command `sbx kit inspect`.
- `kit-tck` validates OCI kit format conformance; it does not test sandbox runtime isolation.

Supporting repo-only artifacts (excluded from the primary docs path unless separately accepted for docs expansion):

- `examples/ticket-triage/`: a packaged `src` app with data files. Its status URL comes from `TRIAGE_STATUS_URL` at runtime, so static inspection cannot resolve the host; the developer must decide the exact allowed host. Its generated kit is in `examples/ticket-triage-kit/`.
- `sample/`: a lexical question-answering lab over synthetic company policies (distinct from sandbox network policy), with tools and an eval suite, packaged by root `langchain.yaml` and `langchain.dockerfile`. The supporting [policy-lab guide](policy-lab-guide.md) also documents contributor build prerequisites.
- Direct-run regression fixtures (`scripts/check-direct.sh`): the helper `direct` subcommand and fixtures support contributor checks; they are not the kit learning path.

Companion records:

- [acceptance-handoff.md](acceptance-handoff.md): fresh native sandbox verification runbook and historical host observations for `examples/single-file-agent-kit/`.
- [provenance.md](provenance.md): pinned `sandbox-kit-spec` files, CI tool versions, Python lock behavior, and API metadata inspection for `sample/`.

## Audience and learning outcomes

The target audience is Python developers who have a LangChain app and a coding agent (such as Claude Code or Codex), have Docker Sandboxes (`sbx`) and a working local Docker Buildx plugin installed (needed when `sbx run --kit` builds a local kit directory), and have not built a kit before. Basic LangChain, Git, and shell familiarity are assumed; `uv`, kits, mixins, and workloads are introduced where used. A Gemini API key is required only for the final live call as the app's runtime credential in the sandbox proxy, separate from the coding agent's own account.

After completing the guide, a reader can:

1. Separate the coding agent's provider and login from the app's model provider and API key.
2. Lock dependencies and generate a kit with the skill, answering access prompts with allow, deny, or out-of-scope while knowing that adding an allow request does not make the composed sandbox policy exclusive (other grants can widen access, while denies win).
3. Read the generated descriptor's network and credential requests alongside `PERMISSIONS.md`.
4. Launch a detached sandbox (`sbx run --detach shell --kit ...`), invoke all `sbx` commands on the host and distinguish commands passed to `sbx exec`, which execute in the guest, run the app offline, configure `sbx secret set google --sandbox ...`, and run against the live model.
5. Understand what cloud sandboxes and publishing to Docker Hub would require, and where verified evidence ends.

## Verification by evidence class

CI checks and manual historical observations cover different layers and must not be conflated. Unit, generation, `kit-tck`, and container probe checks test artifact structure and entrypoints; they are distinct from native `sbx` runtime confinement and proxy secret injection.

### Continuous integration contract (current revision)

On push and manual dispatch, [ci.yml](../.github/workflows/ci.yml) installs pinned tools, selects an isolated BuildKit builder and runs the checks marked "yes" in the workflow column below. `clean-checkout.sh` clones the repository into a temporary directory, selects managed Python 3.13.7 and isolated dependency caches, then runs the checks marked in its column. A check marked in both columns runs again in that clean clone; those are not separate kinds of runtime evidence. Check the actual revision's [Actions result](https://github.com/shelajev/langchain-policy-lab/actions) before calling it passed.

| Check script | Workflow directly | Clean clone | What it checks |
| --- | --- | --- | --- |
| `check-sample.sh` | yes | yes | Locked sample environment, pytest, eval suite, deterministic queries/read-only tools and optional-provider imports; no live call |
| `check-example.sh` | no | yes | Locked ticket-triage environment, pytest and fake CLI output |
| `check-skill.sh` | no | yes | helper unit tests, including provider mappings, hash checks and regeneration/byte comparisons against committed fixtures ("golden" checks) |
| `check-doc-links.py` | no | yes | The repository checker's internal Markdown link targets |
| `check-kit.sh` | yes | yes | Build root `langchain.yaml`, export its OCI layout and validate it with `kit-tck` |
| `check-filesystem.sh` | yes | yes | Build the policy overlay; check its interpreter and eval suite in an offline read-only uid-1000 Debian probe |
| `check-generated-kit.sh` | no | yes | Build/TCK-check the ticket-triage kit; compose with the shell image and check fake output, file hygiene and a clean network-none failure |
| `check-raw-single-file.sh` | no | yes | Start with `agent.py` and `requirements.txt`, add reviewed `pyproject.toml` / `.python-version` / `uv.lock` without changing the app, inspect a synthetic secret-file canary, and generate/build a kit (or direct output when requested) |
| `check-single-file.sh` | no | yes | Build/TCK-check the committed single-file kit; assert its fake JSON in the offline read-only uid-1000 shell-image probe |
| `check-direct.sh` | no | yes | Check raw direct output and an equivalent manually selected app snapshot in an ordinary offline container; unchanged source and file-exclusion checks, no native sandbox run |
| `clean-checkout.sh` | yes | no | Run the clean-clone checks above and require a clean Git working tree at the end |

The clean-clone build/TCK/container branch requires both `docker` and `kit-tck` on PATH. If either is absent, the script prints `NOT RUN` and exits 1; it does not silently pass. CI installs both. Its dependency-age environment is `UV_EXCLUDE_NEWER=P7D` (seven days). None of these checks establishes native SBX network confinement or proxy injection.

### Earlier artifact-check reports

Earlier project records report build, container and `kit-tck` passes for `examples/single-file-agent-kit/` and `examples/ticket-triage/`, plus unit, eval, build, `kit-tck` and container passes for `sample/`. Per-run logs, dates and revision identifiers for those artifact checks are not linked here. Treat this as historical context, not a current-revision pass. These old reports add no additional promised artifact-check scope beyond the reproducible CI checks above; use actual green CI on the revision under review to replace them as current artifact evidence. Native sandbox observations below have a separate date and scope.

### Manual historical observations (not run in CI)

| Observation | Scope and recorded outcome |
| --- | --- |
| `sbx` CLI syntax | Checked against `sbx` v0.53.0 `--help` for `run`, `exec`, `rm`, `secret`, `policy`, `kit`, and `--cloud` |
| App response-format development check | An earlier app-only check of `examples/single-file-agent/` initially returned truncated model output. Its SDK settings now include `thinking_budget=0` and JSON response type; a subsequent development call returned parseable JSON for synthetic ticket `T-101`. That development environment is not specified here and supplies no native sandbox-boundary evidence |
| Native host sandbox run of `examples/single-file-agent-kit/` (2026-11-13, pre-public-history commit `aa2af15`, `sbx` v0.53.0) | **Historical partial-workflow pass.** Detached kit build and sandbox creation (no sandbox approval prompt appeared), offline `--fake-model` JSON output, deployed-filesystem hygiene (not independent proof of adversarial private-file exclusion), `example.com` HTTP 403 with matching policy block log, live Gemini run using the host's pre-existing global `google` secret, post-creation synthetic invalid scoped key (`API_KEY_INVALID` without restart, followed by removal restoring the global call without restart), and cleanup all passed. Recorded details, including the session-specific `DOCKER_CONFIG` Buildx issue and `sbx kit inspect --offline` exit 1, are in [acceptance-handoff.md](acceptance-handoff.md) |

### Unverified or unrun surfaces

- **Clean-host real scoped-key workflow:** Not verified. Entering a real key interactively at `sbx secret set` and immediately running the live call without a pre-existing global secret has not been exercised.
- **Other repository artifacts in native sandboxes:** Native sandbox and live model runs are unrun for `examples/ticket-triage/` and `sample/`.
- **Other providers and accounts:** Native and live proxy evidence covers Google (Gemini) with a pre-existing global key only. OpenAI and Anthropic have descriptor/mapping unit tests only; no new real accounts or keys were tested.
- **Cloud and Docker Hub:** `sbx --cloud` sandboxes and Docker Hub publishing remain unrun (documentation only).

Here, an approval prompt means any CLI request for the user to confirm the kit's requested resources. The historical configured host showed none. The clean-host interaction has not been observed, so these records do not establish when prompts appear or their exact wording.

## Decisions for product and platform owners

- **Repository home:** The public repository is at `https://github.com/shelajev/langchain-policy-lab`, and the guide links to it. Decide whether docs publication needs an alternate mirror or canonical URL.
- **Interactive scoped-key and approval prompts:** No sandbox approval prompt appeared in the historical host run, and the interactive `sbx secret set` prompt was not exercised with a real key. Decide whether to verify that clean-host flow before describing it as end-to-end tested.
- **Local kit prerequisites:** `sbx run --kit ./dir` builds local kits via host Docker Buildx. The canonical guide also uses Git to clone this repository; Git is not a requirement of an already-local `sbx run --kit` invocation. These tools are already listed in the guide. The owner decision is how to present supported local host setup in the published prerequisites, not whether this recorded local-build path needs Buildx.
- **Cloud section:** Cloud sandboxes are unrun with this kit. Decide whether to keep the cloud section and which cloud secret and network commands to document.
- **Provider framing:** Decide how to present Gemini (native historical evidence) versus OpenAI and Anthropic (unit/descriptor tests only) and providers needing manual descriptor/host/credential review (`groq`, `mistral`, `openrouter`, `xai`, Vertex AI, Azure OpenAI, Bedrock). The helper has automatic credential mappings only for Gemini, OpenAI and Anthropic; the [capability reference](../skills/langchain-sandbox-kit/references/capabilities.md) distinguishes native services from provider-specific setup outside those mappings. This is a helper-automation limit, not a claim that SBX supports none of these services.
- **Experimental surface:** `sbx kit` and `--kit` are marked experimental in the CLI. Decide how the published page labels that status.
