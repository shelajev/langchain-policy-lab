# Verification report

Historical policy-lab results. Current bring-your-own-app evidence and remaining
runtime gaps are in [the runtime matrix](evidence/runtime-matrix.md).

Date: 2026-10-09. All observed commands ran inside the task sandbox on Linux
arm64. No code ran on a host, no nested SBX daemon was started, and nothing was
pushed/published. ESC-001's earlier apparent passes were planning assertions;
only the evidence below establishes results. This report separates artifact,
sample and editorial checks from actual runtime policy checks.

## Status by layer

| Layer | Observed status | Evidence |
| --- | --- | --- |
| Descriptor source validation/content build | PASS | `evidence/source-build.txt` |
| OCI directory export | PASS, Linux arm64 | `evidence/oci-build.txt` |
| OCI kit-tck artifact conformance | PASS, 19/19 | `evidence/kit-tck.txt` |
| Python behavioral tests | PASS, 49 tests | `evidence/python-tests.txt` |
| Sample CLI/evaluation/provider import | PASS, fake/offline, 11 cases | `evidence/sample-script.txt` |
| Non-SBX filesystem dependency probe | PASS, Debian arm64, no system Python | `evidence/filesystem-probe.txt` |
| Clean-checkout journey | PASS at base `6bd0119`; executable inputs unchanged at finalization | `evidence/clean-checkout-base.txt` |
| ACR realization | PASS with GH_TOKEN removed from command environment | `evidence/tool-versions.txt` |
| SBX grammar provenance | Official v0.47.0 help observed; NOT daemon validation | `evidence/sbx-help.txt` |
| Editorial stateless Gemini review | READABLE, review 07; optional suggestion retained | `reviews/gemini-07.md`, `editorial-process.md` |
| Live sample model-provider validation | NOT RUN | Optional explicitly approved API use |
| Assembled SBX composition/policy checks | NOT RUN, optional HUMAN handoff | No daemon/host execution authorized |
| Hosted GitHub Actions | Authored, NOT RUN | Local scripts are checked separately |

## Tools and inputs

`evidence/tool-versions.txt` records actual tool output: Docker client/server
29.4.3, Buildx 0.33.0, Python 3.13.7, uv 0.9.26, ACR 0.2.1, and kit-tck
`dev (a1d110de)`. The shell's Go is 1.24.4; the checker binary is built by
downloaded Go 1.26.8. The official CLI is sbx v0.47.0 at source
`0411f50ee4700fe7bd37e6e7e3aced563e850ca9`. Exact upstream URLs, digests,
release metadata and API-source hashes are in `provenance.md` and `evidence/`.

The tool-version capture ran:

```bash
uv --version
python3 --version
docker version --format 'Client {{.Client.Version}} Server {{.Server.Version}}'
docker buildx version
docker info --format '{{.OSType}}/{{.Architecture}}'
kit-tck version
/tmp/langchain-ci-tools/kit-tck version
go version
go version -m /tmp/langchain-ci-tools/kit-tck
acr version
env -u GH_TOKEN acr check
/tmp/sbx-help/docker-sbx/sbx version
sha256sum /tmp/sbx-v0.47.0-arm64.tar.gz
```

## Descriptor, content build and OCI checks

Exact initial successful commands at the repository root:

```bash
docker buildx build . -f langchain.yaml --output type=cacheonly
docker buildx build . -f langchain.yaml -t langchain:1.4.4 --output type=oci,dest=/tmp/langchain-layout,tar=false
kit-tck validate --verbose --layout /tmp/langchain-layout 1.4.4
```

Exit statuses: all 0. `cacheonly` suppresses export, **not** recipe execution.
The frontend strictly validates source and builds the content. The OCI layout
manifest is `sha256:65dfd662db0ea54d39340eafd417a7dfb65611c27dd099805065fc34d37653a3`,
platform `linux/arm64`; config is
`sha256:7f2872e861a7bf60950db3f4a2b246006de8e55841a3d9bfc8b15354619b1ca1`.
kit-tck reported `19 checks · 19 passed` and `conforms`. It also checked
overlay link resolution and staged sources/context. No runtime composition
or policy-enforcement conclusion follows from that report.

Recipe enforcement verifies installed `langchain==1.4.4`, imports SSL/sqlite
and the optional provider, and ships interpreter plus environment in the
same prefix. The mixin owns no launch/user/workdir fields and requests only
agent context. `scripts/check-kit.sh` is the reproducible combined command;
its separately recorded run appears in the final update.

## Python behavior and installed runtime

Exact test command:

```bash
cd sample
uv run --locked pytest -v
```

Observed exit 0, `49 passed in 0.10s`. Tests remove provider keys and patch
socket connects to fail. They exercise six grounded/five unsupported questions,
actual retriever rank/citation metadata, updated corpus content, strict numeric
boundaries/extra arguments, missing data, bad model JSON, duplicate/unknown
citations, sanitized exceptions, provider approval gating and CLI exit status.
The suite uses no live model.

The broader journey was then run from the root:

```bash
bash scripts/check-sample.sh
```

Observed exit 0. It installs from `uv.lock`, runs the suite and 11-case
evaluation, prints a cited `$90` passage, refuses the pet question, calculates
`total_usd: 270`, checks `receipt_required: true` at $25 and imports Gemini
4.4.0. Importing the provider is **not** validating its model endpoint, API key,
SDK request behavior or answer quality.

The installed API inspection command was:

```bash
cd sample
uv run --locked --extra gemini python ../scripts/record-api-provenance.py
```

Observed exit 0; output saved as `evidence/api-provenance.json`. It reads
installed distribution sources and provider fields without constructing or
calling a live model. Primary PyPI snapshots came from
`curl -fsSL https://pypi.org/pypi/<name>/<pin>/json` with selected public
metadata recorded in `evidence/pypi-*.json`.

Exact runtime probe:

```bash
bash scripts/check-filesystem.sh
```

Observed exit 0. It loads the mixin locally, copies its prefix onto the
digest-pinned Debian bookworm base, manually adds PATH, asserts system Python
is absent, prints Python/ldd, and executes the bundled 11-case evaluation with
`docker run --rm --network none --read-only --user 1000:1000`. This establishes
native arm64 Debian/glibc compatibility only. It does not merge SBX config or
test capabilities, workload launch, workspace mounts or policy enforcement.

## CI tooling creation and corrected failure

Exact command:

```bash
bash scripts/install-ci-tools.sh /tmp/langchain-ci-tools
```

The initial version failed with exit 1 because upstream `go install ...@commit`
rejects modules containing replace directives. `evidence/ci-install-initial-failure.txt`
preserves the observed diagnostic. The corrected script fetches the exact
official commit, checks HEAD, and uses Go 1.26.8 `go build -mod=readonly` from
that checkout. Re-execution exited 0; `evidence/ci-install.txt` records the
successful checksum check, commit and binary revision. Required failures are
not ignored or converted into skips.

The workflow has read-only repository permission, a pinned checkout action,
an official digest-pinned BuildKit container and a real Ubuntu runner. It runs
the scripts for sample behavior, source build, OCI/kit-tck, filesystem probe
and clean checkout. It never requests an SBX runtime. A local script pass is
not represented as an actual hosted Actions run.

## ACR/editorial and CLI help commands

Observed ACR commands:

```bash
env -u GH_TOKEN acr install github:shelajev/blog-writer@61844184d925b9f925951241a0d476db7c193e7e --agent codex --agent claude-code --non-interactive
env -u GH_TOKEN acr realize
env -u GH_TOKEN acr check
```

Install and realize succeeded, with `109 realization change(s)`; check reports
`Realization is current for claude-code, codex.` A check with inherited GH_TOKEN
failed `GitHub access denied: Bad credentials`; unsetting it for public-package
requests succeeded. No credential value was printed or stored. The package
pin and content hash are in `.agents/registry.lock`; generated skills are ignored.

CLI provenance acquisition, not runtime execution:

```bash
curl -fsSL https://api.github.com/repos/docker/sbx-releases/releases/latest
curl -fsSL https://github.com/docker/sbx-releases/releases/download/v0.47.0/DockerSandboxes-linux-arm64.tar.gz -o /tmp/sbx-v0.47.0-arm64.tar.gz
tar -xzf /tmp/sbx-v0.47.0-arm64.tar.gz -C /tmp/sbx-help docker-sbx/sbx docker-sbx/sbx-version.json
/tmp/sbx-help/docker-sbx/sbx version
/tmp/sbx-help/docker-sbx/sbx env --help
/tmp/sbx-help/docker-sbx/sbx env run --help
/tmp/sbx-help/docker-sbx/sbx env exec --help
/tmp/sbx-help/docker-sbx/sbx env rm --help
```

All help/version commands exited 0. No CLI daemon command was executed.
The original missing-CLI condition was overcome for help only; ESC-001 remains
an optional HUMAN runtime handoff, not a request to repair sandbox infrastructure.

## Unrun HUMAN checks and remaining boundaries

The guide contains verified command syntax for a human to inspect the environment
plan and run it with their already provisioned SBX daemon. That human should
check actual workload/mixin composition, additive PATH, interpreter use, source
citations and denied-network behavior under approved organization policy.
No host daemon/bridge, extra kit or secret is requested here. Runtime/policy
checks are explicitly optional, not acceptance blockers for these deliverables.

Live sample validation has not run: the provider needs independent explicit
approval, existing credentials and allowed endpoint routing. Gemini editorial
review, when performed, is separate and cannot stand in for that validation.
Independent crew QC is pending; implementation cannot self-declare its verdict.

## Final update

Resumed finalization preserved the observed clean-checkout output for full base
`6bd01195855214624f11b565e182cc59a342eb75` in
`evidence/clean-checkout-base.txt`. It reports 49 passing tests, the 11-case
evaluation and the complete CLI journey with an isolated cache/interpreter.
This is recovered evidence, not a fresh execution at the final delivery tip.

The interrupted alias-only changes to the Dockerfile and sample check script
were discarded. All executable, descriptor, dependency, sample and workflow
inputs remain byte-identical to the verified base. Consequently source/OCI,
19/19 kit-tck, Debian filesystem and sample results remain applicable to those
recorded inputs; no redundant rebuild or runtime launch was performed.

README/guide definition additions are retained. The exact review-07 packet is
now repository-local; all four artifact sections match the final prose. Both
changed artifacts' final scanner JSON outputs match a resumed scanner rerun:
zero required hits, raw exit 1 for contextual hits retained with dispositions.
Review 07 is READABLE. Its PATH-directory consistency suggestion is advisory;
the supplied commands already use the same directory. No further reader call
was needed because the reviewed prose did not change.

`final-delivery.md` and `evidence/finalization-delta-check.txt` record the narrow
checks and handoff. Independent Claude QC remains pending at this commit.
SBX composition/policy, hosted Actions and live sample-provider validation
remain unrun; none is inferred from the artifact or editorial passes.
