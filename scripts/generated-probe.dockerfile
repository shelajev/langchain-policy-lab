# Composition probe: the pinned shell workload (same digest as the kit's documented agent) plus this kit's
# overlay, with the mixin PATH appended after the workload's PATH as kit composition does.
FROM ticket-triage-kit:probe-overlay AS overlay
FROM docker/sbx-kit-shell:1.0.0@sha256:367c9a4b3fd550f777e1d57cc53550afb4a1385055d79111acf6f996272ff6de
COPY --from=overlay /opt/ticket-triage-kit /opt/ticket-triage-kit
ENV PATH="${PATH}:/opt/ticket-triage-kit/venv/bin"
