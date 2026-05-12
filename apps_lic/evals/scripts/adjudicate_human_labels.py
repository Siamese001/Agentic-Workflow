#!/usr/bin/env python3
"""Adjudicate human labels and produce ground truth scores.

Groups labels by holdout_id, computes median per dimension, normalizes 1-5 to 0.0-1.0.
Flags adjudication_required when:
- max labeler disagreement >= 2 on any subjective dimension
- guardrail flags conflict across labelers
- any labeler confidence <= 1

Writes adjudicated_scores CSV.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from pathlib import Path
from typing import Any


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

OUTPUT_COLUMNS = [
    "holdout_id",
    "n_response_likelihood_labels",
    "n_brand_voice_labels",
    "median_response_likelihood_1_5",
    "median_brand_voice_1_5",
    "median_personalization_quality_1_5",
    "median_ask_clarity_low_friction_1_5",
    "n_fake_personalization_true",
    "n_fabricated_relationship_true",
    "n_unsupported_company_fact_true",
    "n_unsupported_recipient_fact_true",
    "n_confidential_leakage_true",
    "n_sensitive_targeting_true",
    "n_spammy_or_hype_true",
    "n_channel_length_violation_true",
    "adjudication_required",
    "disagreement_max",
    "reason_for_review",
    "normalized_response_likelihood_0_1",
    "normalized_brand_voice_0_1",
    "normalized_personalization_quality_0_1",
    "normalized_ask_clarity_0_1",
]


def parse_boolean(value: str) -> bool:
    """Parse boolean string."""
    normalized = value.strip().lower()
    return normalized in ("true", "1", "yes", "t")


def parse_int_safe(value: str) -> int | None:
    """Parse integer safely."""
    try:
        return int(value.strip())
    except (ValueError, AttributeError):
        return None


def normalize_1_5_to_0_1(value: int) -> float:
    """Normalize 1-5 scale to 0.0-1.0."""
    return (value - 1) / 4.0


def compute_median(values: list[int]) -> int | None:
    """Compute median, rounding to nearest int."""
    if not values:
        return None
    # Use high median for consistent behavior: median([3, 5]) = 4
    return int(statistics.median_high(values))


def load_labels(labels_path: Path) -> dict[str, list[dict]]:
    """Load labels grouped by holdout_id."""
    labels_by_holdout: dict[str, list[dict]] = {}

    with labels_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            holdout_id = row.get("holdout_id", "").strip()
            if not holdout_id:
                continue
            if holdout_id not in labels_by_holdout:
                labels_by_holdout[holdout_id] = []
            labels_by_holdout[holdout_id].append(row)

    return labels_by_holdout


def adjudicate(labels_by_holdout: dict[str, list[dict]]) -> list[dict]:
    """Adjudicate labels and return output rows."""
    results: list[dict] = []

    for holdout_id, labels in sorted(labels_by_holdout.items()):
        row: dict[str, Any] = {"holdout_id": holdout_id}

        # Collect scores per dimension
        scores: dict[str, list[int]] = {col: [] for col in SCORE_COLUMNS}
        for label in labels:
            for col in SCORE_COLUMNS:
                val = parse_int_safe(label.get(col, ""))
                if val is not None and 1 <= val <= 5:
                    scores[col].append(val)

        # Count labels per dimension
        row["n_response_likelihood_labels"] = len(scores["response_likelihood_1_5"])
        row["n_brand_voice_labels"] = len(scores["brand_voice_1_5"])

        # Compute medians
        medians: dict[str, int | None] = {}
        for col in SCORE_COLUMNS:
            med = compute_median(scores[col])
            medians[col] = med
            row[f"median_{col}"] = med

        # Normalize medians
        for col in SCORE_COLUMNS:
            med = medians[col]
            if med is not None:
                short_name = col.replace("_1_5", "").replace("ask_clarity_low_friction", "ask_clarity")
                row[f"normalized_{short_name}_0_1"] = round(normalize_1_5_to_0_1(med), 3)
            else:
                short_name = col.replace("_1_5", "").replace("ask_clarity_low_friction", "ask_clarity")
                row[f"normalized_{short_name}_0_1"] = None

        # Count boolean flags
        flag_counts: dict[str, int] = {col: 0 for col in BOOLEAN_COLUMNS}
        for label in labels:
            for col in BOOLEAN_COLUMNS:
                val = label.get(col, "").strip()
                if val and parse_boolean(val):
                    flag_counts[col] += 1

        for col in BOOLEAN_COLUMNS:
            short_name = col.replace("_flag", "").replace("spammy_or_hype_language", "spammy_or_hype")
            row[f"n_{short_name}_true"] = flag_counts[col]

        # Check for adjudication triggers
        adjudication_required = False
        reasons: list[str] = []
        max_disagreement = 0

        # Score disagreement >= 2
        for col in SCORE_COLUMNS:
            if len(scores[col]) >= 2:
                min_score = min(scores[col])
                max_score = max(scores[col])
                disagreement = max_score - min_score
                max_disagreement = max(max_disagreement, disagreement)
                if disagreement >= 2:
                    adjudication_required = True
                    reasons.append(f"{col} disagreement >= 2")

        # Guardrail flag conflicts
        for col in BOOLEAN_COLUMNS:
            count = flag_counts[col]
            n_labels = len(labels)
            if 0 < count < n_labels:  # Some true, some false
                adjudication_required = True
                reasons.append(f"{col} conflict across labelers")

        # Low confidence labels
        for label in labels:
            conf = parse_int_safe(label.get("labeler_confidence_1_3", ""))
            if conf is not None and conf <= 1:
                adjudication_required = True
                reasons.append("labeler confidence <= 1")
                break

        row["adjudication_required"] = adjudication_required
        row["disagreement_max"] = max_disagreement
        row["reason_for_review"] = "; ".join(reasons) if reasons else ""

        results.append(row)

    return results


def write_adjudicated_csv(output_path: Path, rows: list[dict]) -> None:
    """Write adjudicated scores CSV."""
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for row in rows:
            # Ensure all columns present
            for col in OUTPUT_COLUMNS:
                if col not in row:
                    row[col] = ""
            writer.writerow(row)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Adjudicate human labels")
    parser.add_argument(
        "--labels",
        type=Path,
        default=Path("apps_lic/evals/holdout/human_labels.outreach_quality.v1.csv"),
        help="Path to input labels CSV",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("apps_lic/evals/holdout/adjudicated_scores.outreach_quality.v1.csv"),
        help="Path to output adjudicated scores CSV",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Optional JSON report path",
    )
    args = parser.parse_args(argv)

    if not args.labels.exists():
        print(f"Error: Labels file not found: {args.labels}", file=sys.stderr)
        return 1

    # Load and adjudicate
    labels_by_holdout = load_labels(args.labels)

    if not labels_by_holdout:
        print("No labels found in input file", file=sys.stderr)
        return 1

    results = adjudicate(labels_by_holdout)

    # Write output
    write_adjudicated_csv(args.output, results)
    print(f"Adjudicated scores written to {args.output}")

    # Generate report
    n_requiring_review = sum(1 for r in results if r.get("adjudication_required"))
    report: dict[str, Any] = {
        "total_items": len(results),
        "items_requiring_adjudication": n_requiring_review,
        "items_ready": len(results) - n_requiring_review,
        "input_labels": sum(len(v) for v in labels_by_holdout.values()),
        "unique_holdouts": len(labels_by_holdout),
        "output_path": str(args.output),
    }

    report_json = json.dumps(report, indent=2)
    if args.report:
        args.report.write_text(report_json, encoding="utf-8")
        print(f"Report written to {args.report}")
    else:
        print(report_json)

    return 0


if __name__ == "__main__":
    sys.exit(main())
