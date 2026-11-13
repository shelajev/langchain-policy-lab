import argparse
import json
import os
from pathlib import Path

import httpx

from ticket_triage.chain import classify
from ticket_triage.sources import fetch_status, post_summary


def main(argv=None):
    parser = argparse.ArgumentParser(description="Triage one support ticket")
    parser.add_argument("--ticket", type=Path, required=True)
    parser.add_argument("--fake-model", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--post-webhook", action="store_true")
    args = parser.parse_args(argv)
    if args.fake_model:
        os.environ["LANGSMITH_TRACING"] = "false"
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
    try:
        ticket = json.loads(args.ticket.read_text())
        if not isinstance(ticket.get("id"), str) or not isinstance(ticket.get("body"), str):
            raise ValueError("ticket needs string id and body")
        if args.status:
            ticket["status"] = fetch_status(os.environ["TRIAGE_STATUS_URL"])
        result = classify(ticket, args.fake_model).model_dump()
        if args.post_webhook:
            post_summary(result)
    except (httpx.HTTPError, OSError, ValueError, KeyError):
        parser.exit(2, "triage failed: check input, configuration and network policy (details withheld)\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
