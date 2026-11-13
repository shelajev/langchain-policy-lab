# Single-file LangChain app

The primary example for
[Run your LangChain app in Docker Sandboxes](../../docs/run-your-langchain-in-docker-sandboxes.md).
`agent.py` classifies one synthetic support ticket with Gemini
(`gemini-2.5-flash` through `langchain-google-genai`). With `--fake-model` it
uses LangChain's `FakeListChatModel`, needs no key and prints:

```json
{"category":"technical","ticket_id":"T-101"}
```

This directory already has the project files the skill requires:
`pyproject.toml` with exact direct pins, a hashed `uv.lock` and
`.python-version`. The kit generated from it, with the
[reviewed answers](../single-file-agent.answers.json), is committed in
[../single-file-agent-kit/](../single-file-agent-kit/RUN.md) so you can
compare your own output with it.

## Starting from just agent.py and requirements.txt

The guide starts from the [raw version](../../skills/langchain-sandbox-kit/tests/fixtures/raw-agent/)
of the same app, which has only `agent.py` and `requirements.txt`. With uv
0.9.26, in a copy of that directory:

```bash
uv init --bare --no-workspace --name single-file-agent --python 3.13.7
uv python pin 3.13.7
uv add --no-sync 'langchain==1.4.4' 'langchain-core==1.6.9' 'langchain-google-genai==4.4.0'
uv lock
```

These commands add `pyproject.toml`, `.python-version` and `uv.lock` and leave
`agent.py` unchanged. A fresh `uv lock` can pick newer transitive versions than
the lock committed here; both work. See
[dependency setup](../../skills/langchain-sandbox-kit/references/dependencies.md).
