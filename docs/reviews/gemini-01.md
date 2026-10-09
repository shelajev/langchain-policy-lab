# Fresh audience review

Model: gemini-2.5-flash

NEEDS REVISION

## Findings

The primary blocker is the ambiguity regarding the specific function of `scripts/check-filesystem.sh` at its first mention in `README.md`. While the `user-guide.md` later clarifies this, a reader encountering the command in the `README.md` must infer or guess its purpose without immediate context.

- **Exact quote/location:** `README.md`, under "Kit and verification" section:
    ```bash
    bash scripts/check-kit.sh /tmp/langchain-layout-new
    bash scripts/check-filesystem.sh
    ```
    Followed by:
    ```markdown
    The first command downloads checksum-pinned uv and builds Docker's kit-tck from
    an exact source commit. Use a **new** layout path. Checks run source validation
    and build, OCI export, artifact conformance and a filesystem-only Debian probe.
    The probe is not actual SBX composition. GitHub Actions executes these checks,
    behavioral tests and an isolated clean-checkout journey on `ubuntu-24.04`;
    the hosted workflow itself has not been run from this unpublished repository.
    ```

- **What was understood so far:**
    I understand that `scripts/install-ci-tools.sh` downloads `uv` and builds `kit-tck`. I also understand that `scripts/check-kit.sh` is run. The subsequent sentence describes a set of checks: "source validation and build, OCI export, artifact conformance and a filesystem-only Debian probe."

- **What is missing:**
    At this point in `README.md`, it is unclear which of the listed scripts (`check-kit.sh` or `check-filesystem.sh`) is responsible for which specific part of the described "checks." Specifically, the role of `scripts/check-filesystem.sh` is not explicitly stated. A reader must guess whether it performs the "filesystem-only Debian probe" or if that is part of `check-kit.sh`, or if `check-filesystem.sh` performs some other, unspecified, check.

- **Concrete repair:**
    Clarify the specific function of `scripts/check-filesystem.sh` in `README.md` immediately after its mention, making it explicit which script performs which check.

    **Proposed change:**

    ```diff
    --- a/README.md
    +++ b/README.md
    @@ -34,10 +34,11 @@
     export PATH="/tmp/langchain-tools:$PATH"
     bash scripts/check-kit.sh /tmp/langchain-layout-new
     bash scripts/check-filesystem.sh
    -
    -The first command downloads checksum-pinned uv and builds Docker's kit-tck from
    -an exact source commit. Use a **new** layout path. Checks run source validation
    -and build, OCI export, artifact conformance and a filesystem-only Debian probe.
    -The probe is not actual SBX composition. GitHub Actions executes these checks,
    -behavioral tests and an isolated clean-checkout journey on `ubuntu-24.04`;
    -the hosted workflow itself has not been run from this unpublished repository.
    +
    +The first command downloads checksum-pinned uv and builds Docker's kit-tck from an exact source commit.
    +Use a **new** layout path. `check-kit.sh` runs source validation, builds the OCI image, and
    +performs artifact conformance checks. `check-filesystem.sh` runs a filesystem-only Debian probe.
    +The probe is not actual SBX composition.
    +GitHub Actions executes these checks, behavioral tests and an isolated clean-checkout journey
    +on `ubuntu-24.04`; the hosted workflow itself has not been run from this unpublished repository.
    ```
