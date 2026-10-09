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
test -z "$(git -C "$temporary/checkout" status --porcelain)"
printf '%s\n' 'Clean-checkout journey passed with isolated dependency cache and managed interpreter.'
