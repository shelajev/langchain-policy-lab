# single-file-agent-kit

The reviewed app is installed inside this sandbox at /opt/single-file-agent-kit/app with its own locked Python environment.
Run it from a shell inside this sandbox:

    cd /opt/single-file-agent-kit/app && /opt/single-file-agent-kit/venv/bin/python agent.py

Use the app's virtual-environment interpreter path shown above; plain `python` runs the `shell` workload's system Python without the app's dependencies.
