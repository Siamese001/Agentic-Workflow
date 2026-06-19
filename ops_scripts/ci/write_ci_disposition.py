#!/usr/bin/env python3
"""Write a normalized CI disposition JSON payload."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

STATUS_BLOCKING = {"FAIL_BLOCKING"}
STATUS_VOCAB = {
    "PASS",
    "FAIL_BLOCKING",
    "FAIL_ADVISORY",
    "SKIP_NOT_RELEVANT",
    "SKIP_MISSING_INPUT",
    "INFRASTRUCTURE_GAP",
    "MANUAL_ONLY",
}


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    items: list[str] = []
    for part in value.replace("\n", ",").split(","):
        item = part.strip()
        if item:
            items.append(item)
    return items


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workflow", required=True)
    parser.add_argument("--lane", required=True)
    parser.add_argument("--status", required=True)
    parser.add_argument("--reason", default="")
    parser.add_argument("--evidence-artifact", default="")
    parser.add_argument("--selected-lanes-text", default="")
    parser.add_argument("--changed-files-text", default="")
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    status = args.status.strip().upper()
    if status not in STATUS_VOCAB:
        raise SystemExit(f"unsupported status: {status}")

    payload = {
        "workflow": args.workflow,
        "lane": args.lane,
        "status": status,
        "blocking": status in STATUS_BLOCKING,
        "reason": args.reason,
        "evidence_artifact": args.evidence_artifact,
        "selected_lanes": _split_csv(args.selected_lanes_text),
        "changed_files": [line for line in args.changed_files_text.splitlines() if line.strip()],
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.out.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
