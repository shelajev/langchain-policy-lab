FROM ghcr.io/astral-sh/uv:0.9.26-bookworm-slim@sha256:85c530098e4db6143cf1b63d1634a9150210a3f98690b3eb6e9fa6515bc60954 AS build
ARG LANGCHAIN_VERSION=1.4.4
ENV UV_PYTHON_INSTALL_DIR=/opt/langchain/python
ENV UV_PROJECT_ENVIRONMENT=/opt/langchain/venv
ENV UV_LINK_MODE=copy
WORKDIR /opt/langchain/sample
COPY sample/pyproject.toml sample/uv.lock sample/.python-version ./
COPY sample/src ./src
COPY sample/data ./data
RUN uv python install --no-bin 3.13.7 && uv sync --locked --all-extras --no-dev --no-editable --python 3.13.7 --managed-python
RUN /opt/langchain/venv/bin/python -c "import importlib.metadata as m; assert m.version('langchain') == '${LANGCHAIN_VERSION}'; import ssl, sqlite3, langchain_google_genai" \
    && chown -R 0:0 /opt/langchain

FROM scratch
COPY --from=build /opt/langchain /opt/langchain
ENV PATH="/opt/langchain/venv/bin"
ENV LANGCHAIN_LAB_POLICIES="/opt/langchain/sample/data/policies"
