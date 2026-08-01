"""CLI for offline whole-resume and W9 evaluation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .evaluation import evaluate_whole_resume
from .reporting import write_receipt

_EXIT_CODES = {"PASS": 0, "FAIL": 1, "UNKNOWN": 2}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate a sealed six-pair whole-resume W9 bundle.")
    parser.add_argument("--input", required=True, type=Path, help="Sealed input JSON")
    parser.add_argument("--output", type=Path, help="Optional evaluation receipt path")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        bundle = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"whole-resume input error: {exc}", file=sys.stderr)
        return 3
    receipt = evaluate_whole_resume(bundle)
    if args.output is not None:
        try:
            write_receipt(receipt, args.output, pretty=not args.compact)
        except OSError as exc:
            print(f"whole-resume output error: {exc}", file=sys.stderr)
            return 3
    print(
        json.dumps(
            receipt,
            allow_nan=False,
            ensure_ascii=False,
            indent=None if args.compact else 2,
            separators=(",", ":") if args.compact else None,
            sort_keys=True,
        )
    )
    return _EXIT_CODES[receipt["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
