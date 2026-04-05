#!/usr/bin/env python3
"""
P3/L6 Observability Dashboard CI Gate

Enforces Gates A-E for observability dashboard closure:
- Gate A: Required dashboard views have runtime data source
- Gate B: Aggregate metrics can be computed for core stages
- Gate C: Degraded subsystem can be represented in health flags
- Gate D: Dashboard snapshots are queryable by time window
- Gate E: Raw telemetry exists and aggregation path exists

Runtime-only closure: excludes test, tests, spec, fixture, mock files.
"""

import sqlite3
import sys
from pathlib import Path
from typing import List, Tuple

from agentic_core.runtime.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)

emit_determinism_digest("_observability_dashboard_gate", "_observability_dashboard_gate_digest")
record_execution_trace("_observability_dashboard_gate", "_observability_dashboard_gate_trace")


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
    conn: sqlite3.Connection, relation_type: str, filter_clause: str = NON_TEST
) -> int:
    """Count distinct source files for a relation type."""
    cursor = conn.execute(
        f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type=? {filter_clause}",
        (relation_type,),
    )
    return cursor.fetchone()[0]


def gate_a(conn: sqlite3.Connection) -> bool:
    """Gate A — Required dashboard views have runtime data source.

    Passes when:
    - DashboardSnapshot exported >= 1
      (dashboard snapshot with 13 required fields), AND
    - aggregate_runtime_observability exported >= 1
      (mandatory aggregation entrypoint), AND
    - dashboard_aggregated function exported >= 1
      (ADG edge emitter for dashboard aggregation), AND
    - records_execution_trace edges >= 1
      (runtime telemetry data source), AND
    - routes_through edges >= 1
      (routing telemetry data source), AND
    - escalates_to_human edges >= 1
      (escalation telemetry data source)
    """
    dashboard_snapshot = _count_exported(conn, "DashboardSnapshot", "dashboard_aggregate")
    aggregate_function = _count_exported(conn, "aggregate_runtime_observability", "dashboard_orchestrator")
    emitter_function = _count_exported(conn, "dashboard_aggregated", "dashboard_orchestrator")
    trace_edges = _count_distinct_sources(conn, "records_execution_trace")
    routing_edges = _count_distinct_sources(conn, "routes_through")
    escalation_edges = _count_distinct_sources(conn, "escalates_to_human")

    ok = (
        dashboard_snapshot >= 1
        and aggregate_function >= 1
        and emitter_function >= 1
        and trace_edges >= 1
        and routing_edges >= 1
        and escalation_edges >= 1
    )
    GATE_RESULTS.append(
        (
            "A",
            ok,
            f"DashboardSnapshot exported={dashboard_snapshot} (>=1), "
            f"aggregate_runtime_observability exported={aggregate_function} (>=1), "
            f"dashboard_aggregated exported={emitter_function} (>=1), "
            f"records_execution_trace sources={trace_edges} (>=1), "
            f"routes_through sources={routing_edges} (>=1), "
            f"escalates_to_human sources={escalation_edges} (>=1)",
        )
    )
    return ok


def gate_b(conn: sqlite3.Connection) -> bool:
    """Gate B — Aggregate metrics can be computed for core stages.

    Passes when:
    - DashboardSnapshot exported >= 1
      (dashboard snapshot for metrics storage), AND
    - routing_throughput exported >= 1
      (routing throughput metric), AND
    - reasoning_throughput exported >= 1
      (reasoning throughput metric), AND
    - execution_success_rate exported >= 1
      (execution success rate metric), AND
    - metrics_collected function exported >= 1
      (ADG edge emitter for metrics collection), AND
    - records_execution_trace edges >= 1
      (runtime telemetry for metrics computation)
    """
    dashboard_snapshot = _count_exported(conn, "DashboardSnapshot", "dashboard_aggregate")
    routing_throughput = _count_exported(conn, "routing_throughput", "dashboard_aggregate")
    reasoning_throughput = _count_exported(conn, "reasoning_throughput", "dashboard_aggregate")
    success_rate = _count_exported(conn, "execution_success_rate", "dashboard_aggregate")
    metrics_emitter = _count_exported(conn, "metrics_collected", "dashboard_orchestrator")
    trace_edges = _count_distinct_sources(conn, "records_execution_trace")

    ok = (
        dashboard_snapshot >= 1
        and routing_throughput >= 1
        and reasoning_throughput >= 1
        and success_rate >= 1
        and metrics_emitter >= 1
        and trace_edges >= 1
    )
    GATE_RESULTS.append(
        (
            "B",
            ok,
            f"DashboardSnapshot exported={dashboard_snapshot} (>=1), "
            f"routing_throughput exported={routing_throughput} (>=1), "
            f"reasoning_throughput exported={reasoning_throughput} (>=1), "
            f"execution_success_rate exported={success_rate} (>=1), "
            f"metrics_collected exported={metrics_emitter} (>=1), "
            f"records_execution_trace sources={trace_edges} (>=1)",
        )
    )
    return ok


def gate_c(conn: sqlite3.Connection) -> bool:
    """Gate C — Degraded subsystem can be represented in health flags.

    Passes when:
    - HealthFlag exported >= 1
      (health flag enumeration), AND
    - HEALTHY status exported >= 1
      (healthy status), AND
    - DEGRADED status exported >= 1
      (degraded status), AND
    - CRITICAL status exported >= 1
      (critical status), AND
    - health_computed function exported >= 1
      (ADG edge emitter for health computation), AND
    - degraded_component_flags exported >= 1
      (degraded component flags field)
    """
    health_flag = _count_exported(conn, "HealthFlag", "dashboard_aggregate")
    healthy_status = _count_exported(conn, "HEALTHY", "dashboard_aggregate")
    degraded_status = _count_exported(conn, "DEGRADED", "dashboard_aggregate")
    critical_status = _count_exported(conn, "CRITICAL", "dashboard_aggregate")
    health_emitter = _count_exported(conn, "health_computed", "dashboard_orchestrator")
    degraded_flags = _count_exported(conn, "degraded_component_flags", "dashboard_aggregate")

    ok = (
        health_flag >= 1
        and healthy_status >= 1
        and degraded_status >= 1
        and critical_status >= 1
        and health_emitter >= 1
        and degraded_flags >= 1
    )
    GATE_RESULTS.append(
        (
            "C",
            ok,
            f"HealthFlag exported={health_flag} (>=1), "
            f"HEALTHY exported={healthy_status} (>=1), "
            f"DEGRADED exported={degraded_status} (>=1), "
            f"CRITICAL exported={critical_status} (>=1), "
            f"health_computed exported={health_emitter} (>=1), "
            f"degraded_component_flags exported={degraded_flags} (>=1)",
        )
    )
    return ok


def gate_d(conn: sqlite3.Connection) -> bool:
    """Gate D — Dashboard snapshots are queryable by time window.

    Passes when:
    - DashboardSnapshot exported >= 1
      (dashboard snapshot for time window queries), AND
    - dashboard_snapshot_id exported >= 1
      (snapshot ID for time window queries), AND
    - snapshot_tick exported >= 1
      (snapshot tick for time window queries), AND
    - query_dashboard_snapshots exported >= 1
      (time window query function), AND
    - snapshot_persisted function exported >= 1
      (ADG edge emitter for snapshot persistence), AND
    - query_exposed function exported >= 1
      (ADG edge emitter for query API exposure)
    """
    dashboard_snapshot = _count_exported(conn, "DashboardSnapshot", "dashboard_aggregate")
    snapshot_id = _count_exported(conn, "dashboard_snapshot_id", "dashboard_aggregate")
    snapshot_tick = _count_exported(conn, "snapshot_tick", "dashboard_aggregate")
    query_function = _count_exported(conn, "query_dashboard_snapshots", "dashboard_orchestrator")
    snapshot_emitter = _count_exported(conn, "snapshot_persisted", "dashboard_orchestrator")
    query_emitter = _count_exported(conn, "query_exposed", "dashboard_orchestrator")

    ok = (
        dashboard_snapshot >= 1
        and snapshot_id >= 1
        and snapshot_tick >= 1
        and query_function >= 1
        and snapshot_emitter >= 1
        and query_emitter >= 1
    )
    GATE_RESULTS.append(
        (
            "D",
            ok,
            f"DashboardSnapshot exported={dashboard_snapshot} (>=1), "
            f"dashboard_snapshot_id exported={snapshot_id} (>=1), "
            f"snapshot_tick exported={snapshot_tick} (>=1), "
            f"query_dashboard_snapshots exported={query_function} (>=1), "
            f"snapshot_persisted exported={snapshot_emitter} (>=1), "
            f"query_exposed exported={query_emitter} (>=1)",
        )
    )
    return ok


def gate_e(conn: sqlite3.Connection) -> bool:
    """Gate E — Raw telemetry exists and aggregation path exists.

    Passes when:
    - DashboardAggregate exported >= 1
      (dashboard aggregate for aggregation path), AND
    - TelemetryWindow exported >= 1
      (telemetry window for aggregation), AND
    - DashboardPolicy exported >= 1
      (dashboard policy for aggregation), AND
    - aggregate_runtime_observability exported >= 1
      (aggregation path entrypoint), AND
    - records_execution_trace edges >= 1
      (raw telemetry exists), AND
    - dashboard_aggregated function exported >= 1
      (aggregation path completion)
    """
    dashboard_aggregate = _count_exported(conn, "DashboardAggregate", "dashboard_aggregate")
    telemetry_window = _count_exported(conn, "TelemetryWindow", "dashboard_orchestrator")
    dashboard_policy = _count_exported(conn, "DashboardPolicy", "dashboard_orchestrator")
    aggregate_function = _count_exported(conn, "aggregate_runtime_observability", "dashboard_orchestrator")
    trace_edges = _count_distinct_sources(conn, "records_execution_trace")
    dashboard_emitter = _count_exported(conn, "dashboard_aggregated", "dashboard_orchestrator")

    ok = (
        dashboard_aggregate >= 1
        and telemetry_window >= 1
        and dashboard_policy >= 1
        and aggregate_function >= 1
        and trace_edges >= 1
        and dashboard_emitter >= 1
    )
    GATE_RESULTS.append(
        (
            "E",
            ok,
            f"DashboardAggregate exported={dashboard_aggregate} (>=1), "
            f"TelemetryWindow exported={telemetry_window} (>=1), "
            f"DashboardPolicy exported={dashboard_policy} (>=1), "
            f"aggregate_runtime_observability exported={aggregate_function} (>=1), "
            f"records_execution_trace sources={trace_edges} (>=1), "
            f"dashboard_aggregated exported={dashboard_emitter} (>=1)",
        )
    )
    return ok


def _print_baseline(conn: sqlite3.Connection) -> None:
    """Print P3/L6 observability dashboard baseline for verification."""
    print("\n--- P3/L6 Observability Dashboard Baseline ---")

    for rel in (
        "records_execution_trace",
        "routes_through",
        "escalates_to_human",
        "requires_human_review",
        "dashboard_aggregated",
        "health_computed",
        "metrics_collected",
        "snapshot_persisted",
        "query_exposed",
    ):
        total = _count_distinct_sources(conn, rel)
        print(f"  {rel:<45} total={total:4d}")

    print("\n--- Key L6 dashboard symbols (non-test) ---")
    for sym in (
        "DashboardSnapshot",
        "DashboardAggregate",
        "aggregate_runtime_observability",
        "HealthFlag",
        "TelemetryWindow",
        "DashboardPolicy",
        "dashboard_snapshot_id",
        "snapshot_tick",
        "active_run_count",
        "routing_throughput",
        "reasoning_throughput",
        "execution_success_rate",
        "execution_failure_rate",
        "policy_block_rate",
        "human_escalation_rate",
        "queue_depth_summary",
        "median_latency_by_stage",
        "p95_latency_by_stage",
        "degraded_component_flags",
        "HEALTHY",
        "DEGRADED",
        "CRITICAL",
        "UNKNOWN",
        "DashboardAggregateError",
    ):
        count = _count_exported(conn, sym)
        print(f"  symbol:{sym:<40} sources={count:4d}")

    print("\n--- L6 dashboard module exports (non-test) ---")
    cursor = conn.execute(
        f"""
        SELECT DISTINCT source_file, symbol
        FROM edges
        WHERE source_file LIKE '%L6_observability/dashboard%' {NON_TEST}
        ORDER BY source_file, symbol
        LIMIT 30
        """
    )
    for source, symbol in cursor.fetchall():
        print(f"  {source:<60} [{symbol}]")


def main() -> int:
    """Run P3/L6 observability dashboard gates."""
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
        print("P3/L6 OBSERVABILITY DASHBOARD: ALL GATES PASSED - CLOSURE VERIFIED")
    else:
        failed_gates = [gate for gate, ok, _ in GATE_RESULTS if not ok]
        print(f"P3/L6 OBSERVABILITY DASHBOARD: FAILED GATES {failed_gates}")
    print("=" * 70)

    conn.close()
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
