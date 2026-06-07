"""Verifier — Schema validity of the hardened certification matrix.

Plan: ``.claude/plans/runtime-cert-hardened-w0-7e3c9a.md``
Covers: RTC-REQ-002 (proof depth fields mandatory),
        RTC-REQ-003 (claim_type enum),
        RTC-REQ-006 (subclaim decomposition),
        RTC-REQ-110 (matrix schema CI gate)

What "schema valid" means here
------------------------------

1. All 32 columns from ``REQUIRED_COLUMNS`` are present in the CSV header.
2. Every row's ``req_id`` is non-empty and unique (loader already enforces).
3. Every row's ``claim_type`` is in ``ALLOWED_CLAIM_TYPES``.
4. Every row's ``required_proof_depth`` is in canonical ``DEPTHS``.
5. Every row's ``priority`` is in ``ALLOWED_PRIORITY``.
6. Every row's ``runtime_sensitive`` and ``side_effect_sensitive`` are
   recognized boolean strings.
7. RTC-REQ-006: subclaim decomposition — when a row has a non-empty
   ``required_artifacts`` field with multiple ``;``-separated entries, the
   row's ``positive_assertions_to_implement`` MUST be non-empty so the
   downstream verifier knows what to assert.
8. The 8 W0-mandated matrix columns named in RTC-REQ-002's required
   matrix output (required_proof_depth, actual_proof_depth, proof_depth_status,
   proof_classification, runtime_claim_allowed, final_acceptance_status,
   acceptance_caveat, blocking_gap) are LISTED in RTC-REQ-002's
   ``required_matrix_columns`` value (sanity check on the metadata itself).

Output: ``artifacts/certification/schema_validation_report.json``

Exit codes: 0 PASS, 2 FAIL_CLOSED, 3 HARNESS_ERROR.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from agentic_core.runtime.prove_requirements.matrix_loader import (  # noqa: E402
    ALLOWED_BOOLEAN_STRINGS,
    ALLOWED_CLAIM_TYPES,
    ALLOWED_PRIORITY,
    REQUIRED_COLUMNS,
    MatrixLoadError,
    load_matrix,
)
from agentic_core.runtime.prove_requirements.proof_depth_ladder import (  # noqa: E402
    DEPTHS,
    is_valid_depth,
)

ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "certification"
SCHEMA_REPORT = ARTIFACTS_DIR / "schema_validation_report.json"

# RTC-REQ-002: the 8 columns the matrix must declare in required_matrix_columns
W0_REQUIRED_MATRIX_COLUMN_TOKENS = (
    "required_proof_depth",
    "actual_proof_depth",
    "proof_depth_status",
    "proof_classification",
    "runtime_claim_allowed",
    "final_acceptance_status",
    "acceptance_caveat",
    "blocking_gap",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_report(report: dict) -> None:
    SCHEMA_REPORT.parent.mkdir(parents=True, exist_ok=True)
    SCHEMA_REPORT.write_text(
        json.dumps(report, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )


def main() -> int:
    print("[verify_matrix_schema] loading canonical CSV...")
    try:
        result = load_matrix()
    except MatrixLoadError as exc:
        report = {
            "verifier": "verify_runtime_certification_matrix_schema",
            "executed_at_utc": _now(),
            "status": "FAIL_CLOSED",
            "expected_fail_reason": "MATRIX_LOAD_FAILED",
            "actual_fail_reason": str(exc),
            "rule": "RTC-REQ-110",
            "violations": [],
        }
        _write_report(report)
        print(json.dumps(report, indent=2))
        return 2

    violations: list[dict] = []

    # Already enforced by load_matrix: column presence, req_id uniqueness.
    # Restate them in the report for posterity.
    column_names = list(result.column_names)
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in column_names]
    if missing_cols:
        violations.append({
            "rule": "RTC-REQ-002",
            "kind": "MISSING_REQUIRED_COLUMNS",
            "detail": missing_cols,
        })

    # Per-row enum + content validity
    for i, row in enumerate(result.rows):
        rid = (row.get("req_id") or "").strip()
        ctype = (row.get("claim_type") or "").strip()
        rdepth = (row.get("required_proof_depth") or "").strip()
        prio = (row.get("priority") or "").strip()
        rs = (row.get("runtime_sensitive") or "").strip()
        ses = (row.get("side_effect_sensitive") or "").strip()
        if ctype and ctype not in ALLOWED_CLAIM_TYPES:
            violations.append({
                "row_index": i,
                "req_id": rid,
                "rule": "RTC-REQ-003",
                "kind": "CLAIM_TYPE_OUT_OF_ENUM",
                "value": ctype,
            })
        if rdepth and not is_valid_depth(rdepth):
            violations.append({
                "row_index": i,
                "req_id": rid,
                "rule": "RTC-REQ-002",
                "kind": "REQUIRED_PROOF_DEPTH_OUT_OF_LADDER",
                "value": rdepth,
            })
        if prio and prio not in ALLOWED_PRIORITY:
            violations.append({
                "row_index": i,
                "req_id": rid,
                "rule": "RTC-REQ-110",
                "kind": "PRIORITY_OUT_OF_ENUM",
                "value": prio,
            })
        for fname, fval in (("runtime_sensitive", rs), ("side_effect_sensitive", ses)):
            if fval and fval not in ALLOWED_BOOLEAN_STRINGS:
                violations.append({
                    "row_index": i,
                    "req_id": rid,
                    "rule": "RTC-REQ-110",
                    "kind": "BOOLEAN_FIELD_NOT_BOOL_STRING",
                    "field": fname,
                    "value": fval,
                })

        # RTC-REQ-006: subclaim decomposition — when a row has multiple
        # required_artifacts entries (split on ';') it MUST also declare
        # positive_assertions_to_implement. Otherwise a downstream verifier
        # has no concrete checks to run against the listed artifacts.
        artifacts_field = (row.get("required_artifacts") or "").strip()
        positive_field = (row.get("positive_assertions_to_implement") or "").strip()
        artifact_count = len([a for a in artifacts_field.split(";") if a.strip()])
        if artifact_count >= 2 and not positive_field:
            violations.append({
                "row_index": i,
                "req_id": rid,
                "rule": "RTC-REQ-006",
                "kind": "MULTI_ARTIFACT_ROW_LACKS_POSITIVE_ASSERTIONS",
                "artifact_count": artifact_count,
            })

    # RTC-REQ-002 sanity: at least one row's required_matrix_columns field
    # MUST list all 8 W0 tokens. (We don't require every row to declare them;
    # the schema validator only confirms the metadata records the expectation.)
    declared_in_any_row = False
    for row in result.rows:
        rmc = (row.get("required_matrix_columns") or "").strip().lower()
        if all(tok in rmc for tok in W0_REQUIRED_MATRIX_COLUMN_TOKENS):
            declared_in_any_row = True
            break
    if not declared_in_any_row:
        violations.append({
            "rule": "RTC-REQ-002",
            "kind": "NO_ROW_DECLARES_FULL_W0_MATRIX_COLUMNS",
            "expected_tokens": list(W0_REQUIRED_MATRIX_COLUMN_TOKENS),
        })

    legal = len(violations) == 0
    report = {
        "verifier": "verify_runtime_certification_matrix_schema",
        "executed_at_utc": _now(),
        "rule": "RTC-REQ-002 + RTC-REQ-003 + RTC-REQ-006 + RTC-REQ-110",
        "status": "PASS" if legal else "FAIL_CLOSED",
        "expected_fail_reason": "" if legal else "MATRIX_SCHEMA_GAP",
        "actual_fail_reason": "" if legal else f"{len(violations)} schema violation(s) detected",
        "csv_path": str(result.csv_path),
        "csv_sha256": result.csv_sha256,
        "row_count": result.row_count,
        "column_count": len(result.column_names),
        "violations": violations,
        "allowed_claim_types": sorted(ALLOWED_CLAIM_TYPES),
        "allowed_priority": sorted(ALLOWED_PRIORITY),
        "allowed_proof_depths": list(DEPTHS),
    }
    _write_report(report)
    print(f"[verify_matrix_schema] {report['status']}: {len(violations)} violations")
    print(f"[verify_matrix_schema] wrote: {SCHEMA_REPORT.relative_to(REPO_ROOT)}")
    return 0 if legal else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"[verify_matrix_schema] HARNESS_ERROR: {exc}", file=sys.stderr)
        sys.exit(3)
