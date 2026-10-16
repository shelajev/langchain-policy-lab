FROM ticket-triage:probe-overlay AS overlay
FROM debian:bookworm-slim@sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587
COPY --from=overlay /opt/ticket-triage /opt/ticket-triage
ENV PATH="/opt/ticket-triage/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
