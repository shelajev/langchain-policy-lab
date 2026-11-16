# From a raw script to a reviewed lock

Start with your unchanged `agent.py` and `requirements.txt`. Read both as data
first: review the dependency names and any existing project config or build
backend before running tooling, and do not execute the app. The helper requires
a `uv` project and refuses requirements-only input (even if `requirements.txt`
already contains hashes).

For the bundled raw single-file fixture, the developer selects Python 3.13.7 and
the exact direct versions below. Treat those as fixture-specific choices rather
than automatic versions or upgrades for your own app; confirm compatible pins
for your real requirements first. With `uv` 0.9.26, run these commands on the
coding agent's authorized environment, **inside the raw app directory**:

```bash
uv init --bare --no-workspace --name single-file-agent --python 3.13.7
uv python pin 3.13.7
uv add --no-sync 'langchain==1.4.4' 'langchain-core==1.6.9' 'langchain-google-genai==4.4.0'
uv lock
```

These commands are for a root-script project. A `src/` package also needs its
package metadata and build system so the app is installed into the environment;
keep an existing supported package setup rather than applying `uv init --bare`
blindly. The [ticket-triage project](../../../examples/ticket-triage/pyproject.toml)
shows the supported pinned build-system layout.

The expected outcome is three files (`pyproject.toml`, `.python-version`, and
`uv.lock`) with `agent.py` left untouched and no virtual environment created.
Using `--bare --no-workspace` avoids adding a build system, so `uv` treats the
directory as a non-package, and `--no-sync` skips local installation. Before
generating a kit, review the exact direct pins, resolved transitive versions,
public PyPI sources, and artifact hashes in `uv.lock` (do not assume a fresh
lock and an older lock behave identically without checking). Keep `.env` out of
the directory snapshot, and keep dependency resolution separate from the
deterministic kit helper.

To verify the raw-to-kit path locally, run `bash scripts/check-raw-single-file.sh`
**from the repository root** in an environment authorized for dependency
resolution and Docker builds. That regression script uses network
access to lock and build, verifies byte-identical `agent.py` preservation and an
excluded test-only `.env`, and generates and builds the reviewed kit. It does
not run a live model call or an `sbx` sandbox runtime test.
