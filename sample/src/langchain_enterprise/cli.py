import argparse
import json
from pathlib import Path
import sys

from .chain import PolicyAssistant
from .evaluation import evaluate


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Synthetic policy assistant; offline by default")
    parser.add_argument("--policies", type=Path, default=Path("data/policies"))
    parser.add_argument("--provider", choices=["deterministic", "gemini"], default="deterministic")
    parser.add_argument("--approve-live", action="store_true")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--query")
    mode.add_argument("--eval-suite", action="store_true")
    mode.add_argument("--tool", choices=["meal", "receipt"])
    parser.add_argument("--city-tier", type=int, default=1)
    parser.add_argument("--days", type=int, default=1)
    parser.add_argument("--amount", type=float, default=25)
    args = parser.parse_args(argv)
    try:
        assistant = PolicyAssistant(args.policies, args.provider, approve_live=args.approve_live)
        if args.eval_suite:
            result = evaluate(assistant)
            exit_code = 0 if result["passed"] else 1
        elif args.tool:
            inputs = {"city_tier": args.city_tier, "days": args.days} if args.tool == "meal" else {"amount": args.amount}
            result = assistant.tools[args.tool].invoke(inputs)
            exit_code = 0
        else:
            result = assistant.ask(args.query)
            exit_code = 1 if result["status"] == "failure" else 0
    except Exception:
        result = {"status": "failure", "error": "configuration_or_tool_failure",
                  "hint": "Check policy path, input bounds, optional dependency and approved provider credential."}
        exit_code = 1
    print(json.dumps(result, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
