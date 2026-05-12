#!/usr/bin/env python3
"""Validate the outreach holdout corpus JSONL file.

Verifies:
- JSONL parses correctly
- Required fields present
- 50 <= corpus size <= 100
- holdout_id uniqueness
- No blank composed_message
- expected_guardrail_flags from allowed enum
- frozen=true invariant

Emits JSON validation report.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ALLOWED_GUARDRAIL_FLAGS = {
    "fake_personalization_flag",
    "fabricated_relationship_flag",
    "unsupported_company_fact_flag",
    "unsupported_recipient_fact_flag",
    "confidential_leakage_flag",
    "sensitive_targeting_flag",
    "spammy_or_hype_language_flag",
    "channel_length_violation_flag",
}

REQUIRED_FIELDS = [
    "holdout_id",
    "scenario_id",
    "channel",
    "recipient_class",
    "outreach_mode",
    "evidence_posture",
    "source_items",
    "composed_message",
    "expected_guardrail_flags",
    "notes",
    "frozen",
    "split",
    "created_by",
    "schema_version",
]


def validate_corpus(corpus_path: Path) -> dict[str, Any]:
    """Validate corpus and return report dict."""
    report: dict[str, Any] = {
        "valid": False,
        "corpus_path": str(corpus_path),
        "total_rows": 0,
        "errors": [],
        "warnings": [],
        "checks": {},
    }

    if not corpus_path.exists():
        report["errors"].append(f"Corpus file not found: {corpus_path}")
        return report

    rows: list[dict] = []
    holdout_ids: set[str] = set()
    line_no = 0

    try:
        with corpus_path.open("r", encoding="utf-8") as f:
            for line in f:
                line_no += 1
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                    rows.append(row)
                except json.JSONDecodeError as e:
                    report["errors"].append(f"Line {line_no}: JSON parse error: {e}")
    except Exception as e:
        report["errors"].append(f"Failed to read corpus: {e}")
        return report

    report["total_rows"] = len(rows)

    # Check corpus size
    if len(rows) < 50:
        report["errors"].append(f"Corpus too small: {len(rows)} rows (minimum 50)")
    elif len(rows) > 100:
        report["errors"].append(f"Corpus too large: {len(rows)} rows (maximum 100)")
    else:
        report["checks"]["corpus_size"] = f"OK ({len(rows)} rows)"

    # Validate each row
    for idx, row in enumerate(rows, 1):
        prefix = f"Row {idx}"

        # Required fields
        for field in REQUIRED_FIELDS:
            if field not in row:
                report["errors"].append(f"{prefix}: Missing required field '{field}'")

        # holdout_id uniqueness
        holdout_id = row.get("holdout_id")
        if holdout_id:
            if holdout_id in holdout_ids:
                report["errors"].append(f"{prefix}: Duplicate holdout_id '{holdout_id}'")
            else:
                holdout_ids.add(holdout_id)
            # Validate format
            if not holdout_id.startswith("lic_holdout_"):
                report["errors"].append(f"{prefix}: Invalid holdout_id format '{holdout_id}'")

        # composed_message not blank
        message = row.get("composed_message", "").strip()
        if not message:
            report["errors"].append(f"{prefix}: composed_message is blank")
        elif len(message) < 10:
            report["warnings"].append(f"{prefix}: composed_message suspiciously short ({len(message)} chars)")

        # expected_guardrail_flags validation
        flags = row.get("expected_guardrail_flags", [])
        if not isinstance(flags, list):
            report["errors"].append(f"{prefix}: expected_guardrail_flags must be a list")
        else:
            invalid_flags = [f for f in flags if f not in ALLOWED_GUARDRAIL_FLAGS]
            if invalid_flags:
                report["errors"].append(f"{prefix}: Invalid guardrail flags: {invalid_flags}")

        # frozen must be true
        frozen = row.get("frozen")
        if frozen is not True:
            report["errors"].append(f"{prefix}: frozen must be true, got {frozen}")

        # split must be holdout
        split = row.get("split")
        if split != "holdout":
            report["errors"].append(f"{prefix}: split must be 'holdout', got '{split}'")

        # schema_version
        schema = row.get("schema_version")
        if schema != "outreach_holdout_corpus.v1":
            report["warnings"].append(f"{prefix}: Unexpected schema_version '{schema}'")

    # Summary
    report["unique_holdout_ids"] = len(holdout_ids)
    report["valid"] = len(report["errors"]) == 0

    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate outreach holdout corpus")
    parser.add_argument(
        "--corpus",
        type=Path,
        default=Path("apps_lic/evals/holdout/outreach_holdout_corpus.v1.jsonl"),
        help="Path to corpus JSONL file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output JSON report path (default: print to stdout)",
    )
    args = parser.parse_args(argv)

    report = validate_corpus(args.corpus)

    report_json = json.dumps(report, indent=2, ensure_ascii=False)

    if args.output:
        args.output.write_text(report_json, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(report_json)

    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
