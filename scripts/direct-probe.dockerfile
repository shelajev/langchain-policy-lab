FROM ghcr.io/astral-sh/uv:0.9.26-bookworm-slim@sha256:85c530098e4db6143cf1b63d1634a9150210a3f98690b3eb6e9fa6515bc60954 AS dependencies
ENV UV_PYTHON_INSTALL_DIR=/opt/direct/python
ENV UV_PROJECT_ENVIRONMENT=/opt/direct/venv
ENV UV_EXCLUDE_NEWER=P7D
ENV UV_LINK_MODE=copy
WORKDIR /opt/direct/project
COPY workspace/pyproject.toml workspace/uv.lock workspace/.python-version ./
RUN uv python install --no-bin 3.13.7 && uv sync --locked --no-dev --python 3.13.7 --managed-python

FROM docker/sbx-kit-shell:1.0.0@sha256:367c9a4b3fd550f777e1d57cc53550afb4a1385055d79111acf6f996272ff6de
COPY --from=dependencies /opt/direct /opt/direct
ENV PATH="/opt/direct/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ENV PYTHONDONTWRITEBYTECODE=1
USER 1000:1000
WORKDIR /workspace
ENTRYPOINT ["sh"]
