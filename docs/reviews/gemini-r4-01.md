# Fresh audience review

Model: gemini-3.8-flash

## Overall Status: NEEDS REVISION

The draft provides clear security motivation and helpful explanations of the inspection-to-generation pipeline. However, a reader following the tutorial will get stuck due to direct contradictions between the promised workflow and the manual steps, missing installation steps for required tools, and incompatible commands when executing the sandboxed app.

---

## Blockers

### 1. Direct contradiction: Manual path does not use the ticket-triage app
- **Location:** Paragraph 2 vs. section "The manual path uses the same kit":
  > "There is an agent-assisted path and an equivalent manual path. Both use the same ticket-triage app and files."

  contrasted with:
  > "For a root `agent.py`, start from the [single-file kit](../examples/single-file-agent-kit/). It is a template, not your app or your answers. ... 1. **`app/`**: remove the example files and put your own unchanged `agent.py`, `pyproject.toml`, `uv.lock` and `.python-version` here..."
- **What was understood so far:** Both paths would demonstrate packaging the same `ticket-triage` example application so the reader can compare agent-driven vs. manual packaging on identical inputs.
- **What is missing:** The manual path immediately abandons `ticket-triage`, switches to copying `examples/single-file-agent-kit`, and instructs the reader to provide a separate root `agent.py`. The premise that both paths use the same app and files is false. A reader attempting to manually package `ticket-triage` has no instructions for its `src/` layout or multi-file configuration.
- **Concrete repair:** Either update paragraph 2 to state that the agent path packages the `ticket-triage` example while the manual path demonstrates adapting the `single-file-agent-kit` template for a custom `agent.py`, or provide manual instructions that actually package `ticket-triage` (using `examples/ticket-triage-kit/`).

---

### 2. Missing prerequisite installation step for `kit-tck`
- **Location:** Section "Start with an app, not a sandbox framework" and "The manual path uses the same kit":
  > "Build validation additionally needs the pinned `kit-tck`; the [guide](user-guide.md) shows its user-local installer."

  followed later by:
  ```bash
  kit-tck validate --verbose --layout /tmp/manual-agent-layout 0.1.0
  ```
- **What was understood so far:** `kit-tck` is a required validation tool.
- **What is missing:** `kit-tck` is not a standard Docker or system binary. The tutorial runs `kit-tck validate` as a shell command without providing the command to install it or set up `PATH`. Telling the reader that another document ("the guide") shows an installer breaks linear execution in this tutorial with `command not found: kit-tck`.
- **Concrete repair:** Add the prerequisite installation commands directly in the prerequisites section:
  ```bash
  bash scripts/install-ci-tools.sh /tmp/triage-tools
  export PATH="/tmp/triage-tools:$PATH"
  ```

---

### 3. Incompatible execution command for manual kit users
- **Location:** Section "Run your app inside local Docker Sandboxes":
  > ```bash
  > sbx env plan ./examples/ticket-triage-kit/sbxenv.local.yaml
  > sbx env run --detach ./examples/ticket-triage-kit/sbxenv.local.yaml
  > sbx env exec ./examples/ticket-triage-kit/sbxenv.local.yaml -- sh -lc 'cd /opt/ticket-triage/app && python -m ticket_triage.app --ticket data/tickets/t-101.json --fake-model'
  > ```
  > "For your generated or manual copy, use its absolute environment-file path."
- **What was understood so far:** If the reader built the manual kit in the previous section (`/tmp/manual-agent-kit`), they should substitute `/tmp/manual-agent-kit/sbxenv.local.yaml`.
- **What is missing:** In the manual kit, the application directory is `/opt/manual-agent/app` and the script is `agent.py`. Substituting the manual path into `sbx env exec` as instructed will fail because `/opt/ticket-triage/app` and `ticket_triage.app` do not exist in the manual container overlay. The reader must guess what command to run.
- **Concrete repair:** Explicitly show the alternative `env exec` command for the manual single-file kit:
  ```bash
  # For manual-agent:
  sbx env exec /tmp/manual-agent-kit/sbxenv.local.yaml -- sh -lc 'cd /opt/manual-agent/app && python agent.py --fake-model'
  ```

---

### 4. Missing build step for the agent-generated kit
- **Location:** Between "Generate packaging you can review" and "Run your app inside local Docker Sandboxes".
- **What was understood so far:** The agent-assisted path generates a kit in `/tmp/my-ticket-triage-kit`. The manual path shows `docker buildx build . -f manual-agent.yaml ...` and `kit-tck validate`.
- **What is missing:** The reader following the agent path generates files into `/tmp/my-ticket-triage-kit`, but is never told whether `docker buildx build` must be run on `ticket-triage.yaml` before calling `sbx env run`, or whether `sbx` handles building the kit from the environment file. If building and TCK validation are required or recommended, the build command for `/tmp/my-ticket-triage-kit` is omitted.
- **Concrete repair:** Clarify explicitly whether `sbx env plan`/`run` builds kits on demand from the directory or whether `docker buildx build` is required beforehand. If artifact validation is recommended for the generated kit, provide the corresponding build and `kit-tck` command for `/tmp/my-ticket-triage-kit` before transitioning to runtime execution.

---

## Optional Improvements

### 1. Clarify "implementation sandbox" vs. Docker Sandboxes
- **Location:** Section "Run your LangChain in Docker Sandboxes", paragraph 3:
  > "One host-authorized live Gemini call also passed inside the implementation sandbox, with one synthetic ticket and bounded output. That is **not local/cloud SBX acceptance**. Actual local and cloud SBX have **not run** here because `sbx` is absent."
- **Issue:** To a reader new to v3 Sandbox kits, "passed inside the implementation sandbox" while "`sbx` is absent" sounds contradictory (since both use the term "sandbox").
- **Repair:** Clarify that "implementation sandbox" refers to the repository author's containerized build/CI environment rather than a Docker Sandboxes runtime.

### 2. Explicit working directory reset before `sbx env`
- **Location:** Section "Run your app inside local Docker Sandboxes":
  > "On the approved host, from the repository root:"
- **Issue:** The preceding manual section left the shell in `/tmp/manual-agent-kit` (`cd /tmp/manual-agent-kit`). A reader following commands in order on an approved host may execute the relative paths (`./examples/ticket-triage-kit/...`) from `/tmp/manual-agent-kit` instead of the repo root.
- **Repair:** Prepend `cd <path-to-repo-root>` to the code block or include `cd -` before running the `sbx` commands.
