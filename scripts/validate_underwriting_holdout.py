"""Validate the apps_underwriting_ai rationale-judge holdout dataset.

Checks schema, provenance, and attestation integrity for the holdout YAML
used by the underwriting rationale judge calibration pipeline.

Usage::

    python scripts/validate_underwriting_holdout.py \\
        --holdout path/to/rationale_judge_holdout.yaml \\
        --provenance path/to/rationale_judge_holdout_provenance.yaml

Exit codes:
    0 — all validations passed
    1 — validation errors present
    2 — file not found or YAML parse error

Plan: apps-underwriting-ai-kill-parallel-pipelines-a3f7e2 W4 (re-creation).
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Any

import yaml


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

REQUIRED_EXAMPLE_FIELDS = (
    "decision_id",
    "dim_id",
    "evidence_refs",
    "ground_truth_score",
    "human_score",
    "labeled_at",
    "labeler_id",
    "rationale_text",
)

VALID_DIMS = (
    "evidence_sufficiency",
    "feature_derivation_correctness",
    "policy_compliance",
    "explainability",
    "fairness",
)


def sha256_file(path: Path) -> str:
    """Return hex SHA-256 of the file at *path*."""
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return digest


def validate_holdout(
    holdout_path: Path,
) -> tuple[list[str], list[str], dict[str, Any]]:
    """Validate a holdout YAML file.

    Returns:
        (errors, warnings, summary) — errors is empty on success.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not holdout_path.exists():
        errors.append(f"holdout file missing: {holdout_path}")
        return errors, warnings, {}

    try:
        data = yaml.safe_load(holdout_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        errors.append(f"YAML parse error: {exc}")
        return errors, warnings, {}

    examples: list[dict] = data.get("examples") or []

    if not examples:
        errors.append("holdout file contains no examples")
        return errors, warnings, {}

    seen_ids: set[str] = set()
    dim_counts: dict[str, int] = {}

    for i, ex in enumerate(examples):
        # Required fields
        missing = [f for f in REQUIRED_EXAMPLE_FIELDS if f not in ex]
        if missing:
            errors.append(
                f"example[{i}] missing required fields: {', '.join(missing)}"
            )

        # decision_id uniqueness
        did = ex.get("decision_id", "")
        if did in seen_ids:
            errors.append(f"duplicate decision_id: {did!r} at example[{i}]")
        seen_ids.add(did)

        # human_score range
        hs = ex.get("human_score")
        if hs is not None:
            try:
                hs_f = float(hs)
                if not (0.0 <= hs_f <= 1.0):
                    errors.append(
                        f"example[{i}] human_score must be numeric in [0,1], got {hs}"
                    )
            except (TypeError, ValueError):
                errors.append(
                    f"example[{i}] human_score must be numeric in [0,1], got {hs!r}"
                )

        # labeler_id non-empty
        lid = ex.get("labeler_id", "")
        if not lid:
            errors.append(f"example[{i}] labeler_id must be non-empty")

        # dim tracking
        dim = ex.get("dim_id", "")
        dim_counts[dim] = dim_counts.get(dim, 0) + 1

    # Ground-truth == human_score warning (all-or-none heuristic)
    gt_eq_hs = all(
        ex.get("ground_truth_score") == ex.get("human_score")
        for ex in examples
        if "ground_truth_score" in ex and "human_score" in ex
    )
    if gt_eq_hs:
        warnings.append("HOLDOUT_GROUND_TRUTH_EQUALS_HUMAN_SCORE")

    summary: dict[str, Any] = {
        "example_count": len(examples),
        "dimension_counts": dim_counts,
        "unique_ids": len(seen_ids),
    }
    return errors, warnings, summary


def validate_provenance(
    provenance_path: Path,
    expected_sha256: str,
) -> tuple[list[str], list[str], dict[str, Any]]:
    """Validate a provenance YAML file against the expected holdout sha256.

    Returns:
        (errors, warnings, summary) — errors is empty on success.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not provenance_path.exists():
        errors.append(f"provenance file missing: {provenance_path}")
        return errors, warnings, {}

    try:
        data = yaml.safe_load(provenance_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        errors.append(f"provenance YAML parse error: {exc}")
        return errors, warnings, {}

    # SHA-256 integrity check
    recorded_sha = data.get("holdout_file_sha256", "")
    if recorded_sha != expected_sha256:
        errors.append(
            f"holdout_file_sha256 mismatch: recorded={recorded_sha!r} "
            f"expected={expected_sha256!r}"
        )

    # Status must be VERIFIED_ANALYST_ATTESTED
    status = data.get("holdout_dataset_status", "")
    if status != "VERIFIED_ANALYST_ATTESTED":
        errors.append(
            f"holdout_dataset_status must be 'VERIFIED_ANALYST_ATTESTED', got {status!r}"
        )

    attestation: dict = data.get("attestation") or {}
    required_bool_flags = (
        "independent_human_review_confirmed",
        "qualified_underwriting_analyst_confirmed",
        "no_pii_confirmed",
        "no_real_applicant_data_confirmed",
        "no_live_lender_thresholds_confirmed",
        "no_llm_or_cascade_authored_labels_confirmed",
    )
    for flag in required_bool_flags:
        if not attestation.get(flag):
            errors.append(f"attestation.{flag} must be True")

    summary: dict[str, Any] = {
        "provenance_status": status,
        "sha256_match": recorded_sha == expected_sha256,
    }
    return errors, warnings, summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="validate_underwriting_holdout",
        description="Validate the underwriting rationale-judge holdout dataset.",
    )
    parser.add_argument("--holdout", required=True, help="Path to holdout YAML.")
    parser.add_argument(
        "--provenance", default=None, help="Path to provenance YAML (optional)."
    )
    args = parser.parse_args(argv)

    holdout_path = Path(args.holdout)
    errors, warnings, summary = validate_holdout(holdout_path)

    if warnings:
        for w in warnings:
            print(f"WARNING: {w}", file=sys.stderr)

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(f"holdout OK — {summary['example_count']} examples")

    if args.provenance:
        sha = sha256_file(holdout_path)
        p_errors, p_warnings, p_summary = validate_provenance(Path(args.provenance), sha)
        if p_warnings:
            for w in p_warnings:
                print(f"WARNING: {w}", file=sys.stderr)
        if p_errors:
            for e in p_errors:
                print(f"ERROR: {e}", file=sys.stderr)
            return 1
        print(f"provenance OK — status={p_summary.get('provenance_status')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
