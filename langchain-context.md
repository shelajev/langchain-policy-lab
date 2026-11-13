# LangChain policy lab

This mixin ships CPython 3.13.7, LangChain 1.4.4 and the synthetic policy sample.
Use `/opt/langchain/venv/bin/python -m langchain_enterprise.cli --policies /opt/langchain/sample/data/policies --eval-suite`.
The default model is an extractive fake, not a live LLM. Citations identify source,
section and chunk. Read-only meal and receipt tools accept bounded typed inputs.
Do not treat the synthetic rules as real company policy or production security.
No network, credentials, host sharing, privilege or lifecycle hooks are requested.
Live Gemini requires separate human-approved network/credential grants and explicit
`--provider gemini --approve-live`; never add grants or print credentials yourself.
The runtime is a glibc Linux overlay, not an Alpine/musl or arbitrary minimal-base claim.
