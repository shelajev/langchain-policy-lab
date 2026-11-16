# LangChain policy lab

This guest context applies inside the sandbox to the supporting policy-QA sample
(`sample/`, separate from the `single-file-agent` learning path).

This mixin ships CPython 3.13.7, LangChain 1.4.4 and the synthetic policy sample
as a glibc Linux overlay (not an Alpine/musl or arbitrary minimal-base claim).
To run the offline evaluation suite inside the sandbox guest, use
`/opt/langchain/venv/bin/python -m langchain_enterprise.cli --policies /opt/langchain/sample/data/policies --eval-suite`.

The sample uses a token-overlap retriever (no vector database) and an extractive
fake model by default, not a live LLM. Citations identify source, section and
chunk. Read-only meal and receipt tools accept bounded typed inputs.

Access boundaries and limits:

- Do not treat the synthetic rules as real company policy or production security.
- No network, credentials, host sharing, privilege or lifecycle hooks are
  requested by this mixin. Note that requesting no grants here does not make an
  effective composed sandbox policy exclusive if other grants are present, while
  explicit denies win.
- Live Gemini mode is separate from any coding-agent model or account, requires
  separate human-approved host network/credential grants and explicit
  `--provider gemini --approve-live`, and remains unrun in native/live sandbox
  checks. Never add grants or print credentials yourself.
