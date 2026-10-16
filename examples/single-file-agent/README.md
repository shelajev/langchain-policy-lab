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
app for forward testing; no additional live model call is needed. The committed
[kit template](../single-file-agent-kit/) and [reviewed answers](../single-file-agent.answers.json)
request only the Gemini host and runtime credential. Its context uses
`python agent.py`; the offline container check adds `--fake-model` instead.

## Starting with just agent.py and requirements.txt

The [raw fixture](../../skills/langchain-sandbox-kit/tests/fixtures/raw-agent/)
has no lock or project metadata. With uv 0.9.26, in a copy of that directory,
after reviewing the requirements and choosing these exact example versions:

```bash
uv init --bare --no-workspace --name single-file-agent --python 3.13.7
uv python pin 3.13.7
uv add --no-sync 'langchain==1.4.4' 'langchain-core==1.6.9' 'langchain-google-genai==4.4.0'
uv lock
```

Only `pyproject.toml`, `.python-version` and `uv.lock` are added. The script is
unchanged and never executed by this setup. Review the lock and adapt version
choices to your app; hashed requirements also need conversion to this supported
uv form. See [dependency setup](../../skills/langchain-sandbox-kit/references/dependencies.md).
