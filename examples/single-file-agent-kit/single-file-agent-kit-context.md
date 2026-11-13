# single-file-agent-kit

The reviewed app is installed at /opt/single-file-agent-kit/app with its own locked Python environment.
Run it from a shell in this sandbox:

    cd /opt/single-file-agent-kit/app && /opt/single-file-agent-kit/venv/bin/python agent.py

Use the app's own interpreter path shown above; plain `python` is the workload's system Python without the app's dependencies.
