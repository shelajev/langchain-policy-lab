import re

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import Field


STOP_WORDS = set("a an the is are do does can i we my our what which how where when for of in on to and or at per about company employee employees policy policies please tell me must use much get have limit daily required requirement".split())
ALIASES = {"dinner": "meal", "meals": "meal", "reimbursed": "reimbursement",
           "receipts": "receipt", "threshold": "receipt", "keys": "key",
           "secrets": "secret", "stored": "store", "storing": "store",
           "password": "passwords", "classifications": "classification",
           "levels": "classification", "equipment": "equipment"}


def tokens(text: str) -> set[str]:
    return {ALIASES.get(word, word) for word in re.findall(r"[a-z]+|\d+", text.lower())
            if word not in STOP_WORDS}


class PolicyRetriever(BaseRetriever):
    documents: list[Document]
    top_k: int = Field(default=2, ge=1, le=4)
    minimum_coverage: float = Field(default=0.6, gt=0, le=1)

    def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> list[Document]:
        query_tokens = tokens(query)
        if not query_tokens:
            return []
        ranked = []
        for document in self.documents:
            passage_tokens = tokens(document.metadata["section"] + " " + document.page_content)
            shared = query_tokens & passage_tokens
            coverage = len(shared) / len(query_tokens)
            if shared and coverage >= self.minimum_coverage:
                ranked.append((coverage, len(shared), document.metadata["chunk_id"], document))
        ranked.sort(key=lambda item: (-item[0], -item[1], item[2]))
        return [item[3] for item in ranked[:self.top_k]]
