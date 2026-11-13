#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
layout="${1:?Pass a fresh OCI layout directory}"
test ! -e "$layout"
cd "$root"
printf '%s\n' 'Evidence class: source/build/TCK/container; NOT SBX runtime confinement proof.'
python3 skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py explain --manifest examples/ticket-triage-kit/kit-manifest.json
docker buildx build examples/ticket-triage-kit -f examples/ticket-triage-kit/ticket-triage-kit.yaml --progress plain --output type=cacheonly
docker buildx build examples/ticket-triage-kit -f examples/ticket-triage-kit/ticket-triage-kit.yaml --progress plain -t ticket-triage-kit:0.1.0 --output "type=oci,dest=$layout,tar=false"
kit-tck validate --verbose --layout "$layout" 0.1.0
docker buildx build examples/ticket-triage-kit -f examples/ticket-triage-kit/ticket-triage-kit.yaml --progress plain -t ticket-triage-kit:probe-overlay --load
docker build -t ticket-triage-kit:probe -f scripts/generated-probe.dockerfile .
bash scripts/check-generated-container.sh
