"""
ops_scripts/ci/_routing_determinism_gate.py

CI gate: Enforce routing determinism replay coverage >= 95%.

Fails the build if:
  - emits_replay_key coverage < 95% of routing decisions
  - emits_determinism_digest coverage < 95% of routing decisions
  - uses_wall_clock in L0 routing > 0
  - invokes_getattr_dynamic in L0 routing logic > 0 (enforcement files excluded)
  - records_execution_trace in L0 == 0

Usage:
    python ops_scripts/ci/_routing_determinism_gate.py [--db PATH]
    python ops_scripts/ci/_routing_determinism_gate.py  # uses latest sqlite

Exit code 0 = all gates pass. Non-zero = gate failure.
"""

from __future__ import annotations

import argparse
import glob
import sqlite3
import sys

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)

emit_determinism_digest("_routing_determinism_gate", "_routing_determinism_gate_digest")
record_execution_trace("_routing_determinism_gate", "_routing_determinism_gate_trace")



def _latest_db() -> str:
    files = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))
    if not files:
        print("ERROR: No ADG sqlite found in artifacts/adg/", file=sys.stderr)
        sys.exit(2)
    return files[-1]


def _query(cur: sqlite3.Cursor, sql: str, params: tuple = ()) -> int:
    cur.execute(sql, params)
    return cur.fetchone()[0]


def run_gate(db_path: str) -> int:
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # Count distinct source modules (not raw edges) to avoid double-counting
    # delegation call sites like self.path_router.select_path
    routing_decisions = _query(
        cur,
        """
        SELECT COUNT(DISTINCT e.src_id) FROM edges e JOIN nodes n ON e.src_id=n.id
        WHERE e.relation_type IN ('routes_path','routes_through')
        AND n.layer='L0'
        """,
    )
    replay_keys = _query(
        cur,
        """
        SELECT COUNT(DISTINCT e.src_id) FROM edges e JOIN nodes n ON e.src_id=n.id
        WHERE e.relation_type='emits_replay_key'
        AND n.layer='L0'
        """,
    )
    determinism_digests = _query(
        cur,
        """
        SELECT COUNT(DISTINCT e.src_id) FROM edges e JOIN nodes n ON e.src_id=n.id
        WHERE e.relation_type='emits_determinism_digest'
        AND n.layer='L0'
        """,
    )
    wall_clock_l0 = _query(
        cur,
        """
        SELECT COUNT(*) FROM edges e JOIN nodes n ON e.src_id=n.id
        WHERE e.relation_type='uses_wall_clock'
        AND n.layer='L0'
        AND e.source_file NOT LIKE '%test%'
        """,
    )
    getattr_dynamic_l0_routing = _query(
        cur,
        """
        SELECT COUNT(*) FROM edges e JOIN nodes n ON e.src_id=n.id
        WHERE e.relation_type='invokes_getattr_dynamic'
        AND n.layer='L0'
        AND e.source_file LIKE '%L0_routing/engines/%'
        """,
    )
    records_trace_l0 = _query(
        cur,
        """
        SELECT COUNT(*) FROM edges e JOIN nodes n ON e.src_id=n.id
        WHERE e.relation_type='records_execution_trace'
        AND n.layer='L0'
        """,
    )
    signs_trace_l0 = _query(
        cur,
        """
        SELECT COUNT(*) FROM edges e JOIN nodes n ON e.src_id=n.id
        WHERE e.relation_type='signs_execution_trace'
        AND n.layer='L0'
        """,
    )

    con.close()

    print(f"[GATE] DB: {db_path}")
    print(f"[GATE] routing_decisions         = {routing_decisions}")
    print(f"[GATE] emits_replay_key          = {replay_keys}")
    print(f"[GATE] emits_determinism_digest  = {determinism_digests}")
    print(f"[GATE] uses_wall_clock (L0 prod) = {wall_clock_l0}")
    print(f"[GATE] getattr_dynamic (L0 eng)  = {getattr_dynamic_l0_routing}")
    print(f"[GATE] records_execution_trace L0= {records_trace_l0}")
    print(f"[GATE] signs_execution_trace L0  = {signs_trace_l0}")

    failures: list[str] = []
    THRESHOLD = 0.95

    if routing_decisions > 0:
        replay_coverage = replay_keys / routing_decisions
        digest_coverage = determinism_digests / routing_decisions
        print(f"[GATE] replay_coverage           = {replay_coverage:.2%}")
        print(f"[GATE] digest_coverage           = {digest_coverage:.2%}")
        if replay_coverage < THRESHOLD:
            failures.append(
                f"replay_key coverage {replay_coverage:.2%} < {THRESHOLD:.0%} "
                f"({replay_keys}/{routing_decisions})",
            )
        if digest_coverage < THRESHOLD:
            failures.append(
                f"determinism_digest coverage {digest_coverage:.2%} < {THRESHOLD:.0%} "
                f"({determinism_digests}/{routing_decisions})",
            )
    else:
        print("[GATE] WARN: No routing_decisions found — coverage gates skipped")

    if wall_clock_l0 > 0:
        failures.append(f"uses_wall_clock in L0 routing = {wall_clock_l0} (must be 0)")

    if getattr_dynamic_l0_routing > 0:
        failures.append(
            f"invokes_getattr_dynamic in L0 routing engines = {getattr_dynamic_l0_routing} (must be 0)",
        )

    if records_trace_l0 == 0:
        failures.append("records_execution_trace in L0 == 0 (must be > 0)")

    if failures:
        print("\n[GATE] FAILED — routing determinism gate violations:")
        for f in failures:
            print(f"  ✗ {f}")
        return 1

    print("\n[GATE] PASSED — all routing determinism gates satisfied")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Routing determinism CI gate")
    parser.add_argument("--db", default=None, help="Path to ADG sqlite (default: latest)")
    args = parser.parse_args()
    db_path = args.db or _latest_db()
    sys.exit(run_gate(db_path))


if __name__ == "__main__":
    main()
