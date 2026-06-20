"""Verifier — Source divergence (RTC-REQ-032).

Plan: ``.codex/plans/runtime-cert-hardened-w0-7e3c9a.md``

Non-negotiable rule §7:

  > If one verifier sees 0 requirements and another sees N, fail with
  > SOURCE_DIVERGENCE.

This verifier reads the canonical CSV, then independently inspects each
prior verifier's report (when emitted) to confirm every verifier saw the
same row count from the same CSV (sha256). If counts disagree, exit 2 with
``expected_fail_reason=SOURCE_DIVERGENCE``.

Inputs (looked for, optional)
-----------------------------

  - ``artifacts/certification/canonical_universe_manifest.json``
  - ``artifacts/certification/requirement_count_receipt.json``
  - ``artifacts/certification/schema_validation_report.json``
  - ``artifacts/certification/acceptance_legality_report.json``
  - ``artifacts/certification/artifact_payload_hash_report.json``

The verifier:

  1. Loads the canonical CSV via the SSOT loader -> baseline (row_count, sha256)
  2. For each report present, extracts its claimed (row_count, sha256)
  3. Asserts they all match the baseline
  4. Asserts the baseline row_count is non-zero AND equals
     ``CANONICAL_REQUIREMENT_COUNT``

Outputs
-------

  ``artifacts/certification/source_divergence_report.json``

Exit codes: 0 PASS, 2 SOURCE_DIVERGENCE, 3 HARNESS_ERROR.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from agentic_core.runtime.prove_requirements.matrix_loader import (  # noqa: E402
    CANONICAL_REQUIREMENT_COUNT,
    MatrixLoadError,
    load_matrix,
)

ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "certification"
DIVERGENCE_REPORT = ARTIFACTS_DIR / "source_divergence_report.json"

# (filename, key path describing how to read the count and hash from the report)
PEER_REPORTS = (
    {"name": "canonical_universe_manifest", "path": "canonical_universe_manifest.json",
     "count_key": "actual_count", "hash_key": "csv_sha256"},
    {"name": "requirement_count_receipt", "path": "requirement_count_receipt.json",
     "count_key": "actual_count", "hash_key": "csv_sha256"},
    {"name": "schema_validation_report", "path": "schema_validation_report.json",
     "count_key": "row_count", "hash_key": "csv_sha256"},
    {"name": "acceptance_legality_report", "path": "acceptance_legality_report.json",
     "count_key": "row_count", "hash_key": "csv_sha256"},
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )


def _read_peer(report_meta: dict) -> dict:
    p = ARTIFACTS_DIR / report_meta["path"]
    out = {
        "report": report_meta["name"],
        "path": str(p),
        "exists": p.exists(),
        "row_count": None,
        "csv_sha256": None,
        "load_error": None,
    }
    if not p.exists():
        return out
    try:
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
        out["row_count"] = data.get(report_meta["count_key"])
        out["csv_sha256"] = data.get(report_meta["hash_key"])
    except (json.JSONDecodeError, OSError) as exc:
        out["load_error"] = str(exc)
    return out


def main() -> int:
    print("[verify_source_divergence] loading canonical CSV (baseline)...")
    try:
        baseline = load_matrix()
    except MatrixLoadError as exc:
        report = {
            "verifier": "verify_source_divergence",
            "executed_at_utc": _now(),
            "status": "FAIL_CLOSED",
            "expected_fail_reason": "SOURCE_DIVERGENCE",
            "actual_fail_reason": f"baseline load failed: {exc}",
            "rule": "RTC-REQ-032",
            "baseline": None,
            "peers": [],
        }
        _write_json(DIVERGENCE_REPORT, report)
        return 2

    baseline_count = baseline.row_count
    baseline_hash = baseline.csv_sha256

    if baseline_count == 0:
        report = {
            "verifier": "verify_source_divergence",
            "executed_at_utc": _now(),
            "status": "FAIL_CLOSED",
            "expected_fail_reason": "SOURCE_DIVERGENCE",
            "actual_fail_reason": "baseline reports 0 rows",
            "rule": "RTC-REQ-032",
            "baseline_count": 0,
            "baseline_csv_sha256": baseline_hash,
            "peers": [],
        }
        _write_json(DIVERGENCE_REPORT, report)
        return 2

    if baseline_count != CANONICAL_REQUIREMENT_COUNT:
        report = {
            "verifier": "verify_source_divergence",
            "executed_at_utc": _now(),
            "status": "FAIL_CLOSED",
            "expected_fail_reason": "SOURCE_DIVERGENCE",
            "actual_fail_reason": (
                f"baseline_count={baseline_count} != "
                f"canonical={CANONICAL_REQUIREMENT_COUNT}"
            ),
            "rule": "RTC-REQ-032",
            "baseline_count": baseline_count,
            "baseline_csv_sha256": baseline_hash,
            "peers": [],
        }
        _write_json(DIVERGENCE_REPORT, report)
        return 2

    peers = [_read_peer(rm) for rm in PEER_REPORTS]
    divergences: list[dict] = []
    for p in peers:
        if not p["exists"]:
            continue  # not produced this run; not a divergence
        if p["load_error"] is not None:
            divergences.append({"report": p["report"], "kind": "LOAD_ERROR", "detail": p["load_error"]})
            continue
        if p["row_count"] is None:
            divergences.append({"report": p["report"], "kind": "ROW_COUNT_MISSING_FROM_REPORT"})
            continue
        if p["row_count"] != baseline_count:
            divergences.append({
                "report": p["report"],
                "kind": "ROW_COUNT_MISMATCH",
                "peer_count": p["row_count"],
                "baseline_count": baseline_count,
            })
        if p["csv_sha256"] and p["csv_sha256"] != baseline_hash:
            divergences.append({
                "report": p["report"],
                "kind": "CSV_SHA256_MISMATCH",
                "peer_sha256": p["csv_sha256"],
                "baseline_sha256": baseline_hash,
            })

    legal = len(divergences) == 0
    report = {
        "verifier": "verify_source_divergence",
        "executed_at_utc": _now(),
        "rule": "RTC-REQ-032",
        "status": "PASS" if legal else "FAIL_CLOSED",
        "expected_fail_reason": "" if legal else "SOURCE_DIVERGENCE",
        "actual_fail_reason": (
            "" if legal else f"{len(divergences)} divergence(s) across peer verifier reports"
        ),
        "baseline_count": baseline_count,
        "baseline_csv_sha256": baseline_hash,
        "canonical_count": CANONICAL_REQUIREMENT_COUNT,
        "peers": peers,
        "divergences": divergences,
    }
    _write_json(DIVERGENCE_REPORT, report)
    print(f"[verify_source_divergence] {report['status']}: peers={sum(1 for p in peers if p['exists'])} divergences={len(divergences)}")
    return 0 if legal else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"[verify_source_divergence] HARNESS_ERROR: {exc}", file=sys.stderr)
        sys.exit(3)
