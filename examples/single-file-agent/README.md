# Existing agent.py, unchanged layout

This is the smallest supported project: a root `agent.py`, project dependencies,
exact Python version and a frozen lock. No `src/` migration or Sandbox API is
required. Ask the skill to inspect `agent.py`, answer its resource questions,
and choose `python agent.py --fake-model` as the initial launch command.

If your own app has only a requirements file, keep the source unchanged, review
its dependencies and build configuration, create a normal `pyproject.toml` with
the intended exact dependency pins and `.python-version`, then run `uv lock`
in an approved development environment. This is ordinary project setup, not
permission for the helper to execute source or grant runtime capabilities.

The [larger ticket-triage example](../ticket-triage/) exercises dynamic endpoints,
declared data paths and the fully worked answers/kit. This file is a second raw
app for forward testing; no additional live model call is needed.
