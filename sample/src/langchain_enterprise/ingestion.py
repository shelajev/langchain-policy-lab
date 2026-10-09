from pathlib import Path
import re

from langchain_core.documents import Document


def load_policies(directory: Path) -> list[Document]:
    paths = sorted(directory.glob("*.md"))
    if not paths:
        raise ValueError("No Markdown policies found")
    documents = []
    for path in paths:
        if path.is_symlink():
            raise ValueError("Policy symlinks are not supported")
        text = path.read_text(encoding="utf-8")
        if len(text) > 100_000:
            raise ValueError("Policy exceeds demo size limit")
        title_match = re.search(r"^title: (.+)$", text, re.MULTILINE)
        if not title_match:
            raise ValueError("Policy title is required")
        title = title_match.group(1)
        for ordinal, section in enumerate(re.split(r"^## ", text, flags=re.MULTILINE)[1:], 1):
            heading, separator, body = section.partition("\n")
            if not separator or not body.strip():
                raise ValueError("Empty policy section")
            documents.append(Document(
                page_content=body.strip(),
                metadata={"source": path.name, "section": heading.strip(),
                          "chunk_id": f"{path.stem}:{ordinal}", "title": title},
            ))
    if not documents:
        raise ValueError("No policy sections found")
    return documents
