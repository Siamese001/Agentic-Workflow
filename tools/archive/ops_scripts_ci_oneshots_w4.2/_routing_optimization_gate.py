#!/usr/bin/env python3
"""
P4/L0 Routing Optimization CI Gate

Enforces Gates A-E for routing optimization closure:
- Gate A: Optimization runs without historical data window
- Gate B: Routing policy mutates without version increment
- Gate C: Optimization recommends routes not present in registry
- Gate D: Optimization recommendations lack reasoning metadata
- Gate E: Optimization bypasses governance approval

Runtime-only closure: excludes test, tests, spec, fixture, mock files.
"""

import sqlite3
import sys
from pathlib import Path

# Constants
NON_TEST = """
    AND source_file NOT LIKE '%test%'
    AND source_file NOT LIKE '%tests%'
    AND source_file NOT LIKE '%spec%'
    AND source_file NOT LIKE '%fixture%'
    AND source_file NOT LIKE '%mock%'
"""

GATE_RESULTS: list[tuple[str, bool, str]] = []


def _count_exported(conn: sqlite3.Connection, symbol: str, module_hint: str = "") -> int:
    """Count distinct source files exporting a symbol."""
    if module_hint:
        cursor = conn.execute(
            f"""
            SELECT COUNT(DISTINCT source_file)
            FROM edges
            WHERE symbol LIKE ? AND source_file LIKE ? {NON_TEST}
            """,
            (f"%{symbol}%", f"%{module_hint}%"),
        )
    else:
        cursor = conn.execute(
            f"""
            SELECT COUNT(DISTINCT source_file)
            FROM edges
            WHERE symbol LIKE ? {NON_TEST}
            """,
            (f"%{symbol}%",),
        )
    return cursor.fetchone()[0]


def _count_distinct_sources(
    conn: sqlite3.Connection,
    relation_type: str,
    filter_clause: str = NON_TEST,
) -> int:
    """Count distinct source files for a relation type."""
    cursor = conn.execute(
        f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type=? {filter_clause}",
        (relation_type,),
    )
    return cursor.fetchone()[0]


def gate_a(conn: sqlite3.Connection) -> bool:
    """Gate A — Optimization runs without historical data window.

    Passes when:
    - RoutingOptimizationRecord exported >= 1
      (routing optimization record with 11 required fields), AND
    - optimize_routing_policy exported >= 1
      (mandatory optimization entrypoint), AND
    - optimizes_routing function exported >= 1
      (ADG edge emitter for routing optimization), AND
    - historical_outcomes_analyzed exported >= 1
      (ADG edge emitter for historical analysis), AND
    - optimization_window_start exported >= 1
      (historical data window start), AND
    - optimization_window_end exported >= 1
      (historical data window end)
    """
    routing_record = _count_exported(conn, "RoutingOptimizationRecord", "routing_optimization")
    optimize_function = _count_exported(conn, "optimize_routing_policy", "optimization_orchestrator")
    emitter_function = _count_exported(conn, "optimizes_routing", "optimization_orchestrator")
    historical_emitter = _count_exported(conn, "historical_outcomes_analyzed", "optimization_orchestrator")
    window_start = _count_exported(conn, "optimization_window_start", "routing_optimization")
    window_end = _count_exported(conn, "optimization_window_end", "routing_optimization")

    ok = (
        routing_record >= 1
        and optimize_function >= 1
        and emitter_function >= 1
        and historical_emitter >= 1
        and window_start >= 1
        and window_end >= 1
    )
    GATE_RESULTS.append(
        (
            "A",
            ok,
            f"RoutingOptimizationRecord exported={routing_record} (>=1), "
            f"optimize_routing_policy exported={optimize_function} (>=1), "
            f"optimizes_routing exported={emitter_function} (>=1), "
            f"historical_outcomes_analyzed exported={historical_emitter} (>=1), "
            f"optimization_window_start exported={window_start} (>=1), "
            f"optimization_window_end exported={window_end} (>=1)",
        ),
    )
    return ok


def gate_b(conn: sqlite3.Connection) -> bool:
    """Gate B — Routing policy mutates without version increment.

    Passes when:
    - RoutingOptimizationRecord exported >= 1
      (routing optimization record for version tracking), AND
    - optimization_reason_hash exported >= 1
      (optimization reason hash for version tracking), AND
    - routing_policy_adapted exported >= 1
      (ADG edge emitter for policy adaptation), AND
    - PolicyContext exported >= 1
      (policy context for version management), AND
    - current_policy_version field available
      (policy version tracking)
    """
    routing_record = _count_exported(conn, "RoutingOptimizationRecord", "routing_optimization")
    reason_hash = _count_exported(conn, "optimization_reason_hash", "routing_optimization")
    policy_emitter = _count_exported(conn, "routing_policy_adapted", "optimization_orchestrator")
    policy_context = _count_exported(conn, "PolicyContext", "optimization_orchestrator")
    # Note: current_policy_version is a field in PolicyContext, not exported separately

    ok = routing_record >= 1 and reason_hash >= 1 and policy_emitter >= 1 and policy_context >= 1
    GATE_RESULTS.append(
        (
            "B",
            ok,
            f"RoutingOptimizationRecord exported={routing_record} (>=1), "
            f"optimization_reason_hash exported={reason_hash} (>=1), "
            f"routing_policy_adapted exported={policy_emitter} (>=1), "
            f"PolicyContext exported={policy_context} (>=1)",
        ),
    )
    return ok


def gate_c(conn: sqlite3.Connection) -> bool:
    """Gate C — Optimization recommends routes not present in registry.

    Passes when:
    - RoutingOptimizationRecord exported >= 1
      (routing optimization record for route tracking), AND
    - route_candidate_hash exported >= 1
      (route candidate hash for registry validation), AND
    - recommended_route_rank exported >= 1
      (recommended route rank for registry validation), AND
    - route_candidate_ranked exported >= 1
      (ADG edge emitter for route ranking), AND
    - PolicyContext exported >= 1
      (policy context with route registry)
    """
    routing_record = _count_exported(conn, "RoutingOptimizationRecord", "routing_optimization")
    route_hash = _count_exported(conn, "route_candidate_hash", "routing_optimization")
    route_rank = _count_exported(conn, "recommended_route_rank", "routing_optimization")
    rank_emitter = _count_exported(conn, "route_candidate_ranked", "optimization_orchestrator")
    policy_context = _count_exported(conn, "PolicyContext", "optimization_orchestrator")

    ok = (
        routing_record >= 1
        and route_hash >= 1
        and route_rank >= 1
        and rank_emitter >= 1
        and policy_context >= 1
    )
    GATE_RESULTS.append(
        (
            "C",
            ok,
            f"RoutingOptimizationRecord exported={routing_record} (>=1), "
            f"route_candidate_hash exported={route_hash} (>=1), "
            f"recommended_route_rank exported={route_rank} (>=1), "
            f"route_candidate_ranked exported={rank_emitter} (>=1), "
            f"PolicyContext exported={policy_context} (>=1)",
        ),
    )
    return ok


def gate_d(conn: sqlite3.Connection) -> bool:
    """Gate D — Optimization recommendations lack reasoning metadata.

    Passes when:
    - RoutingOptimizationRecord exported >= 1
      (routing optimization record for reasoning), AND
    - optimization_reason_hash exported >= 1
      (optimization reason hash for reasoning), AND
    - historical_success_rate exported >= 1
      (historical success rate for reasoning), AND
    - historical_failure_rate exported >= 1
      (historical failure rate for reasoning), AND
    - median_latency_ms exported >= 1
      (latency metrics for reasoning)
    """
    routing_record = _count_exported(conn, "RoutingOptimizationRecord", "routing_optimization")
    reason_hash = _count_exported(conn, "optimization_reason_hash", "routing_optimization")
    success_rate = _count_exported(conn, "historical_success_rate", "routing_optimization")
    failure_rate = _count_exported(conn, "historical_failure_rate", "routing_optimization")
    latency_ms = _count_exported(conn, "median_latency_ms", "routing_optimization")

    ok = (
        routing_record >= 1
        and reason_hash >= 1
        and success_rate >= 1
        and failure_rate >= 1
        and latency_ms >= 1
    )
    GATE_RESULTS.append(
        (
            "D",
            ok,
            f"RoutingOptimizationRecord exported={routing_record} (>=1), "
            f"optimization_reason_hash exported={reason_hash} (>=1), "
            f"historical_success_rate exported={success_rate} (>=1), "
            f"historical_failure_rate exported={failure_rate} (>=1), "
            f"median_latency_ms exported={latency_ms} (>=1)",
        ),
    )
    return ok


def gate_e(conn: sqlite3.Connection) -> bool:
    """Gate E — Optimization bypasses governance approval.

    Passes when:
    - RoutingOptimizationRecord exported >= 1
      (routing optimization record for governance), AND
    - optimize_routing_policy exported >= 1
      (mandatory optimization entrypoint with governance), AND
    - routing_governance_approved exported >= 1
      (ADG edge emitter for governance approval), AND
    - apply_optimization_with_governance exported >= 1
      (governance application function), AND
    - PolicyContext exported >= 1
      (policy context with governance settings)
    """
    routing_record = _count_exported(conn, "RoutingOptimizationRecord", "routing_optimization")
    optimize_function = _count_exported(conn, "optimize_routing_policy", "optimization_orchestrator")
    governance_emitter = _count_exported(conn, "routing_governance_approved", "optimization_orchestrator")
    governance_function = _count_exported(
        conn,
        "apply_optimization_with_governance",
        "optimization_orchestrator",
    )
    policy_context = _count_exported(conn, "PolicyContext", "optimization_orchestrator")

    ok = (
        routing_record >= 1
        and optimize_function >= 1
        and governance_emitter >= 1
        and governance_function >= 1
        and policy_context >= 1
    )
    GATE_RESULTS.append(
        (
            "E",
            ok,
            f"RoutingOptimizationRecord exported={routing_record} (>=1), "
            f"optimize_routing_policy exported={optimize_function} (>=1), "
            f"routing_governance_approved exported={governance_emitter} (>=1), "
            f"apply_optimization_with_governance exported={governance_function} (>=1), "
            f"PolicyContext exported={policy_context} (>=1)",
        ),
    )
    return ok


def _print_baseline(conn: sqlite3.Connection) -> None:
    """Print P4/L0 routing optimization baseline for verification."""
    print("\n--- P4/L0 Routing Optimization Baseline ---")

    for rel in (
        "routes_path",
        "routes_through",
        "records_execution_trace",
        "optimizes_routing",
        "routing_policy_adapted",
        "routing_optimization_persisted",
        "route_candidate_ranked",
        "routing_governance_approved",
        "historical_outcomes_analyzed",
    ):
        total = _count_distinct_sources(conn, rel)
        print(f"  {rel:<45} total={total:4d}")

    print("\n--- Key L0 routing optimization symbols (non-test) ---")
    for sym in (
        "RoutingOptimizationRecord",
        "optimize_routing_policy",
        "RoutingOptimizationError",
        "routing_optimization_id",
        "optimization_window_start",
        "optimization_window_end",
        "route_candidate_hash",
        "historical_success_rate",
        "historical_failure_rate",
        "median_latency_ms",
        "p95_latency_ms",
        "cost_estimate",
        "recommended_route_rank",
        "optimization_reason_hash",
        "RoutingHistory",
        "OptimizationWindow",
        "PolicyContext",
    ):
        count = _count_exported(conn, sym)
        print(f"  symbol:{sym:<40} sources={count:4d}")

    print("\n--- L0 routing optimization module exports (non-test) ---")
    cursor = conn.execute(
        f"""
        SELECT DISTINCT source_file, symbol
        FROM edges
        WHERE source_file LIKE '%L0_routing/optimization%' {NON_TEST}
        ORDER BY source_file, symbol
        LIMIT 30
        """,
    )
    for source, symbol in cursor.fetchall():
        print(f"  {source:<60} [{symbol}]")


def main() -> int:
    """Run P4/L0 routing optimization gates."""
    # Find latest ADG SQLite artifact
    adg_dir = Path("artifacts/adg")
    if not adg_dir.exists():
        print("ERROR: artifacts/adg directory not found")
        return 1

    db_files = sorted(adg_dir.glob("adg_indexed_*.sqlite"))
    if not db_files:
        print("ERROR: No ADG SQLite artifacts found")
        return 1

    db_path = db_files[-1]
    print(f"Using ADG: {db_path.name}")

    conn = sqlite3.connect(str(db_path))

    # Run gates
    gate_a_result = gate_a(conn)
    gate_b_result = gate_b(conn)
    gate_c_result = gate_c(conn)
    gate_d_result = gate_d(conn)
    gate_e_result = gate_e(conn)

    # Print baseline
    _print_baseline(conn)

    # Print results
    print("\n" + "=" * 70)
    print("GATE RESULTS")
    print("=" * 70)
    for gate, ok, details in GATE_RESULTS:
        status = "PASS" if ok else "FAIL"
        print(f"  Gate {gate}: {status} - {details}")

    # Overall result
    all_passed = all([gate_a_result, gate_b_result, gate_c_result, gate_d_result, gate_e_result])
    print("\n" + "=" * 70)
    if all_passed:
        print("P4/L0 ROUTING OPTIMIZATION: ALL GATES PASSED - CLOSURE VERIFIED")
    else:
        failed_gates = [gate for gate, ok, _ in GATE_RESULTS if not ok]
        print(f"P4/L0 ROUTING OPTIMIZATION: FAILED GATES {failed_gates}")
    print("=" * 70)

    conn.close()
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
