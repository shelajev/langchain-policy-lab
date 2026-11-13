CASES = [
    ("What is the Tier 1 meal allowance?", "grounded", "$90", "travel_policy.md"),
    ("What is the receipt threshold?", "grounded", "$25", "expense_policy.md"),
    ("What is the home office equipment stipend?", "grounded", "$500", "remote_work_policy.md"),
    ("What is the monthly internet reimbursement?", "grounded", "$50", "remote_work_policy.md"),
    ("Where are API keys and secrets stored?", "grounded", "vault", "security_policy.md"),
    ("What are the data classification levels?", "grounded", "Restricted", "security_policy.md"),
    ("Can I bring my pet python into the office?", "unsupported", "", None),
    ("What is the company car policy?", "unsupported", "", None),
    ("What holiday bonuses are paid?", "unsupported", "", None),
    ("What is the stock option vesting schedule?", "unsupported", "", None),
    ("What are the parental leave benefits?", "unsupported", "", None),
]


def evaluate(assistant) -> dict:
    results = []
    for question, status, fact, source in CASES:
        answer = assistant.ask(question)
        passed = (answer["status"] == status and fact in answer["answer"]
                  and (source is None and not answer["citations"]
                       or any(citation["source"] == source for citation in answer["citations"])))
        results.append({"question": question, "passed": passed, "result": answer})
    return {"provider": assistant.provider, "passed": all(result["passed"] for result in results),
            "cases": results}
