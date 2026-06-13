"""Compare an apps_eval record against a baseline record."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from apps_eval.runner.core import compare_record_to_baseline


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare apps_eval records without storing drift memory")
    parser.add_argument("--record", required=True)
    parser.add_argument("--baseline", required=True)
    args = parser.parse_args(argv)
    record = json.loads(Path(args.record).read_text(encoding="utf-8"))
    baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    summary = compare_record_to_baseline(record, baseline)
    print(json.dumps(summary.to_dict(), indent=2, sort_keys=True))
    return 0 if summary.verdict != "regression" else 1


if __name__ == "__main__":
    raise SystemExit(main())
