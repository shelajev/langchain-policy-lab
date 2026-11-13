#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root"
uv run --no-project --python 3.13.7 python -m unittest discover -s skills/langchain-sandbox-kit/tests -v
