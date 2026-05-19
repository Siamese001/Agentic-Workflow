#!/usr/bin/env python3
"""Validate apps_rg benchmark sample JSON files (schema + offline invariants)."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import jsonschema

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from _common import (
    human_scores_absent_or_null,
    iter_string_fields,
    load_json,
    resolve_glob,
    scan_pii,
    write_json_report,
)


def _validate_sample(
    path: Path,
    sample: dict,
    validator: jsonschema.Draft7Validator,
    *,
    allow_pending_pii: bool = False,
) -> list[str]:
    errors: list[str] = []
    for err in sorted(validator.iter_errors(sample), key=lambda e: list(e.path)):
        errors.append(f"schema: {err.message} at {list(err.path)}")

    if not allow_pending_pii and sample.get("pii_status") != "cleared":
        errors.append(f"pii_status must be cleared for calibration-eligible samples (got {sample.get('pii_status')!r})")
    if allow_pending_pii and sample.get("pii_status") not in ("cleared", "pending_review"):
        errors.append(f"pii_status must be cleared or pending_review (got {sample.get('pii_status')!r})")

    if sample.get("dataset_origin") == "public_bootstrap":
        errors.append("public_bootstrap cannot be used as calibration proof sample")

    ok_hs, hs_err = human_scores_absent_or_null(sample)
    if not ok_hs and hs_err:
        errors.append(hs_err)

    if sample.get("reviewer_role") is not None:
        errors.append("reviewer_role must be absent for synthetic examples")
    if sample.get("reviewer_confidence") is not None:
        errors.append("reviewer_confidence must be absent for synthetic examples")

    for field_path, text in iter_string_fields(sample):
        if field_path.endswith("human_notes"):
            continue
        for hit in scan_pii(text):
            if "[SYNTHETIC" in text or "Fictional" in text or "placeholder" in text.lower():
                continue
            errors.append(f"pii_heuristic:{hit['kind']} in {field_path}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate benchmark samples against JSON Schema.")
    parser.add_argument("--schema", required=True, help="Path to human_benchmark_schema.json")
    parser.add_argument("--samples-glob", required=True, help="Glob for sample JSON files")
    parser.add_argument("--out", required=True, help="Output validation report JSON path")
    parser.add_argument(
        "--profile",
        choices=("examples", "collected"),
        default="examples",
        help="examples=strict cleared PII; collected=allow pending_review",
    )
    args = parser.parse_args(argv)
    allow_pending_pii = args.profile == "collected"

    schema_path = Path(args.schema)
    schema = load_json(schema_path)
    validator = jsonschema.Draft7Validator(schema)
    sample_paths = resolve_glob(args.samples_glob)
    if not sample_paths:
        report = {
            "tool": "validate_benchmark_samples",
            "status": "FAIL",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "error": f"no samples matched glob: {args.samples_glob}",
            "samples": [],
        }
        write_json_report(Path(args.out), report)
        return 1

    results: list[dict] = []
    any_fail = False
    for path in sample_paths:
        sample = load_json(path)
        errs = _validate_sample(path, sample, validator, allow_pending_pii=allow_pending_pii)
        status = "PASS" if not errs else "FAIL"
        if errs:
            any_fail = True
        results.append(
            {
                "path": str(path.as_posix()),
                "benchmark_id": sample.get("benchmark_id"),
                "status": status,
                "errors": errs,
            }
        )

    report = {
        "tool": "validate_benchmark_samples",
        "status": "PASS" if not any_fail else "FAIL",
        "dry_run": True,
        "proof_eligible": False,
        "schema": str(schema_path.as_posix()),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sample_count": len(results),
        "samples": results,
    }
    write_json_report(Path(args.out), report)
    return 0 if not any_fail else 1


if __name__ == "__main__":
    sys.exit(main())
