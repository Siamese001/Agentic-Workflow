#!/usr/bin/env python3
"""Validate human labels CSV against the corpus.

Verifies:
- CSV schema matches expected columns
- holdout_id exists in corpus
- Score fields are integers 1-5
- Boolean guardrail fields parse correctly
- Each holdout item has at least 2 labels (unless marked pending)

Emits JSON validation report.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_COLUMNS = [
    "holdout_id",
    "labeler_id_hash",
    "label_batch_id",
    "labeled_at",
    "response_likelihood_1_5",
    "brand_voice_1_5",
    "personalization_quality_1_5",
    "ask_clarity_low_friction_1_5",
    "fake_personalization_flag",
    "fabricated_relationship_flag",
    "unsupported_company_fact_flag",
    "unsupported_recipient_fact_flag",
    "confidential_leakage_flag",
    "sensitive_targeting_flag",
    "spammy_or_hype_language_flag",
    "channel_length_violation_flag",
    "labeler_confidence_1_3",
    "comments",
]

SCORE_COLUMNS = [
    "response_likelihood_1_5",
    "brand_voice_1_5",
    "personalization_quality_1_5",
    "ask_clarity_low_friction_1_5",
]

BOOLEAN_COLUMNS = [
    "fake_personalization_flag",
    "fabricated_relationship_flag",
    "unsupported_company_fact_flag",
    "unsupported_recipient_fact_flag",
    "confidential_leakage_flag",
    "sensitive_targeting_flag",
    "spammy_or_hype_language_flag",
    "channel_length_violation_flag",
]

CONFIDENCE_COLUMN = "labeler_confidence_1_3"


def load_corpus_ids(corpus_path: Path) -> set[str]:
    """Load all holdout_ids from corpus."""
    ids: set[str] = set()
    if not corpus_path.exists():
        return ids
    with corpus_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                holdout_id = row.get("holdout_id")
                if holdout_id:
                    ids.add(holdout_id)
            except json.JSONDecodeError:
                continue
    return ids


def parse_boolean(value: str) -> tuple[bool, bool]:
    """Parse boolean string. Returns (success, parsed_value)."""
    normalized = value.strip().lower()
    if normalized in ("true", "1", "yes", "t"):
        return True, True
    if normalized in ("false", "0", "no", "f"):
        return True, False
    return False, False


def parse_int_range(value: str, min_val: int, max_val: int) -> tuple[bool, int | None]:
    """Parse integer within range. Returns (success, parsed_value)."""
    try:
        val = int(value.strip())
        if min_val <= val <= max_val:
            return True, val
        return False, val
    except (ValueError, AttributeError):
        return False, None


def validate_labels(labels_path: Path, corpus_path: Path) -> dict[str, Any]:
    """Validate labels CSV and return report."""
    report: dict[str, Any] = {
        "valid": False,
        "labels_path": str(labels_path),
        "corpus_path": str(corpus_path),
        "total_labels": 0,
        "errors": [],
        "warnings": [],
        "checks": {},
        "labels_per_holdout": {},
    }

    if not labels_path.exists():
        report["errors"].append(f"Labels file not found: {labels_path}")
        return report

    corpus_ids = load_corpus_ids(corpus_path)
    if not corpus_ids:
        report["warnings"].append("Corpus not found or empty; cannot verify holdout_id existence")

    rows: list[dict] = []

    try:
        with labels_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                report["errors"].append("CSV has no headers")
                return report

            # Check columns
            missing_cols = set(REQUIRED_COLUMNS) - set(reader.fieldnames)
            if missing_cols:
                report["errors"].append(f"Missing required columns: {sorted(missing_cols)}")

            extra_cols = set(reader.fieldnames) - set(REQUIRED_COLUMNS)
            if extra_cols:
                report["warnings"].append(f"Extra columns present: {sorted(extra_cols)}")

            for idx, row in enumerate(reader, 1):
                rows.append(row)
                prefix = f"Row {idx}"

                holdout_id = row.get("holdout_id", "").strip()
                if not holdout_id:
                    report["errors"].append(f"{prefix}: holdout_id is blank")
                    continue

                # Track labels per holdout
                report["labels_per_holdout"][holdout_id] = report["labels_per_holdout"].get(holdout_id, 0) + 1

                # Verify holdout_id exists in corpus
                if corpus_ids and holdout_id not in corpus_ids:
                    report["errors"].append(f"{prefix}: holdout_id '{holdout_id}' not found in corpus")

                # Validate labeler_id_hash
                labeler_hash = row.get("labeler_id_hash", "").strip()
                if not labeler_hash:
                    report["errors"].append(f"{prefix}: labeler_id_hash is blank")
                elif len(labeler_hash) != 64:
                    report["warnings"].append(f"{prefix}: labeler_id_hash length != 64")

                # Validate score columns (1-5)
                for col in SCORE_COLUMNS:
                    val = row.get(col, "").strip()
                    if not val:
                        report["errors"].append(f"{prefix}: {col} is blank")
                        continue
                    success, parsed = parse_int_range(val, 1, 5)
                    if not success:
                        if parsed is None:
                            report["errors"].append(f"{prefix}: {col} is not an integer: '{val}'")
                        else:
                            report["errors"].append(f"{prefix}: {col} out of range (1-5): {parsed}")

                # Validate boolean columns
                for col in BOOLEAN_COLUMNS:
                    val = row.get(col, "").strip()
                    if not val:
                        report["errors"].append(f"{prefix}: {col} is blank")
                        continue
                    success, _ = parse_boolean(val)
                    if not success:
                        report["errors"].append(f"{prefix}: {col} invalid boolean value: '{val}'")

                # Validate confidence (1-3)
                conf = row.get(CONFIDENCE_COLUMN, "").strip()
                if conf:
                    success, parsed = parse_int_range(conf, 1, 3)
                    if not success:
                        if parsed is None:
                            report["errors"].append(f"{prefix}: {CONFIDENCE_COLUMN} is not an integer: '{conf}'")
                        else:
                            report["errors"].append(f"{prefix}: {CONFIDENCE_COLUMN} out of range (1-3): {parsed}")

    except Exception as e:
        report["errors"].append(f"Failed to read labels: {e}")
        return report

    report["total_labels"] = len(rows)

    # Check labels per holdout
    insufficient_labels = []
    for holdout_id, count in report["labels_per_holdout"].items():
        if count < 2:
            insufficient_labels.append(f"{holdout_id} ({count} label)")

    if insufficient_labels:
        report["warnings"].append(f"Holdout items with < 2 labels: {insufficient_labels}")

    report["checks"]["total_labels"] = len(rows)
    report["checks"]["unique_holdouts_labeled"] = len(report["labels_per_holdout"])
    report["valid"] = len(report["errors"]) == 0

    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate human labels CSV")
    parser.add_argument(
        "--labels",
        type=Path,
        default=Path("apps_lic/evals/holdout/human_labels.outreach_quality.v1.csv"),
        help="Path to labels CSV file",
    )
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

    report = validate_labels(args.labels, args.corpus)

    report_json = json.dumps(report, indent=2, ensure_ascii=False)

    if args.output:
        args.output.write_text(report_json, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(report_json)

    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
