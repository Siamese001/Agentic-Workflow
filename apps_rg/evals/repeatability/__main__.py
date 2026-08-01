"""CLI for evaluating an already-completed sealed run set."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evaluation import evaluate_run_set


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-set", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    run_set = json.loads(args.run_set.read_text(encoding="utf-8"))
    receipt = evaluate_run_set(run_set)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
