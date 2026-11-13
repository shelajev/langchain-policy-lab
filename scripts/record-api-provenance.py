import hashlib
import importlib.metadata
import inspect
import json
from pathlib import Path

from langchain.tools import tool
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field


apis = {
    "langchain.tools.tool": tool,
    "langchain_core.callbacks.CallbackManagerForRetrieverRun": CallbackManagerForRetrieverRun,
    "langchain_core.documents.Document": Document,
    "langchain_core.retrievers.BaseRetriever": BaseRetriever,
    "langchain_core.runnables.RunnableLambda": RunnableLambda,
    "langchain_core.prompts.ChatPromptTemplate": ChatPromptTemplate,
    "langchain_core.language_models.chat_models.BaseChatModel": BaseChatModel,
    "langchain_core.output_parsers.StrOutputParser": StrOutputParser,
    "langchain_core.messages.AIMessage": AIMessage,
    "langchain_core.outputs.ChatGeneration": ChatGeneration,
    "langchain_core.outputs.ChatResult": ChatResult,
    "pydantic.BaseModel": BaseModel,
    "pydantic.Field": Field,
    "langchain_google_genai.ChatGoogleGenerativeAI": ChatGoogleGenerativeAI,
}
records = []
for public_api, implementation in apis.items():
    source = Path(inspect.getsourcefile(implementation))
    package = implementation.__module__.split(".")[0]
    distribution = package.replace("_", "-")
    records.append({
        "public_api": public_api,
        "implementation_module": implementation.__module__,
        "distribution": distribution,
        "version": importlib.metadata.version(distribution),
        "file": str(source).split("site-packages/", 1)[-1],
        "source_line": inspect.getsourcelines(implementation)[1],
        "file_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    })
fields = ChatGoogleGenerativeAI.model_fields
print(json.dumps({"apis": records, "provider_fields": {
    name: {"present": name in fields, "alias": fields[name].alias if name in fields else None}
    for name in ["model", "temperature", "max_retries", "timeout", "max_output_tokens"]
}}, indent=2))
