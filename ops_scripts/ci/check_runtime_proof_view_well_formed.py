#!/usr/bin/env python3
"""Gate G-RUNTIME-PROOF-VIEW-WELL-FORMED — assert v_runtime_proof rows are valid.

ADG consumer mode: ``proof`` — this gate is enforcement-grade.

Per ADR-074 (Runtime Bucket as OTEL View) and the 2026-04-29 user pivot,
the ``v_runtime_proof`` table is the runtime bucket of the three-bucket
authority model. Every row in that table represents a runtime evidence
summary, and every AUTHORITATIVE_RUNTIME row MUST carry a real OTel
trace_id pointer (otherwise the "evidence" is fabricated).

Invariants asserted:

  1. Every row has bucket='runtime' (table default; sanity check)
  2. Every row has authority_status in the closed runtime enum
     {AUTHORITATIVE_RUNTIME, PARTIAL, UNKNOWN_NOT_PROOF}
  3. Every AUTHORITATIVE_RUNTIME row has non-empty latest_trace_id
     (the OTel evidence pointer)
  4. Every AUTHORITATIVE_RUNTIME row has attesting_trace_count >= 1
     (consistency with the classifier law in
     ``edge_authority.runtime_authority_for``)
  5. Every row has src_name and dst_name non-empty
     (UNIQUE constraint guards uniqueness; this guards quality)

Failure modes detected:

  * A runtime evidence row marked AUTHORITATIVE_RUNTIME but with an empty
    trace_id — likely a builder bug or a regression in
    ``runtime_view_builder.py``
  * A row with an authority_status outside the closed runtime enum
  * Inconsistent rows (e.g. attesting_trace_count=0 but
    authority_status=AUTHORITATIVE_RUNTIME)

Tier: B (advisory until activation flag set).
Plan: ``.claude/plans/three-bucket-otel-view-5db409.md`` (W4.P4.1).

USAGE
=====

::

    python ops_scripts/ci/check_runtime_proof_view_well_formed.py
    python ops_scripts/ci/check_runtime_proof_view_well_formed.py --strict
    python ops_scripts/ci/check_runtime_proof_view_well_formed.py --snapshot path/to/adg_indexed_<ts>.sqlite

Bypass: ``RUNTIME_PROOF_VIEW_BYPASS=1`` — logs and skips.
Activation: ``RUNTIME_PROOF_VIEW_STRICT=1`` flips advisory -> strict.
"""

from __future__ import annotations

# Per W4 of plan adg-three-bucket-authority-model-7e2a91, every ADG consumer
# declares its mode. This gate reads v_runtime_proof rows for proof-grade
# assertions, so it is proof-mode.
__adg_consumer_mode__ = "proof"

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

ARTIFACT_DIR: Final[Path] = REPO_ROOT / "artifacts" / "adg"
REPORT_PATH: Final[Path] = (
    REPO_ROOT / "docs" / "reports" / "adg" / "runtime_proof_view_gate_report.json"
)

VALID_AUTHORITY_STATUSES: Final[frozenset[str]] = frozenset(
    {"AUTHORITATIVE_RUNTIME", "PARTIAL", "UNKNOWN_NOT_PROOF"}
)


def _latest_snapshot() -> Path | None:
    """Return the latest ADG SQLite snapshot via canonical resolver."""
    from tools.adg.shared_modules.path_resolver import latest_sqlite  # noqa: PLC0415

    return latest_sqlite()


def _check_view_exists(con: sqlite3.Connection) -> tuple[bool, str]:
    """Return (exists, message). The table SHOULD exist after W1.P1.2 ships."""
    cur = con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='v_runtime_proof'"
    )
    if cur.fetchone() is None:
        return False, "v_runtime_proof table missing — W1 schema not applied"
    return True, "ok"


def _check_rows(con: sqlite3.Connection) -> dict[str, object]:
    """Run the five invariants and return a structured violations report."""
    out: dict[str, object] = {
        "total_rows": 0,
        "by_authority_status": {},
        "violations": [],
    }
    violations: list[dict[str, object]] = []

    rows = con.execute(
        """
        SELECT id, src_name, dst_name, relation_type, bucket,
               attesting_trace_count, latest_trace_id, authority_status
          FROM v_runtime_proof
        """
    ).fetchall()
    out["total_rows"] = len(rows)

    hist: dict[str, int] = {}
    for row in rows:
        rid, src_name, dst_name, rel, bucket, n_traces, trace_id, auth = row
        hist[auth or "<NULL>"] = hist.get(auth or "<NULL>", 0) + 1

        # Invariant 1 — bucket must be 'runtime'
        if bucket != "runtime":
            violations.append(
                {
                    "id": rid,
                    "kind": "bucket_not_runtime",
                    "message": f"row {rid} bucket={bucket!r} expected 'runtime'",
                }
            )
        # Invariant 2 — authority_status in closed enum
        if auth not in VALID_AUTHORITY_STATUSES:
            violations.append(
                {
                    "id": rid,
                    "kind": "invalid_authority_status",
                    "message": (
                        f"row {rid} authority_status={auth!r} not in "
                        f"{sorted(VALID_AUTHORITY_STATUSES)}"
                    ),
                }
            )
        # Invariant 3 — AUTHORITATIVE_RUNTIME requires trace_id
        if auth == "AUTHORITATIVE_RUNTIME" and not trace_id:
            violations.append(
                {
                    "id": rid,
                    "kind": "missing_trace_id",
                    "message": (
                        f"row {rid} authority_status=AUTHORITATIVE_RUNTIME but "
                        f"latest_trace_id is empty — fabricated evidence"
                    ),
                }
            )
        # Invariant 4 — AUTHORITATIVE_RUNTIME requires attesting_trace_count >= 1
        if auth == "AUTHORITATIVE_RUNTIME" and (n_traces or 0) < 1:
            violations.append(
                {
                    "id": rid,
                    "kind": "zero_attesting_count",
                    "message": (
                        f"row {rid} AUTHORITATIVE_RUNTIME but "
                        f"attesting_trace_count={n_traces} (<1)"
                    ),
                }
            )
        # Invariant 5 — src_name and dst_name non-empty
        if not src_name or not dst_name:
            violations.append(
                {
                    "id": rid,
                    "kind": "empty_endpoint",
                    "message": f"row {rid} has empty src_name or dst_name",
                }
            )

    out["by_authority_status"] = hist
    out["violations"] = violations
    return out


def _emit_report(report: dict[str, object]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, default=str), encoding="utf-8"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--snapshot",
        type=Path,
        default=None,
        help="Path to adg_indexed_<ts>.sqlite (default: latest)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Force strict mode (override RUNTIME_PROOF_VIEW_STRICT env var)",
    )
    args = parser.parse_args(argv)

    if os.environ.get("RUNTIME_PROOF_VIEW_BYPASS") == "1":
        print("[runtime_proof_view] bypass active (RUNTIME_PROOF_VIEW_BYPASS=1)")
        return 0

    # W4 of plan three-bucket-gap-remediation-069806: strict mode is now the
    # default. Set RUNTIME_PROOF_VIEW_STRICT=0 to revert to advisory.
    _env = os.environ.get("RUNTIME_PROOF_VIEW_STRICT", "1")
    strict = args.strict or _env == "1"

    snapshot = args.snapshot or _latest_snapshot()
    report: dict[str, object] = {
        "gate": "G-RUNTIME-PROOF-VIEW-WELL-FORMED",
        "tier": "B",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "snapshot_used": str(snapshot) if snapshot else None,
        "strict_mode": strict,
    }

    if snapshot is None or not snapshot.exists():
        report["status"] = "skip"
        report["reason"] = (
            "no static ADG snapshot found in artifacts/adg/ — gate is no-op"
        )
        _emit_report(report)
        print(f"[runtime_proof_view] {report['reason']}")
        return 0

    db_uri = f"file:{snapshot.as_posix()}?mode=ro&immutable=1"
    con = sqlite3.connect(db_uri, uri=True, timeout=5)
    try:
        ok, msg = _check_view_exists(con)
        if not ok:
            report["status"] = "skip"
            report["reason"] = msg
            _emit_report(report)
            print(f"[runtime_proof_view] {msg}")
            # Pre-W1 snapshots don't have the table; not a hard failure.
            return 0
        details = _check_rows(con)
    finally:
        con.close()

    report.update(details)
    violations = details.get("violations") or []
    n_viol = len(violations) if isinstance(violations, list) else 0
    report["violation_count"] = n_viol
    report["status"] = "ok" if n_viol == 0 else "violations"

    _emit_report(report)

    print(
        f"[runtime_proof_view] snapshot={snapshot.name} "
        f"rows={details['total_rows']} violations={n_viol} "
        f"strict={strict}"
    )
    if n_viol > 0:
        print(f"[runtime_proof_view] details written to {REPORT_PATH}")
        # Print up to 10 representative violations.
        sample = violations[:10] if isinstance(violations, list) else []
        for v in sample:
            if isinstance(v, dict):
                print(f"  - {v.get('kind')}: {v.get('message')}")

    if n_viol == 0:
        return 0
    return 1 if strict else 0


if __name__ == "__main__":
    sys.exit(main())
