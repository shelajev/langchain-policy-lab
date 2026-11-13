set -eu
python3 - <<'PY'
import hashlib
import io
import platform
from pathlib import Path
import tarfile
from urllib.request import urlopen

checksums = {
    "x86_64": "30ccbf0a66dc8727a02b0e245c583ee970bdafecf3a443c1686e1b30ec4939e8",
    "aarch64": "f71040c59798f79c44c08a7a1c1af7de95a8d334ea924b47b67ad6b9632be270",
}
architecture = platform.machine()
expected = checksums[architecture]
directory = f"uv-{architecture}-unknown-linux-gnu"
with urlopen(f"https://github.com/astral-sh/uv/releases/download/0.9.26/{directory}.tar.gz", timeout=120) as response:
    archive = response.read()
if hashlib.sha256(archive).hexdigest() != expected:
    raise SystemExit("uv checksum mismatch")
destination = Path.home() / ".local/bin/uv"
destination.parent.mkdir(parents=True, exist_ok=True)
with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as bundle:
    destination.write_bytes(bundle.extractfile(directory + "/uv").read())
destination.chmod(0o755)
PY
export PATH="$HOME/.local/bin:$PATH"
uv --version
uv sync --locked
