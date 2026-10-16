#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' 'Evidence class: container only; NOT SBX runtime confinement proof.'
docker run --rm --network none --read-only --user 1000:1000 -e PYTHONDONTWRITEBYTECODE=1 single-file:probe sh -eu -c '
  cd /opt/single-file/app
  python agent.py --fake-model
  test -z "$(find /opt/single-file -name .env -o -name private -o -name id_rsa)"
  if grep -r -l TEST_ONLY_PRIVATE_CANARY_4728c2bd /opt/single-file; then exit 1; fi
  printf "%s\n" "PASS: unchanged root script, sanitized filesystem, network-none/read-only/uid1000; not SBX policy proof."
'
