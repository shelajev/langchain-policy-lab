# Single-file LangChain app

This is the primary example for
[Run your LangChain app in Docker Sandboxes](../../docs/run-your-langchain-in-docker-sandboxes.md).
`agent.py` classifies one synthetic support ticket with Gemini
(`gemini-2.5-flash` through `langchain-google-genai`), and has two run modes:

- **Offline mode (`--fake-model`):** uses LangChain's `FakeListChatModel`,
  requires no API key or network access, and deterministically prints:

```json
{"category":"technical","ticket_id":"T-101"}
```

- **Live mode (no `--fake-model`):** sends the ticket to Gemini. Inside a
  sandbox, this uses a runtime `google` credential stored via `sbx secret set`
  and an allowed outbound host request, separate from whatever model or account
  runs your coding agent.

This directory already has the project files the skill requires:
`pyproject.toml` with exact direct pins, a hashed `uv.lock` and
`.python-version`. The kit generated from it, with the
[reviewed answers](../single-file-agent.answers.json), is committed in
[../single-file-agent-kit/](../single-file-agent-kit/RUN.md) so you can
compare the layout with a built reference. This source directory has no
`requirements.txt`, so its committed kit has eight inspection findings. The
tutorial retains `requirements.txt` while adding `pyproject.toml`, producing
12 findings (including repeated provider evidence); the two outputs are not
expected to have identical IDs, reasons or names.

## Starting from just agent.py and requirements.txt

To reflect a typical starting point, the main guide begins from the
[raw version](../../skills/langchain-sandbox-kit/tests/fixtures/raw-agent/) of
the same app, which has only `agent.py` and `requirements.txt`. With uv
0.9.26, run these commands on the host inside a copy of that `raw-agent`
directory:

```bash
uv init --bare --no-workspace --name single-file-agent --python 3.13.7
uv python pin 3.13.7
uv add --no-sync 'langchain==1.4.4' 'langchain-core==1.6.9' 'langchain-google-genai==4.4.0'
uv lock
```

These commands create `pyproject.toml`, `.python-version` and `uv.lock` while
leaving `agent.py` unchanged. A fresh `uv lock` can pick newer transitive
versions than the lock committed here. Only the committed lock has been built
and verified by this repository's checks. For your own fresh lock, rebuild
your generated kit and repeat the tutorial's offline run before a live call.
If you change the committed example in a fork, also run the repository checks,
which target those committed fixtures rather than your separate `my-agent` directory. See
[dependency setup](../../skills/langchain-sandbox-kit/references/dependencies.md).
