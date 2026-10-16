#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root"
temporary=$(mktemp -d)
trap 'rm -rf "$temporary"' EXIT
printf '%s\n' 'Evidence class: single-file source/build/TCK/container; NOT SBX runtime confinement proof.'
python3 skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py explain --manifest examples/single-file-agent-kit/kit-manifest.json
docker buildx build examples/single-file-agent-kit -f examples/single-file-agent-kit/single-file.yaml --progress plain --output type=cacheonly
docker buildx build examples/single-file-agent-kit -f examples/single-file-agent-kit/single-file.yaml --progress plain -t single-file:0.1.0 --output "type=oci,dest=$temporary/layout,tar=false"
kit-tck validate --verbose --layout "$temporary/layout" 0.1.0
docker buildx build examples/single-file-agent-kit -f examples/single-file-agent-kit/single-file.yaml --progress plain -t single-file:probe-overlay --load
docker build -t single-file:probe -f scripts/single-file-probe.dockerfile .
bash scripts/check-single-file-container.sh
