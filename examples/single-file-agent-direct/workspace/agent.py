import argparse
import os

from langchain.chat_models import init_chat_model
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


parser = argparse.ArgumentParser()
parser.add_argument("--fake-model", action="store_true")
args = parser.parse_args()
if args.fake_model:
    os.environ["LANGSMITH_TRACING"] = "false"
    model = FakeListChatModel(responses=['{"category":"technical","ticket_id":"T-101"}'])
else:
    model = init_chat_model("gemini-2.5-flash", model_provider="google_genai", max_output_tokens=256, thinking_budget=0, response_mime_type="application/json")
prompt = ChatPromptTemplate.from_template("Classify this synthetic ticket, return JSON: {ticket}")
print((prompt | model | StrOutputParser()).invoke({"ticket": "T-101: report export fails"}))
