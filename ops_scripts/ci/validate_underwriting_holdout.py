#!/usr/bin/env python3
"""Validate apps_underwriting_ai rationale judge holdout and provenance gate.

Exit codes:
  0 = schema valid and provenance accepted
  1 = schema/provenance failed
  2 = schema valid but provenance pending, so W1 is not complete
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required: pip install pyyaml") from exc

EXPECTED_DIMS = {
    "evidence_sufficiency",
    "feature_derivation_correctness",
    "policy_compliance",
    "explainability",
    "fairness",
}
REQUIRED_EXAMPLE_FIELDS = {
    "decision_id",
    "dim_id",
    "rationale_text",
    "human_score",
    "labeler_id",
    "labeled_at",
    "evidence_refs",
}
REQUIRED_ATTESTATION_TRUE_FIELDS = {
    "independent_human_review_confirmed",
    "qualified_underwriting_analyst_confirmed",
    "no_pii_confirmed",
    "no_real_applicant_data_confirmed",
    "no_live_lender_thresholds_confirmed",
    "no_llm_or_cascade_authored_labels_confirmed",
}
PII_PATTERNS = {
    "ssn_like": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "email_like": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "phone_like": re.compile(r"(?<!\d)(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}(?!\d)"),
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"{path} must contain a YAML object")
    return loaded


def scan_pii(text: str) -> list[str]:
    hits: list[str] = []
    for name, pattern in PII_PATTERNS.items():
        if pattern.search(text):
            hits.append(name)
    return hits


def validate_holdout(holdout_path: Path) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    data = load_yaml(holdout_path)
    examples = data.get("examples")
    if not isinstance(examples, list):
        return ["examples must be a list"], warnings, {"example_count": 0}

    if len(examples) != 100:
        errors.append(f"expected 100 examples, found {len(examples)}")

    ids: list[str] = []
    dims: list[str] = []
    all_gt_equals_human = True
    labelers: set[str] = set()

    for i, row in enumerate(examples):
        prefix = f"examples[{i}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix} must be an object")
            continue

        missing = sorted(REQUIRED_EXAMPLE_FIELDS - row.keys())
        if missing:
            errors.append(f"{prefix} missing required fields: {missing}")

        decision_id = row.get("decision_id")
        if not isinstance(decision_id, str) or not decision_id.strip():
            errors.append(f"{prefix}.decision_id must be non-empty string")
        else:
            ids.append(decision_id)

        dim_id = row.get("dim_id")
        if dim_id not in EXPECTED_DIMS:
            errors.append(f"{prefix}.dim_id invalid: {dim_id!r}")
        else:
            dims.append(dim_id)

        human_score = row.get("human_score")
        if not isinstance(human_score, (int, float)) or not 0.0 <= float(human_score) <= 1.0:
            errors.append(f"{prefix}.human_score must be numeric between 0.0 and 1.0")

        labeler_id = row.get("labeler_id")
        if not isinstance(labeler_id, str) or not labeler_id.strip():
            errors.append(f"{prefix}.labeler_id must be non-empty string")
        else:
            labelers.add(labeler_id)

        evidence_refs = row.get("evidence_refs")
        if not isinstance(evidence_refs, list):
            errors.append(f"{prefix}.evidence_refs must be a list")

        rationale_text = row.get("rationale_text")
        if not isinstance(rationale_text, str) or not rationale_text.strip():
            errors.append(f"{prefix}.rationale_text must be non-empty string")
        elif scan_pii(rationale_text):
            errors.append(f"{prefix}.rationale_text contains possible PII: {scan_pii(rationale_text)}")

        if "ground_truth_score" in row and row.get("ground_truth_score") != row.get("human_score"):
            all_gt_equals_human = False

    duplicate_ids = sorted([item for item, count in Counter(ids).items() if count > 1])
    if duplicate_ids:
        errors.append(f"duplicate decision_id values: {duplicate_ids[:10]}")

    dim_counts = Counter(dims)
    for dim in sorted(EXPECTED_DIMS):
        if dim_counts.get(dim, 0) != 20:
            errors.append(f"expected 20 examples for {dim}, found {dim_counts.get(dim, 0)}")

    if all_gt_equals_human and examples:
        warnings.append("HOLDOUT_GROUND_TRUTH_EQUALS_HUMAN_SCORE")

    summary = {
        "example_count": len(examples),
        "dimension_counts": dict(sorted(dim_counts.items())),
        "unique_decision_ids": len(set(ids)),
        "labeler_ids": sorted(labelers),
        "holdout_sha256": sha256_file(holdout_path),
    }
    return errors, warnings, summary


def validate_provenance(provenance_path: Path | None, holdout_sha: str) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    summary: dict[str, Any] = {"provenance_status": "MISSING"}

    if provenance_path is None or not provenance_path.exists():
        errors.append("provenance file missing; W1 cannot be COMPLETE")
        return errors, warnings, summary

    data = load_yaml(provenance_path)
    status = data.get("holdout_dataset_status")
    summary["provenance_status"] = status

    expected_sha = data.get("holdout_file_sha256")
    if expected_sha != holdout_sha:
        errors.append(f"provenance holdout_file_sha256 mismatch: expected {holdout_sha}, found {expected_sha}")

    if status != "VERIFIED_ANALYST_ATTESTED":
        errors.append(f"holdout_dataset_status is {status!r}; expected VERIFIED_ANALYST_ATTESTED for W1_COMPLETE")

    attestation = data.get("attestation")
    if not isinstance(attestation, dict):
        errors.append("attestation must be an object")
        return errors, warnings, summary

    for field in sorted(REQUIRED_ATTESTATION_TRUE_FIELDS):
        if attestation.get(field) is not True:
            errors.append(f"attestation.{field} must be true for W1_COMPLETE")

    for field in ["attestation_owner", "attestation_owner_role", "attestation_date", "analyst_labeling_or_review_method", "calibration_method"]:
        if not attestation.get(field):
            errors.append(f"attestation.{field} is required for W1_COMPLETE")

    return errors, warnings, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--holdout", default="apps_underwriting_ai/holdout/rationale_judge_holdout.yaml")
    parser.add_argument("--provenance", default="apps_underwriting_ai/holdout/rationale_judge_holdout_provenance.yaml")
    parser.add_argument("--require-provenance", action="store_true")
    parser.add_argument(
        "--require-anthropic-key",
        action="store_true",
        help="Opt-in diagnostic only. ANTHROPIC_API_KEY is already configured in CI secrets "
             "and local .env — do not use this flag in standard CI gates.",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    holdout_path = Path(args.holdout)
    provenance_path = Path(args.provenance) if args.provenance else None

    errors, warnings, summary = validate_holdout(holdout_path)
    prov_errors: list[str] = []
    prov_warnings: list[str] = []
    prov_summary: dict[str, Any] = {}

    if args.require_provenance:
        prov_errors, prov_warnings, prov_summary = validate_provenance(provenance_path, summary.get("holdout_sha256", ""))

    if args.require_anthropic_key and not os.environ.get("ANTHROPIC_API_KEY"):
        prov_errors.append("ANTHROPIC_API_KEY not found in environment (opt-in check via --require-anthropic-key)")

    all_errors = errors + prov_errors
    all_warnings = warnings + prov_warnings
    status = "W1_COMPLETE" if not all_errors and args.require_provenance else "W1_SCHEMA_VALID"
    if args.require_provenance and all_errors:
        status = "W1_PROVENANCE_PENDING" if not errors else "W1_BLOCKED"

    report = {
        "status": status,
        "errors": all_errors,
        "warnings": all_warnings,
        "summary": {**summary, **prov_summary},
    }

    if args.as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"status: {status}")
        for key, value in report["summary"].items():
            print(f"{key}: {value}")
        if all_warnings:
            print("warnings:")
            for warning in all_warnings:
                print(f"  - {warning}")
        if all_errors:
            print("errors:")
            for error in all_errors:
                print(f"  - {error}")

    if all_errors:
        return 2 if status == "W1_PROVENANCE_PENDING" else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
