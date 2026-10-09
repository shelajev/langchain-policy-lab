import json
import os

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class DeterministicFakeChatModel(BaseChatModel):
    @property
    def _llm_type(self) -> str:
        return "deterministic-extractive-fake"

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        payload = json.loads(messages[-1].content)
        passages = payload["passages"]
        response = {"answer": "\n".join(passage["text"] for passage in passages),
                    "chunk_ids": [passage["chunk_id"] for passage in passages]}
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=json.dumps(response)))])


def get_model(provider: str, *, approve_live: bool = False) -> BaseChatModel:
    if provider == "deterministic":
        return DeterministicFakeChatModel()
    if provider != "gemini":
        raise ValueError("Unknown provider")
    if not approve_live:
        raise ValueError("Live Gemini requires explicit --approve-live")
    if not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
        raise ValueError("An existing approved Gemini credential is required")
    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0,
                                 max_retries=0, timeout=30, max_output_tokens=512)
