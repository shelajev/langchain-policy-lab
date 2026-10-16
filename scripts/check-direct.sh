#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
temporary=$(mktemp -d)
trap 'rm -rf "$temporary"' EXIT
printf '%s\n' 'Evidence class: raw source/lock and ordinary shell-image container; NOT local/cloud SBX confinement.'
bash "$root/scripts/check-raw-single-file.sh" --direct-out "$temporary/direct"
cmp "$root/skills/langchain-sandbox-kit/tests/fixtures/raw-agent/agent.py" "$temporary/direct/workspace/agent.py"
test ! -e "$temporary/direct/workspace/.env"
test ! -e "$temporary/direct/workspace/private"
if grep -r -l TEST_ONLY_PRIVATE_CANARY_4728c2bd "$temporary/direct"; then exit 1; fi
docker buildx build "$temporary/direct" -f "$root/scripts/direct-probe.dockerfile" --load -t langchain-direct:probe --progress plain
docker run --rm --network none --read-only --user 1000:1000 --mount "type=bind,src=$temporary/direct/workspace,dst=/workspace,readonly" langchain-direct:probe -eu -c '
  python agent.py --fake-model
  test ! -e .env
  test ! -e private
  test -f agent.py
  printf "%s\n" "PASS: unchanged app in pinned shell-image container, read-only snapshot, uid1000, no network."
'
mkdir -p "$temporary/manual/workspace"
cp "$root/skills/langchain-sandbox-kit/tests/fixtures/raw-agent/agent.py" "$temporary/manual/workspace/"
cp "$temporary/direct/workspace/pyproject.toml" "$temporary/direct/workspace/uv.lock" "$temporary/direct/workspace/.python-version" "$temporary/manual/workspace/"
cp "$root/skills/langchain-sandbox-kit/templates/direct-setup.txt" "$temporary/manual/setup-deps.sh"
cmp "$temporary/manual/workspace/agent.py" "$temporary/direct/workspace/agent.py"
docker run --rm --network none --read-only --user 1000:1000 --mount "type=bind,src=$temporary/manual/workspace,dst=/workspace,readonly" langchain-direct:probe -eu -c 'python agent.py --fake-model; test ! -e .env; test ! -e private'
printf '%s\n' 'PASS: manual allowlisted snapshot of original raw source plus reviewed lock metadata, ordinary container only.'
if docker run --rm --network none --read-only langchain-direct:probe -c "python -c \"import socket; socket.create_connection(('192.0.2.1', 443), timeout=3)\""; then
  echo 'FAIL: negative network control unexpectedly connected' >&2
  exit 1
fi
printf '%s\n' 'PASS: ordinary container network-none negative control failed as expected; not SBX policy evidence.'
