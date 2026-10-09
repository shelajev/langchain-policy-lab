#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root"
docker buildx build . -f langchain.yaml --progress plain -t langchain:filesystem --load
docker build --progress plain -t langchain:filesystem-probe -f scripts/filesystem-probe.dockerfile .
docker run --rm --network none --read-only --user 1000:1000 langchain:filesystem-probe sh -eu -c '
  test ! -e /usr/bin/python3
  /opt/langchain/venv/bin/python --version
  ldd /opt/langchain/venv/bin/python
  /opt/langchain/venv/bin/python -m langchain_enterprise.cli --policies /opt/langchain/sample/data/policies --eval-suite
'
