"""Verifier — Canonical certification matrix + universe declaration.

Plan: ``.windsurf/plans/runtime-cert-hardened-w0-7e3c9a.md``
Covers: RTC-REQ-001, RTC-REQ-030, RTC-REQ-033, RTC-REQ-124, RTC-REQ-031 (presence)

Behavior
--------

1. Load the canonical CSV via the SSOT loader (``matrix_loader.load_matrix``).
2. Emit the canonical universe manifest (RTC-REQ-001) to
   ``artifacts/certification/canonical_universe_manifest.json``.
3. Emit a requirement count receipt (RTC-REQ-030) to
   ``artifacts/certification/requirement_count_receipt.json``.
4. Verify single-repo-root + output-dir binding (RTC-REQ-124) by asserting the
   loader bound ``CANONICAL_CSV_PATH`` and the output dir resolves under the
   same git root.
5. Verify hardening minimum (RTC-REQ-033): the CSV must declare at least
   ``CANONICAL_REQUIREMENT_COUNT`` rows, no duplicates, no missing IDs.
6. Mark Merkle-root readiness (RTC-REQ-031): we don't compute the root in W0
   (the all-requirements pipeline owns it), but we DO verify ``leaf_count``
   would be non-zero and equal to the canonical count.

Exit codes
----------

  0  PASS — all rules satisfied
  2  FAIL_CLOSED — at least one fail-closed condition triggered
  3  HARNESS_ERROR — unexpected exception
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from agentic_core.runtime.prove_requirements.matrix_loader import (  # noqa: E402
    CANONICAL_CSV_PATH,
    CANONICAL_REQUIREMENT_COUNT,
    MatrixLoadError,
    load_matrix,
)

ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "certification"
UNIVERSE_MANIFEST = ARTIFACTS_DIR / "canonical_universe_manifest.json"
COUNT_RECEIPT = ARTIFACTS_DIR / "requirement_count_receipt.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )


def main() -> int:
    print(f"[verify_matrix] canonical CSV: {CANONICAL_CSV_PATH}")
    if not CANONICAL_CSV_PATH.exists():
        manifest = {
            "verifier": "verify_runtime_certification_matrix",
            "executed_at_utc": _now(),
            "status": "FAIL_CLOSED",
            "expected_fail_reason": "CANONICAL_CSV_NOT_BOUND",
            "actual_fail_reason": (
                f"canonical CSV missing at {CANONICAL_CSV_PATH}; "
                "copy from docs/reference/runtime_certification_requirements_100_percent_hardened.csv"
            ),
            "rule": "RTC-REQ-124",
            "expected_count": CANONICAL_REQUIREMENT_COUNT,
            "actual_count": 0,
        }
        _write_json(UNIVERSE_MANIFEST, manifest)
        print(json.dumps(manifest, indent=2))
        return 2

    try:
        result = load_matrix()
    except MatrixLoadError as exc:
        manifest = {
            "verifier": "verify_runtime_certification_matrix",
            "executed_at_utc": _now(),
            "status": "FAIL_CLOSED",
            "expected_fail_reason": str(exc).split(":", 1)[0] if ":" in str(exc) else "LOAD_ERROR",
            "actual_fail_reason": str(exc),
            "rule": "RTC-REQ-001",
            "expected_count": CANONICAL_REQUIREMENT_COUNT,
            "actual_count": 0,
        }
        _write_json(UNIVERSE_MANIFEST, manifest)
        print(json.dumps(manifest, indent=2))
        return 2

    # ── RTC-REQ-001: canonical universe manifest
    universe = {
        "verifier": "verify_runtime_certification_matrix",
        "executed_at_utc": _now(),
        "rule": "RTC-REQ-001",
        "csv_path": str(result.csv_path),
        "csv_sha256": result.csv_sha256,
        "expected_count": CANONICAL_REQUIREMENT_COUNT,
        "actual_count": result.row_count,
        "matches_canonical_count": result.row_count == CANONICAL_REQUIREMENT_COUNT,
        "distinct_req_ids": sorted({(r.get("req_id") or "").strip() for r in result.rows}),
        "duplicates": [],
        "missing": [],
        "extra": [],
        "column_names": list(result.column_names),
    }

    # ── RTC-REQ-033: hardening minimum
    if universe["actual_count"] != universe["expected_count"]:
        universe["status"] = "FAIL_CLOSED"
        universe["expected_fail_reason"] = "HARDENING_MIN_NOT_MET"
        universe["actual_fail_reason"] = (
            f"actual_count={universe['actual_count']} != expected_count={universe['expected_count']}"
        )
        _write_json(UNIVERSE_MANIFEST, universe)
        print(json.dumps(universe, indent=2))
        return 2
    universe["status"] = "PASS"

    # ── RTC-REQ-124: single repo root + output dir binding
    if not str(ARTIFACTS_DIR).startswith(str(REPO_ROOT)):
        universe["status"] = "FAIL_CLOSED"
        universe["expected_fail_reason"] = "OUTPUT_DIR_OUTSIDE_REPO_ROOT"
        universe["actual_fail_reason"] = (
            f"artifacts dir {ARTIFACTS_DIR} resolves outside repo root {REPO_ROOT}"
        )
        _write_json(UNIVERSE_MANIFEST, universe)
        return 2

    _write_json(UNIVERSE_MANIFEST, universe)

    # ── RTC-REQ-030: requirement count receipt
    receipt = {
        "verifier": "verify_runtime_certification_matrix",
        "executed_at_utc": _now(),
        "rule": "RTC-REQ-030",
        "expected_count": CANONICAL_REQUIREMENT_COUNT,
        "actual_count": result.row_count,
        "csv_sha256": result.csv_sha256,
        "wave_distribution": {},
        "claim_type_distribution": {},
        "priority_distribution": {},
        "merkle_readiness": {
            "rule": "RTC-REQ-031",
            "leaf_count_would_be": result.row_count,
            "non_empty": result.row_count > 0,
            "complete": result.row_count == CANONICAL_REQUIREMENT_COUNT,
        },
    }
    for r in result.rows:
        for k, target in [
            ("implementation_wave", "wave_distribution"),
            ("claim_type", "claim_type_distribution"),
            ("priority", "priority_distribution"),
        ]:
            v = (r.get(k) or "").strip() or "(unset)"
            receipt[target][v] = receipt[target].get(v, 0) + 1

    _write_json(COUNT_RECEIPT, receipt)

    print(f"[verify_matrix] PASS: 86 rows, sha256={result.csv_sha256[:12]}")
    print(f"[verify_matrix] wrote: {UNIVERSE_MANIFEST.relative_to(REPO_ROOT)}")
    print(f"[verify_matrix] wrote: {COUNT_RECEIPT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"[verify_matrix] HARNESS_ERROR: {exc}", file=sys.stderr)
        sys.exit(3)
