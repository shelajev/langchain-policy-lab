#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' 'Evidence class: container composition probe (shell workload image + kit overlay); NOT SBX runtime confinement proof.'
docker run --rm --network none --read-only --tmpfs /tmp --user 1000:1000 -e PYTHONDONTWRITEBYTECODE=1 --entrypoint sh ticket-triage-kit:probe -eu -c '
  cd /opt/ticket-triage-kit/app
  /opt/ticket-triage-kit/venv/bin/python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model
  test -z "$(find /opt/ticket-triage-kit -name .env -o -name private -o -name id_rsa)"
  if grep -r -l TEST_ONLY_PRIVATE_CANARY_4728c2bd /opt/ticket-triage-kit; then exit 1; fi
  set +e
  result=$(TRIAGE_STATUS_URL=https://example.com /opt/ticket-triage-kit/venv/bin/python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model --status 2>&1)
  status=$?
  set -e
  test "$status" -eq 2
  printf "%s\n" "$result" | grep -q "triage failed: check input, configuration and network policy"
  printf "%s\n" "PASS: fake app on shell workload, sanitized filesystem, clean network-none failure; not SBX policy proof."
'
