PLAN run=000000000000000018dcd9b9d5da52d8-f628885e0369bb1d round=1

# Enterprise LangChain Docker Sandboxes v3 Kit Implementation Plan

## Executive Overview & Architectural Strategy

### 1. Kit Kind & Interpreter Portability Decision: Composable Mixin (`kind: mixin`) with Bundled Standalone Python
- **Kind Decision**: Author `langchain` as a composable mixin (`kind: mixin`).
  - **Rationale**: Enterprise teams run standardized agent workloads (e.g. Codex, Claude, or Shell sandboxes). They require LangChain orchestration, synthetic policy ingestion, and compliance toolchains as an additive overlay rather than replacing their established agent environment.
- **Solving the Virtualenv Portability Trap**:
  - Per Docker Sandboxes v3 `RECIPES.md`, copying a standard virtualenv across container boundaries fails because `/bin/python` symlinks point to the build host's interpreter, causing `ModuleNotFoundError` when layered onto dissimilar target base images.
  - The content recipe (`langchain.dockerfile`) builds a self-contained runtime under `/opt/langchain` using `uv` with a standalone bundled Python interpreter (`uv python install 3.13` / `--managed-python`). When layered onto any base (Debian, Ubuntu, Alpine, or a minimal container with no Python), `/opt/langchain/bin/python` resolves internally without host dependencies.
  - The mixin exports `ENV PATH="/opt/langchain/bin:${PATH}"` and `ENV PYTHONPATH="/opt/langchain/lib/python3.13/site-packages:${PYTHONPATH}"` in its scratch stage.

### 2. Audience & Enterprise User Journey
- **Audience**: Enterprise AI engineers and platform teams building internal knowledge assistants in isolated sandboxes.
- **End-to-End Enterprise Journey**:
  1. Synthetic company policy ingestion: Structured policies for Travel & Per Diem, Expense Reimbursement, Remote Work Equipment, and Information Security.
  2. Document chunking and retrieval: In-memory retrieval returning ranked passages with rigorous source file, section, and chunk ID citations.
  3. Bounded read-only tools: Strict deterministic tools for meal allowance lookup and receipt requirement threshold verification.
  4. Grounded question evaluation vs. unsupported question refusal: System answers policy questions with citations; cleanly refuses out-of-scope queries (e.g. pet policies, office pets) without hallucinations.
  5. Default credential-free deterministic path: Uses `DeterministicFakeChatModel` delivering reproducible policy answers and citation structures offline without any API keys or network calls.
  6. Opt-in approved live provider: Google Gemini (`ChatGoogleGenerativeAI`) enabled explicitly via `LANGCHAIN_PROVIDER=gemini` using existing proxy credentials.
  7. Honest enterprise scope: Clearly explain sandbox network isolation, deterministic vs. live testing, and data boundaries without claiming demo-level production readiness.

### 3. Environment Grammar & CLI Provenance
- Nested `sbx` CLI executable is not installed in the container environment (ESC-001).
- Grammar provenance for `sbxenv.yaml` is recovered directly from primary sources in the official `github.com/docker/sandbox-kit-spec` repository pinned at commit `a1d110de252bcc3cb2fa6d47fe37137a1a328b97` (found locally in `/home/agent/go/pkg/mod/...` and copied to `docs/references/sandbox-kit-spec/sbxenv.yaml`).
- No invented flags or YAML fields: all descriptors and environment configurations conform strictly to the published specification.

### 4. Non-SBX Verification vs. Optional Human SBX Runtime Handoff
- Per binding human goal continuation:
  - **No nested SBX daemon, host execution, or daemon bridge is requested or authorized.**
  - **In-Sandbox Verification Scope**: Complete all available non-SBX build and validation checks inside this sandbox:
    1. Docker Buildx source validation (`docker buildx build . -f langchain.yaml --output type=cacheonly`).
    2. Docker Buildx OCI layout export (`docker buildx build . -f langchain.yaml -t langchain:1.4.4 --output type=oci,dest=/tmp/langchain-layout,tar=false`).
    3. `kit-tck` layout conformance verification (`kit-tck validate --layout /tmp/langchain-layout 1.4.4`).
    4. Python behavioral unit and integration test suite (`uv run --project sample pytest sample/tests/ -v`).
    5. Clean-checkout sample CLI execution (`uv run --project sample python -m langchain_enterprise.cli --eval-suite`).
    6. ACR package realization and Gemini reader review.
  - **Optional Human SBX Runtime Handoff**: Assembled composition (`sbx run ./langchain`, `sbx env run`) requires Docker Sandboxes CLI / daemon on the host. This is formally documented in `docs/verification-report.md` as an optional human handoff with exact host commands, not an automated acceptance blocker.
  - **Correction of ESC-001**: Prior planning assertions are treated as planned/not yet evidenced. Verification reports only observed tool outputs.

### 5. GitHub Actions Workflows on Real Hosted Runners
- Workflow `.github/workflows/ci.yml` targets real GitHub Actions runner `ubuntu-latest`.
- Enforces all runnable checks without silent skips:
  - Setup Python & uv, execute sample tests and CLI evaluation suite.
  - Setup Go, install pinned `kit-tck` from `github.com/docker/sandbox-kit-spec/v3/cmd/kit-tck@a1d110de252bcc3cb2fa6d47fe37137a1a328b97`.
  - Setup Docker Buildx, validate descriptor source syntax (`type=cacheonly`).
  - Export OCI layout and run `kit-tck validate --layout`.
- Clearly documents the boundary: does not pretend hosted SBX runners exist; excludes optional human SBX runtime checks from automated claims.

### 6. Editorial, Marketing & Blog-Writer Scope via ACR 0.2.1
- Realize pinned package `github:shelajev/blog-writer@61844184d925b9f925951241a0d476db7c193e7e` using ACR 0.2.1; track `agents.yaml` and `.agents/registry.lock`.
- Follow the scoped non-blog route (`scoped-edit.md`) for user guide, README, and marketing brief.
- Neutral authorial voice: strictly grounded in assignment facts; no invented Oleg personal experience or Docker corporate persona.
- Author a factual marketing brief/explainer and proposed blog outline based on actual build evidence. Author identity selection gates are left explicitly pending.
- Run stateless Gemini audience review via `fresh-reader.py` using only complete draft and audience prerequisites (never plans, sources, or private history). Address reader feedback and record review transcript.

### 7. Crew Roles and Single Repository Writer Enforcement
- **Implementer (`codex`)** is the sole repository writer. The implementer must copy this plan into `docs/implementation-plan.md` in the repository as its first step.
- Planner (`pi`) authors this plan and updates status notes in `/home/agent/crew/status.md`.
- Quality Control (`claude`) will independently inspect clean porcelain state and verify all acceptance criteria.

---

## Detailed Step-by-Step Implementation Plan

### Step 1: Branch Setup and Implementation Plan Archival in Repository
- **Assigned Role**: Implementer (single repository writer)
- **Files**:
  - `docs/implementation-plan.md`
- **Actions**:
  1. Check out dedicated branch: `git checkout -b feat/langchain-enterprise-kit`.
  2. Create directory `docs/`.
  3. Copy this `/home/agent/crew/plan.md` content verbatim into `docs/implementation-plan.md`.
- **Observable Done Condition**:
  - `git branch --show-current` outputs `feat/langchain-enterprise-kit`.
  - `test -f docs/implementation-plan.md` succeeds with matching content.

### Step 2: Fetch and Archive Reference Specifications & Official Skill
- **Assigned Role**: Implementer
- **Files**:
  - `docs/references/create-kit-v3/SKILL.md`
  - `docs/references/create-kit-v3/RECIPES.md`
  - `docs/references/sandbox-kit-spec/sbxenv.yaml`
- **Actions**:
  1. Copy the official pinned `create-kit-v3` skill sources (`SKILL.md` and `RECIPES.md`) from local Go cache `/home/agent/go/pkg/mod/github.com/docker/sandbox-kit-spec/v3@v3.0.0-m.8.0.20261008125117-a1d110de252b/skills/create-kit-v3/` into `docs/references/create-kit-v3/`.
  2. Copy the reference `sbxenv.yaml` from `/home/agent/go/pkg/mod/github.com/docker/sandbox-kit-spec/v3@v3.0.0-m.8.0.20261008125117-a1d110de252b/sbxenv.yaml` into `docs/references/sandbox-kit-spec/sbxenv.yaml`.
  3. Record exact commit hash `a1d110de252bcc3cb2fa6d47fe37137a1a328b97` in `docs/references/PROVENANCE.md`.
- **Observable Done Condition**:
  - `grep -q "create-kit-v3" docs/references/create-kit-v3/SKILL.md` returns 0.
  - `grep -q "schemaVersion: \"1\"" docs/references/sandbox-kit-spec/sbxenv.yaml` returns 0.

### Step 3: Project-Local ACR Realization of `shelajev/blog-writer`
- **Assigned Role**: Implementer
- **Files**:
  - `agents.yaml`
  - `.agents/registry.lock`
  - `.codex/skills/...`
  - `.claude/skills/...`
- **Actions**:
  1. Install pinned package: `env -u GH_TOKEN acr install github:shelajev/blog-writer@61844184d925b9f925951241a0d476db7c193e7e --agent codex --agent claude-code --non-interactive`.
  2. Realize locked packages: `env -u GH_TOKEN acr realize`.
  3. Verify `acr check` runs cleanly.
- **Observable Done Condition**:
  - `acr check` exits 0.
  - `test -f agents.yaml && test -f .agents/registry.lock` succeeds.
  - `test -f .codex/skills/acr__shelajev__blog-writer__blog-writer/fresh-reader.py` succeeds.

### Step 4: Synthetic Enterprise Policy Documents Dataset
- **Assigned Role**: Implementer
- **Files**:
  - `sample/data/policies/travel_policy.md`
  - `sample/data/policies/expense_policy.md`
  - `sample/data/policies/remote_work_policy.md`
  - `sample/data/policies/security_policy.md`
- **Content Details**:
  - `travel_policy.md`: Airfare classes, city tier meal allowances (Tier 1: $90/day, Tier 2: $70/day, Tier 3: $50/day), lodging limits, and booking window rules.
  - `expense_policy.md`: Receipt requirement threshold ($25 and above), reimbursement submission deadline (30 days), eligible vs ineligible expenses.
  - `remote_work_policy.md`: Home office setup stipend ($500 one-time), monthly internet reimbursement ($50), core collaboration hours (10:00-15:00 UTC).
  - `security_policy.md`: Data classification (Public, Internal, Confidential, Restricted), API key and secret storage rules, password policies, device encryption requirements.
- **Observable Done Condition**:
  - 4 markdown files authored with frontmatter, section headers, clear rules, and explicit numeric thresholds.

### Step 5: Enterprise LangChain Sample Implementation
- **Assigned Role**: Implementer
- **Files**:
  - `sample/pyproject.toml`
  - `sample/uv.lock`
  - `sample/src/langchain_enterprise/__init__.py`
  - `sample/src/langchain_enterprise/config.py`
  - `sample/src/langchain_enterprise/ingestion.py`
  - `sample/src/langchain_enterprise/retriever.py`
  - `sample/src/langchain_enterprise/tools.py`
  - `sample/src/langchain_enterprise/models.py`
  - `sample/src/langchain_enterprise/chain.py`
  - `sample/src/langchain_enterprise/cli.py`
- **Primary Pinned Dependencies**:
  - `langchain==1.4.4`
  - `langchain-core==1.6.9`
  - `langchain-community==0.4.2`
  - `langchain-google-genai==4.4.0`
  - `pydantic==2.14.0`
  - `pytest==8.4.2`
- **Architecture & Implementation Logic**:
  - `config.py`: Settings dataclass for policies directory path, provider selection (`deterministic` vs `gemini`), and model parameters.
  - `ingestion.py`: Markdown loader and header-based chunker that attaches structured metadata: `source` (filename), `section` (header path), `chunk_id`, and `title`.
  - `retriever.py`: In-memory retriever that computes token overlap / BM25 scores over chunks and returns top-k matching documents with citation metadata.
  - `tools.py`: Bounded read-only calculation tools:
    - `calculate_meal_allowance(city_tier: int, days: int) -> float`
    - `check_receipt_requirement(amount: float) -> dict`
  - `models.py`:
    - `DeterministicFakeChatModel`: Subclasses `BaseChatModel`. Deterministically inspects query keywords or context passages to produce predictable structured answers with citations offline. Requires zero credentials.
    - `get_model(provider: str)`: Returns `DeterministicFakeChatModel` by default, or `ChatGoogleGenerativeAI(model="gemini-2.5-flash")` if `provider == "gemini"` and `GEMINI_API_KEY` is present.
  - `chain.py`: LCEL orchestration combining retrieval, optional tool execution, structured citation formatting, and safe fallback refusal for out-of-scope/unsupported queries.
  - `cli.py`: Command line interface supporting:
    - `--query "<text>"`: Single query execution.
    - `--eval-suite`: Runs evaluation queries (grounded vs unsupported) and prints structured results.
    - `--provider {deterministic,gemini}`: Selects provider backend.
- **Observable Done Condition**:
  - `uv lock --project sample` generates valid `sample/uv.lock`.
  - `uv run --project sample python -m langchain_enterprise.cli --query "What is the daily dinner reimbursement limit for Tier 1 cities?"` returns answer with citation to `travel_policy.md`.
  - `uv run --project sample python -m langchain_enterprise.cli --query "Can I bring my pet python into the office?"` returns structured refusal: unsupported query not covered by synthetic policies.

### Step 6: Comprehensive Python Test Suite
- **Assigned Role**: Implementer
- **Files**:
  - `sample/tests/conftest.py`
  - `sample/tests/test_ingestion.py`
  - `sample/tests/test_retrieval.py`
  - `sample/tests/test_tools.py`
  - `sample/tests/test_grounded_eval.py`
  - `sample/tests/test_unsupported_refusal.py`
  - `sample/tests/test_models.py`
  - `sample/tests/test_cli.py`
- **Test Scenarios**:
  1. `test_ingestion.py`: Verifies loading of 4 policy files, chunking, and metadata preservation (source, section, chunk_id).
  2. `test_retrieval.py`: Tests retrieval ranking, citation attachment, and top-k accuracy.
  3. `test_tools.py`: Tests `calculate_meal_allowance` and `check_receipt_requirement` with boundary and invalid input cases.
  4. `test_grounded_eval.py`: Tests 5 grounded enterprise questions across travel, expense, remote work, and security; asserts correct facts and citations.
  5. `test_unsupported_refusal.py`: Tests 5 unsupported/out-of-scope questions (e.g. pet policy, company car, holiday bonuses); asserts clear refusal without hallucination.
  6. `test_models.py`: Verifies `DeterministicFakeChatModel` runs without network/credentials; verifies provider switching logic.
  7. `test_cli.py`: Tests CLI arguments, exit codes, and output formatting.
- **Observable Done Condition**:
  - `uv run --project sample pytest sample/tests/ -v` passes with 100% success rate (zero failures).

### Step 7: Docker Sandbox Kit v3 Descriptor, Portable Recipe & Context
- **Assigned Role**: Implementer
- **Files**:
  - `langchain.yaml`
  - `langchain.dockerfile`
  - `langchain-context.md`
  - `README.md`
- **Descriptor Specification (`langchain.yaml`)**:
  - `# syntax=docker/sandbox-kit:3`
  - `schemaVersion: "3"`
  - `kind: mixin`
  - `displayName: LangChain Enterprise`
  - `description: Enterprise LangChain orchestration toolkit and synthetic policy assistant runtime`
  - `version: "${{ kit.args.version }}"`
  - `args`:
    - `version`: default `"1.4.4"`, buildArg `LANGCHAIN_VERSION`
  - `provides: ["langchain@${{ kit.args.version }}"]`
  - `capabilities`:
    - `type: com.docker.sandbox/network-policy@1`:
      - runtime allow: `["pypi.org", "files.pythonhosted.org", "generativelanguage.googleapis.com"]`
    - `type: com.docker.sandbox/credential@1`:
      - `optional: true`
      - `service: gemini`
      - `apiKey: { name: GEMINI_API_KEY, env: GEMINI_API_KEY }`
      - `inject: [{ domain: "generativelanguage.googleapis.com" }]`
    - `type: com.docker.sandbox/agent-context@1`:
      - `config: { contentFile: ./langchain-context.md }`
- **Recipe Specification (`langchain.dockerfile`)**:
  - Multi-stage build:
    - Stage 1 (`build`): Use `debian:bookworm-slim` or `ghcr.io/astral-sh/uv:debian-slim`.
      - Install standalone CPython 3.13 via `uv python install 3.13`.
      - Create self-contained environment in `/out/opt/langchain` containing Python interpreter, standard library, and pinned LangChain dependencies (`langchain==1.4.4`, `langchain-core==1.6.9`, `langchain-community==0.4.2`, `langchain-google-genai==4.4.0`).
      - Verify interpreter portability: `/out/opt/langchain/bin/python` is self-contained.
    - Stage 2 (`scratch`):
      - `FROM scratch`
      - `COPY --from=build /out /`
      - `ENV PATH="/opt/langchain/bin:${PATH}"`
      - `ENV PYTHONPATH="/opt/langchain/lib/python3.13/site-packages:${PYTHONPATH}"`
- **Agent Context (`langchain-context.md`)**:
  - Instructions for agent operating in a sandbox layered with this mixin: explains available CLI tools, Python paths, synthetic policy locations, and provider boundaries.
- **Root `README.md`**:
  - Overview of kit, architecture decisions, quickstart instructions, and composition guide.
- **Observable Done Condition**:
  - `docker buildx build . -f langchain.yaml --output type=cacheonly` succeeds.

### Step 8: Sample Project `sbxenv.yaml` Environment Configuration
- **Assigned Role**: Implementer
- **Files**:
  - `sample/sbxenv.yaml`
- **Grammar & Configuration**:
  - `schemaVersion: "1"`
  - `name: langchain-enterprise-sample`
  - `agent: shell`
  - `kits`:
    - `../` (local kit mixin)
  - `workspace: .`
  - `env`:
    - `LANGCHAIN_PROVIDER: "deterministic"`
    - `POLICIES_DIR: "data/policies"`
  - `lifecycle`:
    - `postCreate`: runs verification suite
  - `bindings`:
    - `gemini`:
      - `apiKey`:
        - `domains: ["generativelanguage.googleapis.com"]`
- **Observable Done Condition**:
  - `sample/sbxenv.yaml` matches official v3 schemaVersion "1" grammar; documented in `docs/sbxenv-grammar-provenance.md`.

### Step 9: GitHub Actions CI Workflow Authoring
- **Assigned Role**: Implementer
- **Files**:
  - `.github/workflows/ci.yml`
- **Workflow Content**:
  - Name: `LangChain Enterprise Kit CI`
  - Trigger: `push`, `pull_request`
  - Runner: `ubuntu-latest`
  - Steps:
    1. Checkout repository: `actions/checkout@v4`.
    2. Set up Python & uv: `astral-sh/setup-uv@v5` with version `0.9.26`.
    3. Install sample dependencies and run pytest:
       `uv run --project sample pytest sample/tests/ -v`
    4. Execute clean-checkout sample evaluation CLI:
       `uv run --project sample python -m langchain_enterprise.cli --eval-suite`
    5. Set up Go: `actions/setup-go@v5` with `go-version: '1.24'`.
    6. Build and install pinned `kit-tck`:
       `go install github.com/docker/sandbox-kit-spec/v3/cmd/kit-tck@a1d110de252bcc3cb2fa6d47fe37137a1a328b97`
    7. Set up Docker Buildx: `docker/setup-buildx-action@v3`.
    8. Descriptor source syntax validation:
       `docker buildx build . -f langchain.yaml --output type=cacheonly`
    9. OCI layout export:
       `docker buildx build . -f langchain.yaml -t langchain:1.4.4 --output type=oci,dest=/tmp/langchain-layout,tar=false`
    10. Conformance validation with kit-tck:
        `kit-tck validate --layout /tmp/langchain-layout 1.4.4`
    11. Boundary statement step: Echo and record that full assembled `sbx run` / `sbx env run` execution requires a host Docker Sandboxes daemon environment and is documented as an optional human handoff, not run in standard hosted CI runners.
- **Observable Done Condition**:
  - `.github/workflows/ci.yml` contains zero conditional skips, no fabricated passes, and valid GitHub Actions syntax.

### Step 10: Multi-Layer Verification & Conformance Testing
- **Assigned Role**: Implementer
- **Files**:
  - `docs/verification-report.md`
- **Verification Execution & Layers**:
  - **Layer 1: Python behavioral test suite**:
    - Command: `uv run --project sample pytest sample/tests/ -v`
    - Record full test pass output.
  - **Layer 2: Clean-checkout sample run**:
    - Command: `uv run --project sample python -m langchain_enterprise.cli --eval-suite`
    - Record output showing grounded queries with citations and unsupported refusals.
  - **Layer 3: Docker Buildx descriptor source validation**:
    - Command: `docker buildx build . -f langchain.yaml --output type=cacheonly`
    - Record build output proving descriptor syntax validity.
  - **Layer 4: Docker Buildx OCI layout export**:
    - Command: `docker buildx build . -f langchain.yaml -t langchain:1.4.4 --output type=oci,dest=/tmp/langchain-layout,tar=false`
    - Record export logs and index.json inspection.
  - **Layer 5: kit-tck layout conformance verification**:
    - Command: `kit-tck validate --layout /tmp/langchain-layout 1.4.4`
    - Record conformance checks passing with zero errors.
  - **Layer 6: Assembled SBX runtime execution**:
    - Explicitly document limitation ESC-001 (nested sbx CLI not installed).
    - Provide exact host commands for optional human handoff:
      `sbx run ./sample --kit ../` and `sbx env run`.
    - Mark as optional HUMAN handoff; do not claim automated pass.
  - **Layer 7: Editorial audience review**:
    - Record transcript from Step 12.
- **Observable Done Condition**:
  - `docs/verification-report.md` documents all layers with exact commands and raw sanitized outputs.

### Step 11: Enterprise User Guide, Marketing Brief & Blog Outline
- **Assigned Role**: Implementer
- **Files**:
  - `docs/user-guide.md`
  - `docs/marketing-brief.md`
  - `docs/blog-outline.md`
- **Content Requirements**:
  - Use ACR `blog-writer` scoped non-blog route (`scoped-edit.md`).
  - Maintain objective, neutral technical voice: no invented personal experiences or corporate posturing.
  - Ground all claims in build and test evidence from this repository.
  - `user-guide.md`: Enterprise audience, architecture, prerequisites, clean-checkout steps, deterministic testing, opt-in Gemini provider, failure cases, limitations.
  - `marketing-brief.md`: Value proposition of Docker Sandboxes v3 kits for enterprise LLM orchestration, security isolation, reproducibility.
  - `blog-outline.md`: Structured narrative outline for an enterprise engineering blog post, explicitly leaving author persona selection gates pending.
- **Observable Done Condition**:
  - All 3 documents exist with rigorous content grounded in actual repository deliverables.

### Step 12: Fresh Stateless Gemini Audience Review
- **Assigned Role**: Implementer
- **Files**:
  - `docs/gemini-audience-review.md`
- **Execution Details**:
  1. Prepare stateless review packet containing only `docs/user-guide.md` and reader prerequisites (no source trees, no private plans).
  2. Execute review using `fresh-reader.py`:
     `python3 .codex/skills/acr__shelajev__blog-writer__blog-writer/fresh-reader.py docs/user-guide.md --audience "Enterprise AI Platform Engineers" --output docs/gemini-audience-review.md`
  3. Inspect findings for clarity, technical prerequisites, or missing details.
  4. Implement improvements in `docs/user-guide.md`.
  5. Rerun review to confirm reader comprehension, or record honest findings if network/service limits apply.
- **Observable Done Condition**:
  - `docs/gemini-audience-review.md` records audience feedback and remediation notes.

### Step 13: Final Repository Cleanliness, Commit & QC Handoff
- **Assigned Role**: Implementer
- **Actions**:
  1. Remove transient build artifacts and caches (`/tmp/langchain-layout`, `.pytest_cache`, `__pycache__`).
  2. Verify working directory contains no uncommitted temporary files or secrets.
  3. Commit all deliverables on `feat/langchain-enterprise-kit`.
  4. Ensure working tree is completely clean (`git status` clean porcelain).
  5. Update `/home/agent/crew/status.md` with commit ID and pass off to QC.
- **Observable Done Condition**:
  - `git status` shows clean working tree.
  - Final commit ID recorded.

---

## Acceptance Criteria Checklist
- [ ] Dedicated working branch `feat/langchain-enterprise-kit` used for all commits.
- [ ] Implementer copies `plan.md` into repository at `docs/implementation-plan.md` as the first repository edit.
- [ ] Pinned `create-kit-v3` skill sources and reference `sbxenv.yaml` archived under `docs/references/`.
- [ ] ACR 0.2.1 realized with pinned `shelajev/blog-writer`; `agents.yaml` and `.agents/registry.lock` tracked.
- [ ] Synthetic policy dataset (4 policies) authored with structured sections and explicit thresholds.
- [ ] Enterprise LangChain sample implemented using pinned dependencies (`langchain==1.4.4`), LCEL, citation retrieval, and bounded tools.
- [ ] Credential-free `DeterministicFakeChatModel` enabled by default; live Gemini provider opt-in via proxy.
- [ ] 100% passing Python behavioral test suite (`pytest`) covering grounded and unsupported queries.
- [ ] Docker Sandboxes v3 kit descriptor (`langchain.yaml`) and portable multi-stage recipe (`langchain.dockerfile`) with bundled Python interpreter.
- [ ] Valid sample `sbxenv.yaml` conforming to official schemaVersion "1" grammar with honest provenance.
- [ ] Real GitHub Actions workflow (`.github/workflows/ci.yml`) on `ubuntu-latest` running all automated checks without silent skips.
- [ ] Docker Buildx descriptor source validation passes (`type=cacheonly`).
- [ ] Docker Buildx OCI layout export passes.
- [ ] `kit-tck validate --layout` passes with zero errors.
- [ ] ESC-001 documented honestly: Layer 6 assembled SBX run is an optional HUMAN handoff, not an automated pass.
- [ ] User guide, marketing brief, and blog outline authored via scoped non-blog route with neutral identity.
- [ ] Fresh stateless Gemini audience review executed and recorded in `docs/gemini-audience-review.md`.
- [ ] No git push, no image publishing, no secrets committed, clean porcelain ready for independent QC.
