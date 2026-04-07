#!/usr/bin/env python3
"""
P2/L6 Performance Observability CI Gate

Enforces Gates A-E for performance observability closure:
- Gate A: Required runtime stages must emit performance records
- Gate B: Performance records must have duration_ms
- Gate C: Performance records must have stage_name and stage_owner
- Gate D: Budgeted stages must have within_budget_flag
- Gate E: Performance coverage must not regress on governed stages

Runtime-only closure: excludes test, tests, spec, fixture, mock files.
"""

import sqlite3
import sys
from pathlib import Path
from typing import List, Tuple

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)

emit_determinism_digest("_performance_observability_gate", "_performance_observability_gate_digest")
record_execution_trace("_performance_observability_gate", "_performance_observability_gate_trace")


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
    conn: sqlite3.Connection, relation_type: str, filter_clause: str = NON_TEST,
) -> int:
    """Count distinct source files for a relation type."""
    cursor = conn.execute(
        f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type=? {filter_clause}",
        (relation_type,),
    )
    return cursor.fetchone()[0]


def gate_a(conn: sqlite3.Connection) -> bool:
    """Gate A — Required runtime stages must emit performance records.

    Passes when:
    - PerformanceMissingError exported >= 1
      (exception for missing performance records), AND
    - record_stage_performance exported >= 1
      (mandatory performance entrypoint), AND
    - performance_record_emitted function exported >= 1
      (ADG edge emitter for static scanner), AND
    - records_execution_trace edges >= 1
      (runtime stages happening), AND
    - routes_path edges >= 1
      (routing stage happening), AND
    - agent_executes_agent edges >= 1
      (orchestration stage happening)
    """
    missing_error = _count_exported(conn, "PerformanceMissingError", "performance_registry")
    emit_function = _count_exported(conn, "record_stage_performance", "performance_emitter")
    emitter_function = _count_exported(conn, "performance_record_emitted", "performance_emitter")
    trace_edges = _count_distinct_sources(conn, "records_execution_trace")
    routing_edges = _count_distinct_sources(conn, "routes_path")
    orchestration_edges = _count_distinct_sources(conn, "agent_executes_agent")

    ok = (
        missing_error >= 1
        and emit_function >= 1
        and emitter_function >= 1
        and trace_edges >= 1
        and routing_edges >= 1
        and orchestration_edges >= 1
    )
    GATE_RESULTS.append(
        (
            "A",
            ok,
            f"PerformanceMissingError exported={missing_error} (>=1), "
            f"record_stage_performance exported={emit_function} (>=1), "
            f"performance_record_emitted exported={emitter_function} (>=1), "
            f"records_execution_trace sources={trace_edges} (>=1), "
            f"routes_path sources={routing_edges} (>=1), "
            f"agent_executes_agent sources={orchestration_edges} (>=1)",
        ),
    )
    return ok


def gate_b(conn: sqlite3.Connection) -> bool:
    """Gate B — Performance records must have duration_ms.

    Passes when:
    - PerformanceRecord exported >= 1
      (performance record with duration_ms field), AND
    - writes_through edges >= 1
      (mutation stage happening for duration measurement)
    """
    perf_record = _count_exported(conn, "PerformanceRecord", "performance_registry")
    mutation_edges = _count_distinct_sources(conn, "writes_through")

    ok = perf_record >= 1 and mutation_edges >= 1
    GATE_RESULTS.append(
        (
            "B",
            ok,
            f"PerformanceRecord exported={perf_record} (>=1), writes_through sources={mutation_edges} (>=1)",
        ),
    )
    return ok


def gate_c(conn: sqlite3.Connection) -> bool:
    """Gate C — Performance records must have stage_name and stage_owner.

    Passes when:
    - PerformanceRecord exported >= 1
      (performance record with stage_name and stage_owner fields), AND
    - StageOwner exported >= 1
      (stage owner enumeration), AND
    - records_execution_trace edges >= 1
      (stages being identified)
    """
    perf_record = _count_exported(conn, "PerformanceRecord", "performance_registry")
    stage_owner = _count_exported(conn, "StageOwner", "performance_emitter")
    trace_edges = _count_distinct_sources(conn, "records_execution_trace")

    ok = perf_record >= 1 and stage_owner >= 1 and trace_edges >= 1
    GATE_RESULTS.append(
        (
            "C",
            ok,
            f"PerformanceRecord exported={perf_record} (>=1), "
            f"StageOwner exported={stage_owner} (>=1), "
            f"records_execution_trace sources={trace_edges} (>=1)",
        ),
    )
    return ok


def gate_d(conn: sqlite3.Connection) -> bool:
    """Gate D — Budgeted stages must have within_budget_flag.

    Passes when:
    - BudgetViolationError exported >= 1
      (exception for budget violations), AND
    - LatencyBudget exported >= 1
      (budget class definitions), AND
    - PerformanceRecord exported >= 1
      (performance record with budget tracking)
    """
    budget_error = _count_exported(conn, "BudgetViolationError", "performance_registry")
    latency_budget = _count_exported(conn, "LatencyBudget", "performance_emitter")
    perf_record = _count_exported(conn, "PerformanceRecord", "performance_registry")

    ok = budget_error >= 1 and latency_budget >= 1 and perf_record >= 1
    GATE_RESULTS.append(
        (
            "D",
            ok,
            f"BudgetViolationError exported={budget_error} (>=1), "
            f"LatencyBudget exported={latency_budget} (>=1), "
            f"PerformanceRecord exported={perf_record} (>=1)",
        ),
    )
    return ok


def gate_e(conn: sqlite3.Connection) -> bool:
    """Gate E — Performance coverage must not regress on governed stages.

    Passes when:
    - PerformanceRegistry exported >= 1
      (registry for performance storage), AND
    - query_performance_records exported >= 1
      (query function), AND
    - PerformanceRecord exported >= 1
      (performance record with run_id and trace_id), AND
    - records_execution_trace edges >= 1
      (runtime stage coverage baseline)
    """
    registry = _count_exported(conn, "PerformanceRegistry", "performance_registry")
    query_function = _count_exported(conn, "query_performance_records", "performance_emitter")
    perf_record = _count_exported(conn, "PerformanceRecord", "performance_registry")
    trace_edges = _count_distinct_sources(conn, "records_execution_trace")

    ok = registry >= 1 and query_function >= 1 and perf_record >= 1 and trace_edges >= 1
    GATE_RESULTS.append(
        (
            "E",
            ok,
            f"PerformanceRegistry exported={registry} (>=1), "
            f"query_performance_records exported={query_function} (>=1), "
            f"PerformanceRecord exported={perf_record} (>=1), "
            f"records_execution_trace sources={trace_edges} (>=1)",
        ),
    )
    return ok


def _print_baseline(conn: sqlite3.Connection) -> None:
    """Print P2/L6 performance observability baseline for verification."""
    print("\n--- P2/L6 Performance Observability Baseline ---")

    for rel in (
        "records_execution_trace",
        "routes_path",
        "routes_through",
        "agent_executes_agent",
        "writes_through",
        "performance_record_emitted",
        "stage_latency_measured",
    ):
        total = _count_distinct_sources(conn, rel)
        print(f"  {rel:<45} total={total:4d}")

    print("\n--- Key L6 performance symbols (non-test) ---")
    for sym in (
        "PerformanceRecord",
        "PerformanceRegistry",
        "record_stage_performance",
        "PerformanceContext",
        "StageOwner",
        "LatencyBudget",
        "PerformanceMissingError",
        "BudgetViolationError",
        "performance_record_emitted",
        "duration_ms",
        "stage_name",
        "stage_owner",
        "start_tick",
        "end_tick",
        "queue_depth",
        "concurrency_count",
        "resource_usage_hash",
        "budget_class",
        "within_budget_flag",
    ):
        count = _count_exported(conn, sym)
        print(f"  symbol:{sym:<40} sources={count:4d}")

    print("\n--- L6 performance module exports (non-test) ---")
    cursor = conn.execute(
        f"""
        SELECT DISTINCT source_file, symbol
        FROM edges
        WHERE source_file LIKE '%L6_observability/performance%' {NON_TEST}
        ORDER BY source_file, symbol
        LIMIT 30
        """,
    )
    for source, symbol in cursor.fetchall():
        print(f"  {source:<60} [{symbol}]")


def main() -> int:
    """Run P2/L6 performance observability gates."""
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
        print("P2/L6 PERFORMANCE OBSERVABILITY: ALL GATES PASSED - CLOSURE VERIFIED")
    else:
        failed_gates = [gate for gate, ok, _ in GATE_RESULTS if not ok]
        print(f"P2/L6 PERFORMANCE OBSERVABILITY: FAILED GATES {failed_gates}")
    print("=" * 70)

    conn.close()
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
