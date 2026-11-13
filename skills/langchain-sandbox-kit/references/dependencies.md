# From a raw script to a reviewed lock

Start with your unchanged `agent.py` and `requirements.txt`. Read both as data;
review dependency names and any existing project config or build backend before
using tooling. Do not run the app. The helper accepts a uv project, not
requirements-only input (even hashed requirements need this conversion).

For the bundled raw fixture, the developer selects Python 3.13.7 and the exact
direct versions below. These are example choices, not automatic upgrades for
your app. Confirm compatible versions for your own requirements first.
With uv 0.9.26, run these commands **inside the raw app directory**:

```bash
uv init --bare --no-workspace --name single-file-agent --python 3.13.7
uv python pin 3.13.7
uv add --no-sync 'langchain==1.4.4' 'langchain-core==1.6.9' 'langchain-google-genai==4.4.0'
uv lock
```

This creates only `pyproject.toml`, `.python-version` and `uv.lock`. It neither
restructures nor runs `agent.py`, and creates no virtual environment. The bare
project has no build system and uv treats it as a non-package. Review the exact
direct pins, resolved transitive versions, public PyPI sources and artifact
hashes in `uv.lock` before generating packaging. Do not add your `.env` to the
snapshot. Keep dependency resolution separate from the deterministic helper.

The network-using regression is `bash scripts/check-raw-single-file.sh` from
the repository root. It checks byte-identical source and an excluded test-only
`.env`, then generates and builds a sanitized kit. It is not a live model or
SBX runtime test.
