#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
temporary=$(mktemp -d)
trap 'rm -rf "$temporary"' EXIT
printf '%s\n' 'Evidence class: raw source/lock setup/build only; NOT SBX or live-model execution.'
cp -R "$root/skills/langchain-sandbox-kit/tests/fixtures/raw-agent" "$temporary/app"
printf '%s\n' 'TEST_ONLY_PRIVATE_CANARY_4728c2bd' > "$temporary/app/.env"
helper="$root/skills/langchain-sandbox-kit/scripts/sbx_langchain_kit.py"
python3 "$helper" inspect --project "$temporary/app" --entrypoint agent.py --json "$temporary/raw.json"
python3 - "$temporary" <<'PY'
import json
from pathlib import Path
import sys

temporary = Path(sys.argv[1])
report = json.loads((temporary / "raw.json").read_text())
assert "requirements.txt" in report["inputHashes"]
assert ".env" in report["excluded"] and ".env" not in report["inputHashes"]
assert any(item["kind"] == "lock-setup" for item in report["findings"])
assert any(item["value"] == "generativelanguage.googleapis.com" for item in report["findings"])
print("PASS: requirements inspected, lock-setup question raised, .env excluded")
PY
cd "$temporary/app"
uv init --bare --no-workspace --name single-file-agent --python 3.13.7
uv python pin 3.13.7
uv add --no-sync 'langchain==1.4.4' 'langchain-core==1.6.9' 'langchain-google-genai==4.4.0'
uv lock
cmp agent.py "$root/skills/langchain-sandbox-kit/tests/fixtures/raw-agent/agent.py"
test "$(find . -maxdepth 1 -type f | wc -l)" -eq 6
python3 "$helper" inspect --project . --entrypoint agent.py --json "$temporary/locked.json"
python3 - "$temporary" <<'PY'
import hashlib
import json
from pathlib import Path
import sys

temporary = Path(sys.argv[1])
report = json.loads((temporary / "locked.json").read_text())
assert not any(item["kind"] == "lock-setup" for item in report["findings"])
answers = {"name": "raw-agent", "launch": "python agent.py --fake-model", "dataPaths": [],
           "decisions": {item["id"]: {"action": "out-of-scope", "reason": "Fake-only build regression; no provider access requested"}
                         for item in report["findings"]}}
(temporary / "answers.json").write_text(json.dumps(answers))
print("PASS: unchanged agent.py SHA256=" + hashlib.sha256((temporary / "app/agent.py").read_bytes()).hexdigest())
PY
if [ "${1:-}" = --direct-out ]; then
  python3 "$helper" direct --project . --entrypoint agent.py --answers "$temporary/answers.json" --out "${2:?Pass a new direct output directory}"
  cmp agent.py "$2/workspace/agent.py"
  test ! -e "$2/workspace/.env"
  printf '%s\n' 'PASS: raw fixture lock setup reused for direct snapshot; no kit build requested.'
  exit 0
fi
python3 "$helper" generate --project . --entrypoint agent.py --answers "$temporary/answers.json" --out "$temporary/kit"
cmp agent.py "$temporary/kit/app/agent.py"
test ! -e "$temporary/kit/app/.env"
if grep -r -l TEST_ONLY_PRIVATE_CANARY_4728c2bd "$temporary/kit"; then exit 1; fi
for document in "$root/skills/langchain-sandbox-kit/SKILL.md" "$root/skills/langchain-sandbox-kit/references/dependencies.md" "$root/examples/single-file-agent/README.md"; do
  sed -n '/^uv init /,/^uv lock$/p' "$root/scripts/check-raw-single-file.sh" | while IFS= read -r command; do
    grep -F -- "$command" "$document" >/dev/null
  done
done
docker buildx build "$temporary/kit" -f "$temporary/kit/raw-agent.yaml" --progress plain --output type=cacheonly
printf '%s\n' 'PASS: raw app -> reviewed uv lock -> sanitized kit build; no app source executed.'
