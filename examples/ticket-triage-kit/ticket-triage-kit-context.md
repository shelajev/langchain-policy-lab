# ticket-triage-kit

The reviewed app is installed at /opt/ticket-triage-kit/app with its own locked Python environment.
Run it from a shell in this sandbox:

    cd /opt/ticket-triage-kit/app && /opt/ticket-triage-kit/venv/bin/python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model

Use the app's own interpreter path shown above; plain `python` is the workload's system Python without the app's dependencies.
