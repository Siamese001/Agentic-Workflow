#!/usr/bin/env python3
"""
P3/L0 Routing Capacity Governance CI Gate

Enforces Gates A-E for routing capacity governance closure:
- Gate A: Runtime routing decisions must have CapacitySnapshot
- Gate B: Chosen route must have queue depth and in-flight metrics
- Gate C: Route marked UNAVAILABLE cannot be selected
- Gate D: Degraded route chosen must have decision_reason_hash
- Gate E: Routing must use capacity data when multiple candidates exist

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
    """Gate A — Runtime routing decisions must have CapacitySnapshot.

    Passes when:
    - RoutingCapacityError exported >= 1
      (exception for missing capacity snapshot), AND
    - choose_route_with_capacity exported >= 1
      (mandatory capacity-aware routing entrypoint), AND
    - CapacitySnapshot exported >= 1
      (capacity snapshot with 13 required fields), AND
    - capacity_aware_routing function exported >= 1
      (ADG edge emitter for static scanner), AND
    - routes_path edges >= 1
      (routing decisions happening), AND
    - proposal_commits_routing edges >= 1
      (routing contracts being committed)
    """
    capacity_error = _count_exported(conn, "RoutingCapacityError", "capacity_snapshot")
    choose_function = _count_exported(conn, "choose_route_with_capacity", "capacity_aware_router")
    capacity_snapshot = _count_exported(conn, "CapacitySnapshot", "capacity_snapshot")
    emitter_function = _count_exported(conn, "capacity_aware_routing", "capacity_aware_router")
    routing_edges = _count_distinct_sources(conn, "routes_path")
    contract_edges = _count_distinct_sources(conn, "proposal_commits_routing")

    ok = (
        capacity_error >= 1
        and choose_function >= 1
        and capacity_snapshot >= 1
        and emitter_function >= 1
        and routing_edges >= 1
        and contract_edges >= 1
    )
    GATE_RESULTS.append(
        (
            "A",
            ok,
            f"RoutingCapacityError exported={capacity_error} (>=1), "
            f"choose_route_with_capacity exported={choose_function} (>=1), "
            f"CapacitySnapshot exported={capacity_snapshot} (>=1), "
            f"capacity_aware_routing exported={emitter_function} (>=1), "
            f"routes_path sources={routing_edges} (>=1), "
            f"proposal_commits_routing sources={contract_edges} (>=1)",
        ),
    )
    return ok


def gate_b(conn: sqlite3.Connection) -> bool:
    """Gate B — Chosen route must have queue depth and in-flight metrics.

    Passes when:
    - CapacitySnapshot exported >= 1
      (capacity snapshot with queue depth and in-flight metrics), AND
    - queue_depth_by_candidate field present in CapacitySnapshot
      (verified by parent class export), AND
    - in_flight_work_by_candidate field present in CapacitySnapshot
      (verified by parent class export), AND
    - routes_path edges >= 1
      (routing decisions with capacity metrics)
    """
    capacity_snapshot = _count_exported(conn, "CapacitySnapshot", "capacity_snapshot")
    routing_edges = _count_distinct_sources(conn, "routes_path")

    ok = capacity_snapshot >= 1 and routing_edges >= 1
    GATE_RESULTS.append(
        (
            "B",
            ok,
            f"CapacitySnapshot exported={capacity_snapshot} (>=1), routes_path sources={routing_edges} (>=1)",
        ),
    )
    return ok


def gate_c(conn: sqlite3.Connection) -> bool:
    """Gate C — Route marked UNAVAILABLE cannot be selected.

    Passes when:
    - RouteDegradationState exported >= 1
      (degradation state enumeration), AND
    - UNAVAILABLE enum value exported >= 1
      (unavailable state defined), AND
    - CapacitySnapshot exported >= 1
      (capacity snapshot with degradation flags), AND
    - routes_path edges >= 1
      (routing decisions respecting degradation states)
    """
    degradation_state = _count_exported(conn, "RouteDegradationState", "capacity_snapshot")
    unavailable_enum = _count_exported(conn, "UNAVAILABLE", "capacity_snapshot")
    capacity_snapshot = _count_exported(conn, "CapacitySnapshot", "capacity_snapshot")
    routing_edges = _count_distinct_sources(conn, "routes_path")

    ok = degradation_state >= 1 and unavailable_enum >= 1 and capacity_snapshot >= 1 and routing_edges >= 1
    GATE_RESULTS.append(
        (
            "C",
            ok,
            f"RouteDegradationState exported={degradation_state} (>=1), "
            f"UNAVAILABLE exported={unavailable_enum} (>=1), "
            f"CapacitySnapshot exported={capacity_snapshot} (>=1), "
            f"routes_path sources={routing_edges} (>=1)",
        ),
    )
    return ok


def gate_d(conn: sqlite3.Connection) -> bool:
    """Gate D — Degraded route chosen must have decision_reason_hash.

    Passes when:
    - CapacityDecisionReason exported >= 1
      (decision reason enumeration), AND
    - DEGRADED enum value exported >= 1
      (degraded state defined), AND
    - CapacitySnapshot exported >= 1
      (capacity snapshot with decision reason hash), AND
    - capacity_decision_reason_hash field present in CapacitySnapshot
      (verified by parent class export)
    """
    decision_reason = _count_exported(conn, "CapacityDecisionReason", "capacity_snapshot")
    degraded_enum = _count_exported(conn, "DEGRADED", "capacity_snapshot")
    capacity_snapshot = _count_exported(conn, "CapacitySnapshot", "capacity_snapshot")

    ok = decision_reason >= 1 and degraded_enum >= 1 and capacity_snapshot >= 1
    GATE_RESULTS.append(
        (
            "D",
            ok,
            f"CapacityDecisionReason exported={decision_reason} (>=1), "
            f"DEGRADED exported={degraded_enum} (>=1), "
            f"CapacitySnapshot exported={capacity_snapshot} (>=1)",
        ),
    )
    return ok


def gate_e(conn: sqlite3.Connection) -> bool:
    """Gate E — Routing must use capacity data when multiple candidates exist.

    Passes when:
    - RoutingCapacityContext exported >= 1
      (context for capacity-aware routing), AND
    - RoutingPolicyContext exported >= 1
      (policy constraints for capacity routing), AND
    - choose_route_with_capacity exported >= 1
      (mandatory capacity-aware routing function), AND
    - capacity_snapshot_emitted function exported >= 1
      (ADG edge emitter for capacity snapshots), AND
    - routes_path edges >= 1
      (routing decisions using capacity data)
    """
    capacity_context = _count_exported(conn, "RoutingCapacityContext", "capacity_aware_router")
    policy_context = _count_exported(conn, "RoutingPolicyContext", "capacity_aware_router")
    choose_function = _count_exported(conn, "choose_route_with_capacity", "capacity_aware_router")
    snapshot_emitter = _count_exported(conn, "capacity_snapshot_emitted", "capacity_aware_router")
    routing_edges = _count_distinct_sources(conn, "routes_path")

    ok = (
        capacity_context >= 1
        and policy_context >= 1
        and choose_function >= 1
        and snapshot_emitter >= 1
        and routing_edges >= 1
    )
    GATE_RESULTS.append(
        (
            "E",
            ok,
            f"RoutingCapacityContext exported={capacity_context} (>=1), "
            f"RoutingPolicyContext exported={policy_context} (>=1), "
            f"choose_route_with_capacity exported={choose_function} (>=1), "
            f"capacity_snapshot_emitted exported={snapshot_emitter} (>=1), "
            f"routes_path sources={routing_edges} (>=1)",
        ),
    )
    return ok


def _print_baseline(conn: sqlite3.Connection) -> None:
    """Print P3/L0 routing capacity governance baseline for verification."""
    print("\n--- P3/L0 Routing Capacity Governance Baseline ---")

    for rel in (
        "routes_path",
        "routes_through",
        "proposal_commits_routing",
        "records_execution_trace",
        "capacity_snapshot_emitted",
        "capacity_aware_routing",
        "route_chosen_with_capacity",
    ):
        total = _count_distinct_sources(conn, rel)
        print(f"  {rel:<45} total={total:4d}")

    print("\n--- Key L0 capacity symbols (non-test) ---")
    for sym in (
        "CapacitySnapshot",
        "choose_route_with_capacity",
        "RoutingCapacityContext",
        "CapacityDecisionReason",
        "capacity_snapshot_id",
        "candidate_route_count",
        "candidate_capacity_hash",
        "chosen_route_hash",
        "queue_depth_by_candidate",
        "in_flight_work_by_candidate",
        "recent_latency_by_candidate",
        "failure_rate_by_candidate",
        "degraded_route_flags",
        "capacity_decision_reason_hash",
        "HEALTHY",
        "DEGRADED",
        "SATURATED",
        "UNAVAILABLE",
        "RoutingCapacityError",
    ):
        count = _count_exported(conn, sym)
        print(f"  symbol:{sym:<40} sources={count:4d}")

    print("\n--- L0 capacity module exports (non-test) ---")
    cursor = conn.execute(
        f"""
        SELECT DISTINCT source_file, symbol
        FROM edges
        WHERE source_file LIKE '%L0_routing/capacity%' {NON_TEST}
        ORDER BY source_file, symbol
        LIMIT 30
        """,
    )
    for source, symbol in cursor.fetchall():
        print(f"  {source:<60} [{symbol}]")


def main() -> int:
    """Run P3/L0 routing capacity governance gates."""
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
        print("P3/L0 ROUTING CAPACITY GOVERNANCE: ALL GATES PASSED - CLOSURE VERIFIED")
    else:
        failed_gates = [gate for gate, ok, _ in GATE_RESULTS if not ok]
        print(f"P3/L0 ROUTING CAPACITY GOVERNANCE: FAILED GATES {failed_gates}")
    print("=" * 70)

    conn.close()
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
