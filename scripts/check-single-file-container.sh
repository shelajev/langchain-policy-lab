#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' 'Evidence class: container composition probe (shell workload image + kit overlay); NOT SBX runtime confinement proof.'
docker run --rm --network none --read-only --tmpfs /tmp --user 1000:1000 -e PYTHONDONTWRITEBYTECODE=1 --entrypoint sh single-file-agent-kit:probe -eu -c '
  cd /opt/single-file-agent-kit/app
  output=$(/opt/single-file-agent-kit/venv/bin/python agent.py --fake-model)
  printf "%s\n" "$output"
  printf "%s" "$output" | /opt/single-file-agent-kit/venv/bin/python -c "import json, sys; data = json.load(sys.stdin); assert data == {\"category\": \"technical\", \"ticket_id\": \"T-101\"}, data"
  if python -c "import langchain" 2>/dev/null; then echo "unexpected: workload python has app dependencies"; exit 1; fi
  test -z "$(find /opt/single-file-agent-kit -name .env -o -name private -o -name id_rsa)"
  if grep -r -l TEST_ONLY_PRIVATE_CANARY_4728c2bd /opt/single-file-agent-kit; then exit 1; fi
  printf "%s\n" "PASS: RUN.md command on shell workload, JSON category=technical ticket_id=T-101, plain python lacks app deps, sanitized filesystem, network-none/read-only/uid1000; not SBX policy proof."
'
