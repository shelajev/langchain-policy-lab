# ticket-triage-kit

The reviewed app is installed inside this sandbox at /opt/ticket-triage-kit/app with its own locked Python environment.
Run it from a shell inside this sandbox:

    cd /opt/ticket-triage-kit/app && /opt/ticket-triage-kit/venv/bin/python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model

Use the app's virtual-environment interpreter path shown above; plain `python` runs the `shell` workload's system Python without the app's dependencies.
