#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root/sample"
unset GEMINI_API_KEY GOOGLE_API_KEY LANGSMITH_API_KEY LANGCHAIN_API_KEY LANGSMITH_TRACING LANGCHAIN_TRACING_V2
uv sync --locked --all-extras
uv run --locked --offline pytest -v
uv run --locked --offline python -m langchain_enterprise.cli --eval-suite
uv run --locked --offline python -m langchain_enterprise.cli --query 'What is the Tier 1 meal allowance?'
uv run --locked --offline python -m langchain_enterprise.cli --query 'Can I bring my pet python into the office?'
uv run --locked --offline python -m langchain_enterprise.cli --tool meal --city-tier 1 --days 3
uv run --locked --offline python -m langchain_enterprise.cli --tool receipt --amount 25
uv run --locked --offline python -c 'import importlib.metadata as m; import langchain_google_genai; assert m.version("langchain") == "1.4.4"; assert m.version("langchain-google-genai") == "4.4.0"; print("Pinned core and optional provider imports verified; no live calls")'
