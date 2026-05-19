#!/usr/bin/env python3
"""Export blind reviewer packets from benchmark samples (no judge/human scores)."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from _common import (
    REASON_CODE_OPTIONS,
    REVIEWER_INSTRUCTIONS,
    SCORING_DIMENSIONS_BY_GROUP,
    load_json,
    resolve_glob,
    write_json_report,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export blind reviewer packets.")
    parser.add_argument("--samples-glob", required=True)
    parser.add_argument("--assignments", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument(
        "--cleared-only",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Export only pii_status=cleared samples (default true)",
    )
    args = parser.parse_args(argv)

    assign_doc = load_json(Path(args.assignments))
    split_by_id = {
        row["benchmark_id"]: row.get("split")
        for row in assign_doc.get("assignments", [])
    }

    sample_paths = resolve_glob(args.samples_glob)
    skipped_pending = 0
    packets: list[dict] = []
    for path in sorted(sample_paths, key=lambda p: p.name):
        sample = load_json(path)
        if args.cleared_only and sample.get("pii_status") != "cleared":
            skipped_pending += 1
            continue
        bid = sample.get("benchmark_id")
        group = sample.get("section_group", "")
        dims = SCORING_DIMENSIONS_BY_GROUP.get(
            str(group),
            SCORING_DIMENSIONS_BY_GROUP.get("positioning", []),
        )
        packets.append(
            {
                "benchmark_id": bid,
                "section_group": group,
                "section_id": sample.get("section_id"),
                "role_anchor": sample.get("role_anchor"),
                "job_family": sample.get("job_family"),
                "split": split_by_id.get(bid),
                "generated_section_text": sample.get("generated_section_text"),
                "scoring_dimensions": dims,
                "reason_code_options": list(REASON_CODE_OPTIONS),
                "reviewer_instructions": list(REVIEWER_INSTRUCTIONS),
            }
        )

    empty_reason = None
    if not packets and skipped_pending > 0 and args.cleared_only:
        empty_reason = "all_samples_pending_review_excluded"

    out_doc = {
        "tool": "export_reviewer_packets",
        "dry_run": True,
        "proof_eligible": False,
        "blind": True,
        "cleared_only": args.cleared_only,
        "skipped_pending_review_count": skipped_pending,
        "empty_reason": empty_reason,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "packet_count": len(packets),
        "excluded_fields": [
            "human_scores",
            "x1d_judge_refs",
            "reviewer_role",
            "reviewer_confidence",
            "judge_scores",
        ],
        "packets": packets,
    }
    write_json_report(Path(args.out), out_doc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
