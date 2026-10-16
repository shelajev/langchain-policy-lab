#!/usr/bin/env python3
import re
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
FILES = [ROOT / "README.md"] + [ROOT / "docs" / name for name in (
    "user-guide.md", "policy-lab-guide.md", "run-your-langchain-in-docker-sandboxes.md",
    "acceptance-handoff.md", "product-overview.md", "marketing-brief.md", "blog-outline.md",
    "provenance.md", "editorial-process.md",
)] + list((ROOT / "skills/langchain-sandbox-kit").rglob("*.md")) + list((ROOT / "examples").glob("*/README.md"))
failures = []
checked = 0
for source in FILES:
    text = re.sub(r"```.*?```", "", source.read_text(), flags=re.S)
    for target in re.findall(r"\]\(([^)\s]+)(?:\s+[^)]*)?\)", text):
        if re.match(r"[a-z]+:", target) or target.startswith("#"):
            continue
        filename = unquote(target.split("#", 1)[0])
        if not filename:
            continue
        checked += 1
        if not (source.parent / filename).exists():
            failures.append(f"{source.relative_to(ROOT)}: missing {filename}")
if failures:
    raise SystemExit("\n".join(failures))
print(f"PASS: {checked} relative file/directory links across {len(FILES)} current reader-facing files; archived review packets excluded.")
