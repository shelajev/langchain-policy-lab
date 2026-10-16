# Manual path forward test — 2026-10-16

PASS, implementer rehearsal, not independent QC. The raw `agent.py` and
requirements fixture was copied to `/tmp/tmp.Tmvwa1JPle`, then the four uv
commands in [dependency setup](../../skills/langchain-sandbox-kit/references/dependencies.md)
were executed there with uv 0.9.26. Only project metadata, Python pin and lock
were added. `agent.py` SHA256 remained
`c930322fd3b6a4aed5fda913babaef015eeed0c32d4e3724f0d197dc8d2f9955`.
The automated raw-route check also passes: [log](raw-single-file.txt).

The [manual transcript](manual-path-forward.txt) records commands actually run,
not an inferred walkthrough. Three occurrences of the synthetic canary value
in command tracing are replaced with `[TEST CANARY REDACTED]`; this redaction
does not hide an app result, error or credential. No real credentials were used.

## Checklist executed without the helper

1. Copied `examples/single-file-agent-kit` to `/tmp/manual-agent-kit`, renamed
   its descriptor, Dockerfile and context to `manual-agent.*` names.
2. Replaced `app/` with only the raw fixture's unchanged script and its newly
   reviewed `pyproject.toml`, `uv.lock` and `.python-version`. The test-created
   `.env` was not copied; `cmp` checked source identity.
3. Edited `manual-agent.yaml` displayName/provides/context to `manual-agent`,
   retained kit version 0.1.0 and only Gemini's host/runtime credential, and
   explicitly denied `api.smith.langchain.com` because tracing is disabled.
4. Changed every Dockerfile `/opt/single-file` path to `/opt/manual-agent`.
   Python remained 3.13.7, matching the raw project's exact pin. `COPY app/ ./`
   needed no additional data COPY because this script reads no data files.
5. Updated the context allowlist entry, context launch to
   `cd /opt/manual-agent/app && python agent.py`, and both environment names.
   Kit path stayed `./`; only local retains `workspace: .`.
6. Rewrote `PERMISSIONS.md` for the actual host, credential, tracing, source,
   model and launch decisions; deleted the stale `kit-manifest.json`.
   No `generate`, `explain` or `--force` was used on the manual copy.
7. Executed the article/guide's cacheonly build, OCI export and TCK commands:

```bash
docker buildx build . -f manual-agent.yaml --progress plain --output type=cacheonly
docker buildx build . -f manual-agent.yaml --progress plain -t manual-agent:0.1.0 --output type=oci,dest=/tmp/manual-agent-layout,tar=false
kit-tck validate --verbose --layout /tmp/manual-agent-layout 0.1.0
```

8. Executed the guide's overlay load, pinned Debian composition and
   `--network none --read-only --user 1000:1000` probe. Only the container ran
   `python agent.py --fake-model`; no generated app source ran on the host.
   Checked `.env`, private/key files and the synthetic canary absent from
   the sanitized kit and `/opt/manual-agent` image tree.

## Results and limits

- Source identity, allowlist/private-file exclusion and both builds: PASS.
- TCK: PASS, 19 checks / 19 passed, pinned dev a1d110de.
- Ordinary container: PASS; output
  `{"category":"technical","ticket_id":"T-101"}`.
- Actual local SBX: NOT RUN. Actual cloud SBX: NOT RUN. No live model call,
  credential binding, cloud upload, policy-denial or microVM claim follows.
  The host-only commands remain in [H1/H2](../acceptance-handoff.md).
