# Fresh audience review

Model: gemini-3.8-flash

## Overall Status

**NEEDS REVISION**

---

## Findings

### 1. Blocker: Prompt instructs coding agent to inspect a non-existent path

- **Location**: Section `## Let a coding agent do the inspection`
- **Exact Quote**:
  > Package my LangChain app at ./ticket-triage to run in Docker Sandboxes.
  > Inspect it without executing it. Ask about unresolved access and show me
  > the generated package before requesting any permissions.

- **What you understood so far**:
  The reader is working from the root of the repository checkout and is packaging the ticket-triage example application. The preceding sections referenced the application at `examples/ticket-triage` (e.g., `The [ticket-triage app](../examples/ticket-triage/)`).

- **What is missing**:
  The prompt instructs the agent to package `./ticket-triage`. At the repository root, there is no `./ticket-triage` directory; the app resides at `examples/ticket-triage` (as reflected in the deterministic CLI command given immediately below: `--project examples/ticket-triage`). A user pasting this prompt to an agent running in the repo root will fail when the agent reports that `./ticket-triage` does not exist.

- **Concrete repair**:
  Update the prompt to reference the actual repository relative path:
  ```markdown
  > Package my LangChain app at ./examples/ticket-triage to run in Docker Sandboxes.
  > Inspect it without executing it. Ask about unresolved access and show me
  > the generated package before requesting any permissions.
  ```

---

### 2. Blocker: Runtime commands switch to an unbuilt repository fixture instead of the generated kit

- **Location**: Section `## Run your app inside local Docker Sandboxes` (and repeated in `## Cloud changes the resources, not the app`)
- **Exact Quote**:
  ```bash
  sbx env plan ./examples/ticket-triage-kit/sbxenv.local.yaml
  sbx env run --detach ./examples/ticket-triage-kit/sbxenv.local.yaml
  sbx env exec ./examples/ticket-triage-kit/sbxenv.local.yaml -- sh -lc 'cd /opt/ticket-triage/app && python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model'
  ```

- **What you understood so far**:
  In Section 5 ("Generate packaging you can review"), the reader generated kit files into `/tmp/my-ticket-triage-kit` and ran `docker buildx` and `kit-tck` on that output. The section ended with: *"Continue to the local host handoff, or take the manual route instead."*

- **What is missing**:
  Upon reaching the local sandbox execution section, the primary command snippet abruptly runs `./examples/ticket-triage-kit/sbxenv.local.yaml` (the pre-existing golden fixture in the repository) rather than the `/tmp/my-ticket-triage-kit` directory the reader just generated and validated.

  While the subsequent prose states:
  > For your generated ticket-triage copy, use its absolute environment-file path with the same ticket-triage launch command.

  giving the pre-committed fixture as the primary copy-paste snippet contradicts the tutorial flow. By contrast, the manual track gets explicit, runnable commands for `/tmp/manual-agent-kit/`. Furthermore, the cleanup commands in the cloud section only clean up `./examples/ticket-triage-kit` and `/tmp/manual-agent-kit`, omitting `/tmp/my-ticket-triage-kit` entirely.

- **Concrete repair**:
  Make the generated kit the primary command block (or provide both clearly labeled), and include its cleanup:
  ```bash
  sbx env plan /tmp/my-ticket-triage-kit/sbxenv.local.yaml
  sbx env run --detach /tmp/my-ticket-triage-kit/sbxenv.local.yaml
  sbx env exec /tmp/my-ticket-triage-kit/sbxenv.local.yaml -- sh -lc 'cd /opt/ticket-triage/app && python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model'
  ```
  Note that `./examples/ticket-triage-kit/sbxenv.local.yaml` is the repository's pre-packaged reference fixture if testing against the committed baseline instead. Update the cleanup commands in the Cloud section to also show how to remove `/tmp/my-ticket-triage-kit`.

---

## Optional Comprehension Improvements

### 3. Unexplained YAML file target in `docker buildx build`

- **Location**: Section `## Generate packaging you can review`
- **Exact Quote**:
  ```bash
  docker buildx build . -f ticket-triage.yaml --progress plain --output type=cacheonly
  ```
- **What is missing**:
  The reader understands Docker buildx and Dockerfiles, but is new to v3 Sandbox kits. Passing `-f ticket-triage.yaml` to `docker buildx build` looks like a mistake or typo for `ticket-triage.dockerfile`.
- **Concrete repair**:
  Add a brief sentence clarifying that in v3 Sandbox kits, the kit descriptor (`ticket-triage.yaml`) serves as the BuildKit build definition when compiling the kit artifact.
