#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root/examples/ticket-triage"
unset GEMINI_API_KEY GOOGLE_API_KEY LANGSMITH_API_KEY LANGCHAIN_API_KEY LANGSMITH_TRACING LANGCHAIN_TRACING_V2
uv sync --locked
uv run --locked --offline pytest -v
uv run --locked --offline python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model
