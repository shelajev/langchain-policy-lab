# Source and dependency provenance

The learning path is [Run your LangChain app in Docker Sandboxes](run-your-langchain-in-docker-sandboxes.md).
The [validation summary](acceptance-handoff.md) records the native runtime
checks; the [docs-team handoff](docs-team-handoff.md) records readiness and
remaining publication decisions.

## Docker Sandboxes kit specification

The checked-in reference files under [references/](references/) come from
[Docker's sandbox-kit-spec](https://github.com/docker/sandbox-kit-spec) at
commit `a1d110de252bcc3cb2fa6d47fe37137a1a328b97`. Its Apache-2.0 license is
retained at [references/LICENSE](references/LICENSE).

The CI tool installer pins the official kit frontend, conformance checker,
uv and build tooling by version or digest. See
[scripts/install-ci-tools.sh](../scripts/install-ci-tools.sh) and the
[CI workflow](../.github/workflows/ci.yml) for the exact inputs.

## Python applications

The examples and policy-lab sample use exact direct dependency pins in their
`pyproject.toml` files and hashed public-PyPI artifacts in `uv.lock`. The
single-file example and generated kits retain a seven-day package-age limit.
The generator preserves a supplied application's source and declared data;
it does not execute source during inspection.

The policy-lab APIs used are LangChain runnable composition, chat models,
messages, documents and tools, with a FAISS retriever. The sample's offline
model is deterministic; offline behavior is not evidence of live model quality.
Use [scripts/record-api-provenance.py](../scripts/record-api-provenance.py) to
inspect installed API provenance inside the sample's environment.

The policy documents, tickets, incidents and example endpoints in this
repository are synthetic. No production credentials or customer records are
required by the offline examples.
