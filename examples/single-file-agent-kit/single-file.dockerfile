FROM ghcr.io/astral-sh/uv:0.9.26-bookworm-slim@sha256:85c530098e4db6143cf1b63d1634a9150210a3f98690b3eb6e9fa6515bc60954 AS build
ENV UV_PYTHON_INSTALL_DIR=/opt/single-file/python
ENV UV_PROJECT_ENVIRONMENT=/opt/single-file/venv
ENV UV_LINK_MODE=copy
WORKDIR /opt/single-file/app
COPY app/ ./
RUN uv python install --no-bin 3.13.7 && uv sync --locked --no-dev --no-editable --python 3.13.7 --managed-python
RUN chown -R 0:0 /opt/single-file

FROM scratch
COPY --from=build /opt/single-file /opt/single-file
ENV PATH="/opt/single-file/venv/bin"
