"""Verifier — Acceptance legality + composition non-promotion.

Plan: ``.claude/plans/runtime-cert-hardened-w0-7e3c9a.md``
Covers: RTC-REQ-004 (acceptance legality),
        RTC-REQ-005 (DOC_REFERENCE_ONLY cannot claim runtime),
        RTC-REQ-111 (acceptance legality CI gate),
        RTC-REQ-127 (COMPOSITION_PROOF cannot promote),
        RTC-REQ-034 (downgraded rows report).

W0-only behavior
----------------

W0 has no per-row evidence yet (no semantic-cache evidence, no OTel export,
no replay bundles). Therefore every row's ``actual_proof_depth`` defaults to
``E0_REQUIREMENT_TEXT`` and ``final_acceptance_status=PENDING``.

The acceptance verifier MUST still pass under those defaults — PENDING never
violates legality rules. What it MUST detect is the *forbidden combinations*:

  - Any row whose metadata declares ``final_acceptance_status=ACCEPTED`` but
    whose ``actual_proof_depth`` is weaker than ``required_proof_depth``.
  - DOC_REFERENCE_ONLY rows that carry ``runtime_claim_allowed=True``.
  - Rows with ``actual=E5_COMPOSITION_PROOF`` and ``required ∈ {E6, E7, E8, E9}``.

Today the source CSV doesn't carry a per-row ``actual_proof_depth`` column,
so the W0 baseline never trips ACCEPTED-with-weak-proof — the rule fires
ONLY when a future wave (or a misconfigured external pipeline) populates an
``actual_proof_depth`` override.

Output
------

  - ``artifacts/certification/acceptance_legality_report.json`` — full per-row
    verdict table
  - ``artifacts/certification/downgraded_rows_report.json`` — RTC-REQ-034:
    rows whose metadata-implied acceptance is downgraded by the validator
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from agentic_core.runtime.prove_requirements.acceptance_validator import (  # noqa: E402
    apply_to_matrix,
)
from agentic_core.runtime.prove_requirements.matrix_loader import (  # noqa: E402
    MatrixLoadError,
    load_matrix,
)

ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "certification"
ACCEPTANCE_REPORT = ARTIFACTS_DIR / "acceptance_legality_report.json"
DOWNGRADED_REPORT = ARTIFACTS_DIR / "downgraded_rows_report.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )


def _load_overrides() -> dict:
    """Read optional runtime evidence overrides from a sidecar JSON file.

    File path: ``artifacts/certification/runtime_evidence_overrides.json``.
    Schema (all fields optional):

      {
        "actual_proof_depth": {"RTC-REQ-001": "E2_STATIC_CHECK", ...},
        "final_acceptance_status": {"RTC-REQ-001": "ACCEPTED", ...},
        "acceptance_caveat": {"...": "..."},
        "blocking_gap": {"...": "..."}
      }

    W0 never produces this sidecar; future waves do. The verifier picks it
    up if present.
    """
    sidecar = ARTIFACTS_DIR / "runtime_evidence_overrides.json"
    if not sidecar.exists():
        return {}
    try:
        with sidecar.open("r", encoding="utf-8") as f:
            return json.load(f) or {}
    except (json.JSONDecodeError, OSError):
        return {}


def main() -> int:
    print("[verify_acceptance] loading canonical CSV...")
    try:
        result = load_matrix()
    except MatrixLoadError as exc:
        report = {
            "verifier": "verify_runtime_certification_acceptance",
            "executed_at_utc": _now(),
            "status": "FAIL_CLOSED",
            "expected_fail_reason": "MATRIX_LOAD_FAILED",
            "actual_fail_reason": str(exc),
            "rule": "RTC-REQ-111",
        }
        _write_json(ACCEPTANCE_REPORT, report)
        return 2

    overrides = _load_overrides()
    verdicts = apply_to_matrix(
        result.rows,
        actual_proof_depth_overrides=overrides.get("actual_proof_depth"),
        final_acceptance_status_overrides=overrides.get("final_acceptance_status"),
        acceptance_caveat_overrides=overrides.get("acceptance_caveat"),
        blocking_gap_overrides=overrides.get("blocking_gap"),
    )

    legal_count = sum(1 for v in verdicts if v.legal)
    illegal_count = sum(1 for v in verdicts if not v.legal)
    by_violation: dict[str, int] = {}
    for v in verdicts:
        for r in v.rule_violations:
            by_violation[r] = by_violation.get(r, 0) + 1

    final_legal = illegal_count == 0
    report = {
        "verifier": "verify_runtime_certification_acceptance",
        "executed_at_utc": _now(),
        "rule": "RTC-REQ-004 + RTC-REQ-005 + RTC-REQ-111 + RTC-REQ-127",
        "status": "PASS" if final_legal else "FAIL_CLOSED",
        "expected_fail_reason": "" if final_legal else "ACCEPTANCE_LEGALITY_VIOLATIONS",
        "actual_fail_reason": "" if final_legal else f"{illegal_count} row(s) violated acceptance rules",
        "csv_sha256": result.csv_sha256,
        "row_count": result.row_count,
        "legal_count": legal_count,
        "illegal_count": illegal_count,
        "violation_distribution": by_violation,
        "verdicts": [v.to_row() for v in verdicts],
        "overrides_applied": bool(overrides),
    }
    _write_json(ACCEPTANCE_REPORT, report)

    # RTC-REQ-034: downgraded rows report
    downgraded = [v.to_row() for v in verdicts if not v.legal]
    downgrade_report = {
        "verifier": "verify_runtime_certification_acceptance",
        "executed_at_utc": _now(),
        "rule": "RTC-REQ-034",
        "downgraded_count": len(downgraded),
        "downgraded_rows": downgraded,
    }
    _write_json(DOWNGRADED_REPORT, downgrade_report)

    print(f"[verify_acceptance] {report['status']}: legal={legal_count} illegal={illegal_count}")
    print(f"[verify_acceptance] wrote: {ACCEPTANCE_REPORT.relative_to(REPO_ROOT)}")
    print(f"[verify_acceptance] wrote: {DOWNGRADED_REPORT.relative_to(REPO_ROOT)}")
    return 0 if final_legal else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"[verify_acceptance] HARNESS_ERROR: {exc}", file=sys.stderr)
        sys.exit(3)
