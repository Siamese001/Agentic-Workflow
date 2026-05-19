#!/usr/bin/env python3
"""Assign deterministic calibration / validation / drift_holdout splits (offline)."""

from __future__ import annotations

import argparse
import hashlib
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from _common import load_json, resolve_glob, write_json_report

SPLITS = ("calibration", "validation", "drift_holdout")
# Cumulative thresholds on 0..99 hash bucket
_THRESHOLDS = (60, 80)  # <60 cal, <80 val, else drift


def _split_bucket(benchmark_id: str, seed: int) -> str:
    digest = hashlib.sha256(f"{seed}:{benchmark_id}".encode()).hexdigest()
    bucket = int(digest[:8], 16) % 100
    if bucket < _THRESHOLDS[0]:
        return "calibration"
    if bucket < _THRESHOLDS[1]:
        return "validation"
    return "drift_holdout"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Assign benchmark split labels.")
    parser.add_argument("--samples-glob", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args(argv)

    sample_paths = resolve_glob(args.samples_glob)
    if not sample_paths:
        write_json_report(
            Path(args.out),
            {"tool": "assign_benchmark_splits", "status": "FAIL", "error": "no samples"},
        )
        return 1

    assignments: list[dict] = []
    by_split: dict[str, int] = defaultdict(int)
    by_group: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for path in sorted(sample_paths, key=lambda p: p.name):
        sample = load_json(path)
        bid = str(sample.get("benchmark_id", path.stem))
        split = _split_bucket(bid, args.seed)
        row = {
            "benchmark_id": bid,
            "source_path": str(path.as_posix()),
            "split": split,
            "section_group": sample.get("section_group"),
            "section_id": sample.get("section_id"),
            "role_anchor": sample.get("role_anchor"),
            "job_family": sample.get("job_family"),
            "negative_control_type": sample.get("negative_control_type"),
        }
        assignments.append(row)
        by_split[split] += 1
        sg = str(sample.get("section_group", "unknown"))
        by_group[sg][split] += 1

    tiny_set = len(assignments) < 10
    report = {
        "tool": "assign_benchmark_splits",
        "status": "PASS",
        "dry_run": True,
        "proof_eligible": False,
        "seed": args.seed,
        "tiny_set_placeholder": tiny_set,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "assignment_count": len(assignments),
        "split_counts": dict(by_split),
        "split_counts_by_section_group": {k: dict(v) for k, v in by_group.items()},
        "note": (
            "Tiny example set: splits are deterministic hash placeholders, not stratified 60/20/20 counts."
            if tiny_set
            else "Splits assigned via seeded hash buckets (60/20/20 target at scale)."
        ),
        "assignments": assignments,
    }
    write_json_report(Path(args.out), report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
