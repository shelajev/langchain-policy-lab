FROM ghcr.io/astral-sh/uv:0.9.26-bookworm-slim@sha256:85c530098e4db6143cf1b63d1634a9150210a3f98690b3eb6e9fa6515bc60954 AS build
ENV UV_PYTHON_INSTALL_DIR=/opt/single-file-agent-kit/python
ENV UV_PROJECT_ENVIRONMENT=/opt/single-file-agent-kit/venv
ENV UV_LINK_MODE=copy
ENV UV_EXCLUDE_NEWER=P7D
WORKDIR /opt/single-file-agent-kit/app
COPY app/ ./
RUN uv python install --no-bin 3.13.7 && uv sync --locked --no-dev --no-editable --python 3.13.7 --managed-python
RUN chown -R 0:0 /opt/single-file-agent-kit

FROM scratch
COPY --from=build /opt/single-file-agent-kit /opt/single-file-agent-kit
ENV PATH="/opt/single-file-agent-kit/venv/bin"
