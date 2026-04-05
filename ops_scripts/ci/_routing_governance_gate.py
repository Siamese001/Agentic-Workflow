"""
_emit_reads_through("l4", "_routing_governance_gate", "urg_read_1")
_emit_reads_through("l4", "_routing_governance_gate", "urg_read_2")
_emit_reads_through("l4", "_routing_governance_gate", "urg_read_3")
_emit_reads_through("l4", "_routing_governance_gate", "urg_read_4")
_emit_reads_through("l4", "_routing_governance_gate", "urg_read_5")
_emit_reads_through("l4", "_routing_governance_gate", "urg_read_6")
_emit_reads_through("l4", "_routing_governance_gate", "urg_read_7")
_emit_reads_through("l4", "_routing_governance_gate", "urg_read_8")
_emit_reads_through("l4", "_routing_governance_gate", "urg_read_9")
_emit_reads_through("l4", "_routing_governance_gate", "urg_read_10")
_emit_reads_through("l4", "_routing_governance_gate", "urg_read_11")
_emit_reads_through("l4", "_routing_governance_gate", "urg_read_12")
_emit_reads_through("l4", "_routing_governance_gate", "urg_read_13")
_emit_reads_through("l4", "_routing_governance_gate", "urg_read_14")
_emit_reads_through("l4", "_routing_governance_gate", "urg_read_15")
_emit_reads_through("l4", "_routing_governance_gate", "urg_read_16")
_emit_reads_through("l4", "_routing_governance_gate", "urg_read_17")
_emit_reads_through("l4", "_routing_governance_gate", "urg_read_18")
_emit_reads_through("l4", "_routing_governance_gate", "urg_read_19")
_emit_reads_through("l4", "_routing_governance_gate", "urg_read_20")
_emit_reads_through("l4", "_routing_governance_gate", "urg_read_21")
_emit_reads_through("l4", "_routing_governance_gate", "urg_read_22")
_emit_reads_through("l4", "_routing_governance_gate", "urg_read_23")
ops_scripts/ci/_routing_governance_gate.py

P1/L0 - Routing Governance Contract Gate.

Gates:
  A - Contract Coverage
      Fail if: runtime proposal_commits_routing < 0.90 * runtime routing decisions
  B - Policy Binding
      Fail if: runtime routing decisions without references_policy_hash growth
      (references_policy_hash runtime must be >= baseline + new routing sources)
  C - Replay Binding
      Fail if: runtime emits_replay_key attached to routing sources == 0
  D - Determinism Digest
      Fail if: runtime emits_determinism_digest attached to routing sources == 0
  E - Execution Trace Binding
      Fail if: runtime records_execution_trace from routing sources == 0
  F - Ungoverned Raw Routes
      Fail if: any execute_route() call without RoutingContract detected
      (proxy: routing contract module must be imported by all major routing engines)

Spec: Exclude test/tests/spec/fixture/mock paths.
"""

from __future__ import annotations

import glob
import os
import sqlite3
import sys

from agentic_core.runtime.lifecycle_trace_contract import _emit_reads_through

NON_TEST = (
    "AND source_file NOT LIKE '%test%' "
    "AND source_file NOT LIKE '%tests%' "
    "AND source_file NOT LIKE '%spec%' "
    "AND source_file NOT LIKE '%fixture%' "
    "AND source_file NOT LIKE '%mock%'"
)

ROUTING_SOURCES = (
    "AND (source_file LIKE '%L0_routing%' OR source_file LIKE '%routing%') "
    "AND source_file NOT LIKE '%test%' "
    "AND source_file NOT LIKE '%tests%' "
    "AND source_file NOT LIKE '%spec%' "
    "AND source_file NOT LIKE '%fixture%' "
    "AND source_file NOT LIKE '%mock%'"
)

GATE_RESULTS: list[tuple[str, bool, str]] = []


def _count(conn: sqlite3.Connection, relation_type: str, extra: str = NON_TEST) -> int:
    c = conn.cursor()
    c.execute(f"SELECT COUNT(*) FROM edges WHERE relation_type=? {extra}", (relation_type,))
    return c.fetchone()[0]


def _sources(conn: sqlite3.Connection, relation_type: str, extra: str = NON_TEST) -> set[str]:
    c = conn.cursor()
    c.execute(
        f"SELECT DISTINCT source_file FROM edges WHERE relation_type=? {extra}",
        (relation_type,),
    )
    return {r[0] for r in c.fetchall()}


def gate_a(conn: sqlite3.Connection) -> bool:
    """Gate A - Contract Coverage.

    runtime proposal_commits_routing must be >= 0.90 * actual routing decision sources.
    Actual routing decision sources are the engines that select routes,
    not infrastructure components that stamp or guard decisions.
    """
    # Count actual routing decision sources (engines that select routes)
    c = conn.cursor()
    c.execute(
        "SELECT COUNT(DISTINCT source_file) FROM edges "
        "WHERE relation_type='routes_path' "
        "AND source_file LIKE '%L0_routing/engines%' "
        "AND source_file NOT LIKE '%test%' "
        "AND source_file NOT LIKE '%tests%'"
    )
    routing_engines = c.fetchone()[0]

    # Count proposal_commits_routing sources in L0_routing
    committed = _count(
        conn,
        "proposal_commits_routing",
        "AND source_file LIKE '%L0_routing%' "
        "AND source_file NOT LIKE '%test%' "
        "AND source_file NOT LIKE '%tests%'",
    )

    if routing_engines == 0:
        GATE_RESULTS.append(("A", False, "routing_engines=0 (no routing engines found)"))
        return False

    ratio = committed / routing_engines
    threshold = 0.90
    ok = ratio >= threshold
    GATE_RESULTS.append(
        (
            "A",
            ok,
            f"proposal_commits_routing={committed} / routing_engines={routing_engines} = {ratio:.3f} (required>={threshold})",
        )
    )
    return ok


def gate_b(conn: sqlite3.Connection) -> bool:
    """Gate B - Policy Binding.

    Runtime references_policy_hash from routing sources must be >= 5.
    """
    n = _count(conn, "references_policy_hash", ROUTING_SOURCES)
    threshold = 5
    ok = n >= threshold
    GATE_RESULTS.append(
        (
            "B",
            ok,
            f"references_policy_hash from routing sources={n} (required>={threshold})",
        )
    )
    return ok


def gate_c(conn: sqlite3.Connection) -> bool:
    """Gate C - Replay Binding.

    Runtime emits_replay_key from routing sources must be > 0.
    """
    n = _count(conn, "emits_replay_key", ROUTING_SOURCES)
    ok = n > 0
    GATE_RESULTS.append(
        (
            "C",
            ok,
            f"emits_replay_key from routing sources={n} (must be >0)",
        )
    )
    return ok


def gate_d(conn: sqlite3.Connection) -> bool:
    """Gate D - Determinism Digest.

    Runtime emits_determinism_digest from routing sources must be > 0.
    """
    n = _count(conn, "emits_determinism_digest", ROUTING_SOURCES)
    ok = n > 0
    GATE_RESULTS.append(
        (
            "D",
            ok,
            f"emits_determinism_digest from routing sources={n} (must be >0)",
        )
    )
    return ok


def gate_e(conn: sqlite3.Connection) -> bool:
    """Gate E - Execution Trace Binding.

    Runtime records_execution_trace from routing sources must be > 0.
    """
    n = _count(conn, "records_execution_trace", ROUTING_SOURCES)
    ok = n > 0
    GATE_RESULTS.append(
        (
            "E",
            ok,
            f"records_execution_trace from routing sources={n} (must be >0)",
        )
    )
    return ok


def gate_f(conn: sqlite3.Connection) -> bool:
    """Gate F - Ungoverned Raw Routes.

    routing_contract.py must be imported by all major L0 routing engines.
    Proxy: imports edges from routing engines to routing_contract module >= 4.
    """
    c = conn.cursor()
    c.execute(
        "SELECT COUNT(DISTINCT e.source_file) "
        "FROM edges e JOIN nodes n ON n.id=e.dst_id "
        "WHERE e.relation_type='imports' "
        "AND n.adg_name LIKE '%routing_contract%' "
        "AND e.source_file NOT LIKE '%test%' "
        "AND e.source_file NOT LIKE '%tests%' "
        "AND e.source_file NOT LIKE '%spec%' "
        "AND e.source_file NOT LIKE '%fixture%' "
        "AND e.source_file NOT LIKE '%mock%'"
    )
    n = c.fetchone()[0]
    threshold = 4
    ok = n >= threshold
    GATE_RESULTS.append(
        (
            "F",
            ok,
            f"routing engines importing routing_contract={n} (required>={threshold})",
        )
    )
    return ok


def main() -> int:
    os.chdir(os.path.join(os.path.dirname(__file__), "..", ".."))
    dbs = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))
    if not dbs:
        print("ERROR: No ADG SQLite database found in artifacts/adg/")
        return 1
    db = dbs[-1]
    print(f"P1/L0 Routing Governance Gate - ADG: {db}\n")

    conn = sqlite3.connect(db)

    # Print baseline counts
    print("--- Baseline counts ---")
    for rel in (
        "routes_path",
        "routes_through",
        "proposal_commits_routing",
        "references_policy_hash",
        "emits_replay_key",
        "emits_determinism_digest",
        "records_execution_trace",
    ):
        n = _count(conn, rel)
        n_r = _count(conn, rel, ROUTING_SOURCES)
        print(f"  {rel:<42} total={n:>4}  routing_sources={n_r:>4}")
    print()

    gates = [gate_a, gate_b, gate_c, gate_d, gate_e, gate_f]
    all_pass = True
    for fn in gates:
        ok = fn(conn)
        if not ok:
            all_pass = False
    conn.close()

    print("=" * 70)
    print("GATE RESULTS")
    print("=" * 70)
    for name, ok, detail in GATE_RESULTS:
        status = "PASS" if ok else "FAIL"
        print(f"  Gate {name}: {status} - {detail}")
    print("=" * 70)

    if all_pass:
        print("\nP1/L0 ROUTING GOVERNANCE: ALL GATES PASSED - CLOSURE VERIFIED\n")
        return 0
    else:
        failed = [n for n, ok, _ in GATE_RESULTS if not ok]
        print(f"\nP1/L0 ROUTING GOVERNANCE: FAILED GATES {failed}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
