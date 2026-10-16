#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' 'Evidence class: container only; NOT SBX runtime confinement proof.'
docker run --rm --network none --read-only --user 1000:1000 -e PYTHONDONTWRITEBYTECODE=1 ticket-triage:probe sh -eu -c '
  cd /opt/ticket-triage/app
  python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model
  test -z "$(find /opt/ticket-triage -name .env -o -name private -o -name id_rsa)"
  if grep -r -l TEST_ONLY_PRIVATE_CANARY_4728c2bd /opt/ticket-triage; then exit 1; fi
  set +e
  result=$(TRIAGE_STATUS_URL=https://example.com python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model --status 2>&1)
  status=$?
  set -e
  test "$status" -eq 2
  printf "%s\n" "$result" | grep -q "triage failed: check input, configuration and network policy"
  printf "%s\n" "PASS: fake app, sanitized filesystem, clean network-none failure; not SBX policy proof."
'
