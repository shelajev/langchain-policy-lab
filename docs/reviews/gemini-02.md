# Fresh audience review

Model: gemini-2.5-flash

NEEDS REVISION

The core content of the documentation is good, providing thorough explanations for the target audience. However, the initial setup instructions in both the `README.md` and `docs/user-guide.md` suffer from commands preceding their necessary explanations, forcing the reader to guess or read ahead. Specifically, the installation of `uv` itself is assumed in the `README.md` quickstart, and the effects of custom shell scripts are consistently described *after* the commands that invoke them, making a smooth first-pass reading and execution challenging.

### Findings

#### 1. Missing `uv` installation instructions in `README.md` Quickstart

*   **Exact Quote/Location:** `README.md`, "Quickstart without a paid credential", under the prerequisite line:
    ```bash
    uv python install 3.13.7
    ```
*   **What I understood so far:** The quickstart requires `uv 0.9.26` to be installed on Linux, but no instructions are provided on *how* to install `uv` itself. The reader is explicitly stated to *not* have prior knowledge of `uv` conventions. The first `uv` command appears before any such explanation.
*   **What is missing:** A direct instruction or link to instructions for installing `uv 0.9.26`. While `docs/user-guide.md` later provides this information, it's not present in the `README.md` quickstart, which is the first point of contact for a new user.
*   **Concrete Repair:** Add a line *before* the quickstart code block in `README.md` to guide the user on `uv` installation. For example:
    "If `uv` is not installed, follow the instructions in [Prerequisites and downloads](docs/user-guide.md#prerequisites-and-downloads) to install `uv 0.9.26`."

#### 2. Script effects explained too late in `README.md`

*   **Exact Quote/Location:** `README.md`, "Kit and verification", first command:
    ```bash
    bash scripts/install-ci-tools.sh /tmp/langchain-tools
    ```
    The explanation "The first command downloads checksum-pinned uv and builds Docker's kit-tck from an exact source commit." appears *after* this command.
*   **What I understood so far:** I need to execute a shell script `install-ci-tools.sh`.
*   **What is missing:** The effect of the script is not explained *before* the command, requiring the reader to run it blindly or read ahead to understand its purpose. This pattern repeats for `scripts/check-kit.sh` and `scripts/check-filesystem.sh` in the same section. The audience brief explicitly states: "A script named in the prose does not explain its effects." This is a direct violation.
*   **Concrete Repair:** Move the explanation for each script to immediately *before* its respective command.
    For `scripts/install-ci-tools.sh`:
    "The `install-ci-tools.sh` script downloads checksum-pinned `uv` and builds Docker's `kit-tck` from an exact source commit. Use a temporary directory for the tools:"
    ```bash
    bash scripts/install-ci-tools.sh /tmp/langchain-tools
    ```
    Repeat this pattern for `scripts/check-kit.sh` and `scripts/check-filesystem.sh`.

#### 3. Script effects explained too late in `docs/user-guide.md`

*   **Exact Quote/Location:** `docs/user-guide.md`, "5. Build and verify the mixin", first command:
    ```bash
    bash scripts/install-ci-tools.sh /tmp/langchain-tools
    ```
    The relevant explanation for `check-kit.sh` ("It executes `docker buildx build` against `langchain.yaml`...") and `check-filesystem.sh` ("The filesystem probe copies the overlay onto...") again appear *after* their respective commands.
*   **What I understood so far:** I need to execute `install-ci-tools.sh`, `check-kit.sh`, and `check-filesystem.sh`.
*   **What is missing:** Similar to the `README.md`, the effects of these scripts are not explained *before* the commands are presented. This forces the reader to execute instructions without full comprehension of their immediate impact.
*   **Concrete Repair:** Move the explanation for each script to immediately *before* its respective command in this section.
    For `scripts/install-ci-tools.sh`:
    "Run `scripts/install-ci-tools.sh` to download checksum-pinned `uv` and build Docker's `kit-tck` from an exact source commit. Use a fresh OCI directory; `check-kit.sh` refuses an existing path."
    ```bash
    bash scripts/install-ci-tools.sh /tmp/langchain-tools
    ```
    For `scripts/check-kit.sh`:
    "Then, `check-kit.sh` will validate the source, build and export the OCI image, and run artifact conformance checks. Local artifact evidence reports 19/19 conformance checks. `sbx kit validate` is not a v3 source validator."
    ```bash
    bash scripts/check-kit.sh /tmp/langchain-layout-new
    ```
    For `scripts/check-filesystem.sh`:
    "Finally, `check-filesystem.sh` runs the bundled Python/sample on a Debian base without system Python, with network disabled. It is a filesystem dependency probe, not actual SBX composition. The filesystem probe copies the overlay onto digest-pinned Debian bookworm with no system Python and runs the evaluation as uid 1000, read-only, `--network none`."
    ```bash
    bash scripts/check-filesystem.sh
    ```
