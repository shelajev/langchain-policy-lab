#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
temporary=$(mktemp -d)
trap 'rm -rf "$temporary"' EXIT
git clone --no-local "$root" "$temporary/checkout"
git -C "$temporary/checkout" rev-parse HEAD
export UV_CACHE_DIR="$temporary/uv-cache"
export UV_PYTHON_INSTALL_DIR="$temporary/python"
export UV_PYTHON_PREFERENCE=only-managed
export UV_LINK_MODE=copy
uv python install --no-bin 3.13.7
bash "$temporary/checkout/scripts/check-sample.sh"
bash "$temporary/checkout/scripts/check-example.sh"
bash "$temporary/checkout/scripts/check-skill.sh"
python3 "$temporary/checkout/scripts/check-doc-links.py"
if command -v docker >/dev/null && command -v kit-tck >/dev/null; then
  bash "$temporary/checkout/scripts/check-kit.sh" "$temporary/policy-layout"
  bash "$temporary/checkout/scripts/check-filesystem.sh"
  bash "$temporary/checkout/scripts/check-generated-kit.sh" "$temporary/generated-layout"
  bash "$temporary/checkout/scripts/check-single-file.sh"
else
  printf '%s\n' 'NOT RUN: kit build/TCK/container scripts require docker and kit-tck on PATH.'
  exit 1
fi
test -z "$(git -C "$temporary/checkout" status --porcelain)"
printf '%s\n' 'Clean-checkout journey passed with isolated dependency cache and managed interpreter.'
