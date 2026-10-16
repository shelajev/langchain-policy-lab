#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root"
temporary=$(mktemp -d)
trap 'rm -rf "$temporary"' EXIT
printf '%s\n' 'Evidence: single-file source/build/container; NOT SBX runtime confinement proof.'
python3 - "$temporary" <<'PY'
import importlib.util
import json
from pathlib import Path
import sys

spec = importlib.util.spec_from_file_location("helper", "skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py")
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
project = Path("examples/single-file-agent")
report, files = helper.inspect(project, "agent.py")
answers = {"name": "single-file", "dataPaths": [], "launch": "python agent.py --fake-model",
           "decisions": {item["id"]: {"action": "out-of-scope", "reason": "Fake-only regression test; no provider or other network access requested"} for item in report["findings"]}}
temporary = Path(sys.argv[1])
path = temporary / "answers.json"
path.write_text(json.dumps(answers))
helper.generate(project, "agent.py", path, temporary / "kit")
assert (temporary / "kit/app/agent.py").read_bytes() == (project / "agent.py").read_bytes()
assert helper.inspect(project, "agent.py")[0]["inputHashes"] == report["inputHashes"]
print("PASS: root script preserved, questions explicitly answered out-of-scope for fake-only regression")
PY
docker buildx build "$temporary/kit" -f "$temporary/kit/single-file.yaml" --progress plain -t single-file:probe-overlay --load
docker build -t single-file:probe -f scripts/single-file-probe.dockerfile .
docker run --rm --network none --read-only --user 1000:1000 -e PYTHONDONTWRITEBYTECODE=1 single-file:probe sh -eu -c 'cd /opt/single-file/app && python agent.py --fake-model'
