# uv 0.9.26 Linux release verification

Verified on 2026-10-10 against the official Astral release API:
`https://api.github.com/repos/astral-sh/uv/releases/tags/0.9.26`.
The response identifies tag `0.9.26` and release page
`https://github.com/astral-sh/uv/releases/tag/0.9.26`.

Downloaded both GNU/Linux archives and their individual checksum files from
`https://github.com/astral-sh/uv/releases/download/0.9.26/` through the existing
proxy. `sha256sum -c` returned OK for each; both digests also match the API's
archive digest fields:

| Architecture | Archive | Checksum file | Archive SHA-256 |
| --- | --- | --- | --- |
| x86_64 | `uv-x86_64-unknown-linux-gnu.tar.gz` | `uv-x86_64-unknown-linux-gnu.tar.gz.sha256` | `30ccbf0a66dc8727a02b0e245c583ee970bdafecf3a443c1686e1b30ec4939e8` |
| aarch64 (arm64) | `uv-aarch64-unknown-linux-gnu.tar.gz` | `uv-aarch64-unknown-linux-gnu.tar.gz.sha256` | `f71040c59798f79c44c08a7a1c1af7de95a8d334ea924b47b67ad6b9632be270` |

Each checksum file contains a SHA-256 digest followed by the exact archive
basename, so it can be checked from the download directory without rewriting.
`tar -tzf` shows three entries per archive: `uv-<target>/`,
`uv-<target>/uv` and `uv-<target>/uvx`, where `<target>` is the corresponding
GNU/Linux target in the table. The guide installs the nested `uv` binary only.
The reviewer-suggested `uv-linux-<arch>.tar.gz` filenames are not these assets.

This verifies release metadata, downloaded checksums and archive layout only;
it does not claim another sample, kit, SBX or live-model execution pass.
