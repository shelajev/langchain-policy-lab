#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
layout="${1:?Pass a fresh OCI layout directory}"
cd "$root"
test ! -e "$layout"
docker buildx version
kit-tck version
docker buildx build . -f langchain.yaml --progress plain --output type=cacheonly
docker buildx build . -f langchain.yaml --progress plain -t langchain:1.4.4 --output "type=oci,dest=$layout,tar=false"
kit-tck validate --verbose --layout "$layout" 1.4.4
