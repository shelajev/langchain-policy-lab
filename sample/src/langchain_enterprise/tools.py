import re
from langchain_core.documents import Document
from langchain.tools import tool
from pydantic import BaseModel, ConfigDict, Field


class MealInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    city_tier: int = Field(ge=1, le=3, strict=True)
    days: int = Field(ge=1, le=30, strict=True)


class ReceiptInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    amount: float = Field(ge=0, le=100_000, allow_inf_nan=False, strict=True)


def policy_tools(documents: list[Document]):
    def section(source: str, heading: str) -> Document:
        matches = [document for document in documents
                   if document.metadata["source"] == source and document.metadata["section"] == heading]
        if len(matches) != 1:
            raise ValueError("Tool policy section missing or ambiguous")
        return matches[0]

    @tool(args_schema=MealInput)
    def calculate_meal_allowance(city_tier: int, days: int) -> dict:
        """Read the synthetic meal allowance and calculate a bounded trip total."""
        document = section("travel_policy.md", "Meal allowance")
        match = re.search(rf"Tier {city_tier}: \$(\d+) per day", document.page_content)
        if not match:
            raise ValueError("Meal allowance format is unsupported")
        daily = int(match.group(1))
        return {"daily_usd": daily, "days": days, "total_usd": daily * days,
                "citation": document.metadata}

    @tool(args_schema=ReceiptInput)
    def check_receipt_requirement(amount: float) -> dict:
        """Read the synthetic receipt threshold for a bounded expense amount."""
        document = section("expense_policy.md", "Receipts")
        match = re.search(r"expense of \$(\d+) or more", document.page_content)
        if not match:
            raise ValueError("Receipt threshold format is unsupported")
        threshold = int(match.group(1))
        return {"amount_usd": amount, "receipt_required": amount >= threshold,
                "threshold_usd": threshold, "citation": document.metadata}

    return {"meal": calculate_meal_allowance, "receipt": check_receipt_requirement}
