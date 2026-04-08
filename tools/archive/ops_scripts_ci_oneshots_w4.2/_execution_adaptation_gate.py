#!/usr/bin/env python3
"""
P4/L2 Execution Adaptation CI Gate

Enforces Gates A-E for execution adaptation closure:
- Gate A: Adaptive strategy chosen without historical metrics
- Gate B: Execution strategy lacks evaluation score
- Gate C: Adaptation changes behavior without trace record
- Gate D: Unsafe strategy selected
- Gate E: Adaptation occurs without policy compliance check

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
    """Gate A — Adaptive strategy chosen without historical metrics.

    Passes when:
    - ExecutionAdaptationRecord exported >= 1
      (execution adaptation record with 9 required fields), AND
    - choose_execution_strategy exported >= 1
      (mandatory strategy selection entrypoint), AND
    - execution_strategy_chosen exported >= 1
      (ADG edge emitter for strategy selection), AND
    - historical_success_rate exported >= 1
      (historical success rate field), AND
    - historical_failure_rate exported >= 1
      (historical failure rate field), AND
    - HistoricalMetrics exported >= 1
      (historical metrics context)
    """
    adaptation_record = _count_exported(conn, "ExecutionAdaptationRecord", "execution_adaptation")
    choose_function = _count_exported(conn, "choose_execution_strategy", "adaptation_orchestrator")
    strategy_emitter = _count_exported(conn, "execution_strategy_chosen", "adaptation_orchestrator")
    success_rate = _count_exported(conn, "historical_success_rate", "execution_adaptation")
    failure_rate = _count_exported(conn, "historical_failure_rate", "execution_adaptation")
    metrics_context = _count_exported(conn, "HistoricalMetrics", "adaptation_orchestrator")

    ok = (
        adaptation_record >= 1
        and choose_function >= 1
        and strategy_emitter >= 1
        and success_rate >= 1
        and failure_rate >= 1
        and metrics_context >= 1
    )
    GATE_RESULTS.append(
        (
            "A",
            ok,
            f"ExecutionAdaptationRecord exported={adaptation_record} (>=1), "
            f"choose_execution_strategy exported={choose_function} (>=1), "
            f"execution_strategy_chosen exported={strategy_emitter} (>=1), "
            f"historical_success_rate exported={success_rate} (>=1), "
            f"historical_failure_rate exported={failure_rate} (>=1), "
            f"HistoricalMetrics exported={metrics_context} (>=1)",
        ),
    )
    return ok


def gate_b(conn: sqlite3.Connection) -> bool:
    """Gate B — Execution strategy lacks evaluation score.

    Passes when:
    - ExecutionAdaptationRecord exported >= 1
      (execution adaptation record for strategy evaluation), AND
    - execution_strategy_hash exported >= 1
      (execution strategy hash field), AND
    - chosen_strategy_hash exported >= 1
      (chosen strategy hash field), AND
    - latency_profile_hash exported >= 1
      (latency profile hash field), AND
    - strategy_evaluated exported >= 1
      (ADG edge emitter for strategy evaluation), AND
    - ExecutionStrategy exported >= 1
      (execution strategy context)
    """
    adaptation_record = _count_exported(conn, "ExecutionAdaptationRecord", "execution_adaptation")
    strategy_hash = _count_exported(conn, "execution_strategy_hash", "execution_adaptation")
    chosen_hash = _count_exported(conn, "chosen_strategy_hash", "execution_adaptation")
    latency_hash = _count_exported(conn, "latency_profile_hash", "execution_adaptation")
    evaluation_emitter = _count_exported(conn, "strategy_evaluated", "adaptation_orchestrator")
    strategy_context = _count_exported(conn, "ExecutionStrategy", "adaptation_orchestrator")

    ok = (
        adaptation_record >= 1
        and strategy_hash >= 1
        and chosen_hash >= 1
        and latency_hash >= 1
        and evaluation_emitter >= 1
        and strategy_context >= 1
    )
    GATE_RESULTS.append(
        (
            "B",
            ok,
            f"ExecutionAdaptationRecord exported={adaptation_record} (>=1), "
            f"execution_strategy_hash exported={strategy_hash} (>=1), "
            f"chosen_strategy_hash exported={chosen_hash} (>=1), "
            f"latency_profile_hash exported={latency_hash} (>=1), "
            f"strategy_evaluated exported={evaluation_emitter} (>=1), "
            f"ExecutionStrategy exported={strategy_context} (>=1)",
        ),
    )
    return ok


def gate_c(conn: sqlite3.Connection) -> bool:
    """Gate C — Adaptation changes behavior without trace record.

    Passes when:
    - ExecutionAdaptationRecord exported >= 1
      (execution adaptation record for trace linkage), AND
    - execution_adaptation_id exported >= 1
      (execution adaptation ID field), AND
    - run_id exported >= 1
      (run ID field for trace linkage), AND
    - trace_id exported >= 1
      (trace ID field for trace linkage), AND
    - records_execution_trace edges >= 1
      (execution trace linkage), AND
    - ExecutionContext exported >= 1
      (execution context for trace linkage)
    """
    adaptation_record = _count_exported(conn, "ExecutionAdaptationRecord", "execution_adaptation")
    adaptation_id = _count_exported(conn, "execution_adaptation_id", "execution_adaptation")
    run_id = _count_exported(conn, "run_id", "execution_adaptation")
    trace_id = _count_exported(conn, "trace_id", "execution_adaptation")
    trace_edges = _count_distinct_sources(conn, "records_execution_trace")
    execution_context = _count_exported(conn, "ExecutionContext", "adaptation_orchestrator")

    ok = (
        adaptation_record >= 1
        and adaptation_id >= 1
        and run_id >= 1
        and trace_id >= 1
        and trace_edges >= 1
        and execution_context >= 1
    )
    GATE_RESULTS.append(
        (
            "C",
            ok,
            f"ExecutionAdaptationRecord exported={adaptation_record} (>=1), "
            f"execution_adaptation_id exported={adaptation_id} (>=1), "
            f"run_id exported={run_id} (>=1), "
            f"trace_id exported={trace_id} (>=1), "
            f"records_execution_trace sources={trace_edges} (>=1), "
            f"ExecutionContext exported={execution_context} (>=1)",
        ),
    )
    return ok


def gate_d(conn: sqlite3.Connection) -> bool:
    """Gate D — Unsafe strategy selected.

    Passes when:
    - ExecutionAdaptationRecord exported >= 1
      (execution adaptation record for safety tracking), AND
    - evaluate_strategy_safety exported >= 1
      (safety evaluation function), AND
    - unsafe_strategy_rejected exported >= 1
      (ADG edge emitter for unsafe strategy rejection), AND
    - ExecutionStrategy exported >= 1
      (execution strategy with safety score), AND
    - choose_execution_strategy exported >= 1
      (strategy selection with safety guard)
    """
    adaptation_record = _count_exported(conn, "ExecutionAdaptationRecord", "execution_adaptation")
    safety_function = _count_exported(conn, "evaluate_strategy_safety", "adaptation_orchestrator")
    unsafe_emitter = _count_exported(conn, "unsafe_strategy_rejected", "adaptation_orchestrator")
    strategy_context = _count_exported(conn, "ExecutionStrategy", "adaptation_orchestrator")
    choose_function = _count_exported(conn, "choose_execution_strategy", "adaptation_orchestrator")

    ok = (
        adaptation_record >= 1
        and safety_function >= 1
        and unsafe_emitter >= 1
        and strategy_context >= 1
        and choose_function >= 1
    )
    GATE_RESULTS.append(
        (
            "D",
            ok,
            f"ExecutionAdaptationRecord exported={adaptation_record} (>=1), "
            f"evaluate_strategy_safety exported={safety_function} (>=1), "
            f"unsafe_strategy_rejected exported={unsafe_emitter} (>=1), "
            f"ExecutionStrategy exported={strategy_context} (>=1), "
            f"choose_execution_strategy exported={choose_function} (>=1)",
        ),
    )
    return ok


def gate_e(conn: sqlite3.Connection) -> bool:
    """Gate E — Adaptation occurs without policy compliance check.

    Passes when:
    - ExecutionAdaptationRecord exported >= 1
      (execution adaptation record for policy compliance), AND
    - adaptation_reason_hash exported >= 1
      (adaptation reason hash for policy tracking), AND
    - check_policy_compliance exported >= 1
      (policy compliance check function), AND
    - policy_compliance_checked exported >= 1
      (ADG edge emitter for policy compliance), AND
    - ExecutionContext exported >= 1
      (execution context with policy requirements)
    """
    adaptation_record = _count_exported(conn, "ExecutionAdaptationRecord", "execution_adaptation")
    reason_hash = _count_exported(conn, "adaptation_reason_hash", "execution_adaptation")
    compliance_function = _count_exported(conn, "check_policy_compliance", "adaptation_orchestrator")
    compliance_emitter = _count_exported(conn, "policy_compliance_checked", "adaptation_orchestrator")
    execution_context = _count_exported(conn, "ExecutionContext", "adaptation_orchestrator")

    ok = (
        adaptation_record >= 1
        and reason_hash >= 1
        and compliance_function >= 1
        and compliance_emitter >= 1
        and execution_context >= 1
    )
    GATE_RESULTS.append(
        (
            "E",
            ok,
            f"ExecutionAdaptationRecord exported={adaptation_record} (>=1), "
            f"adaptation_reason_hash exported={reason_hash} (>=1), "
            f"check_policy_compliance exported={compliance_function} (>=1), "
            f"policy_compliance_checked exported={compliance_emitter} (>=1), "
            f"ExecutionContext exported={execution_context} (>=1)",
        ),
    )
    return ok


def _print_baseline(conn: sqlite3.Connection) -> None:
    """Print P4/L2 execution adaptation baseline for verification."""
    print("\n--- P4/L2 Execution Adaptation Baseline ---")

    for rel in (
        "records_execution_trace",
        "invokes_dynamic",
        "execution_strategy_chosen",
        "execution_adapted",
        "strategy_evaluated",
        "unsafe_strategy_rejected",
        "policy_compliance_checked",
    ):
        total = _count_distinct_sources(conn, rel)
        print(f"  {rel:<45} total={total:4d}")

    print("\n--- Key L2 execution adaptation symbols (non-test) ---")
    for sym in (
        "ExecutionAdaptationRecord",
        "choose_execution_strategy",
        "ExecutionAdaptationError",
        "execution_adaptation_id",
        "run_id",
        "trace_id",
        "execution_strategy_hash",
        "historical_success_rate",
        "historical_failure_rate",
        "latency_profile_hash",
        "chosen_strategy_hash",
        "adaptation_reason_hash",
    ):
        count = _count_exported(conn, sym)
        print(f"  symbol:{sym:<40} sources={count:4d}")

    print("\n--- L2 execution adaptation module exports (non-test) ---")
    cursor = conn.execute(
        f"""
        SELECT DISTINCT source_file, symbol
        FROM edges
        WHERE source_file LIKE '%L2_execution/adaptation%' {NON_TEST}
        ORDER BY source_file, symbol
        LIMIT 30
        """,
    )
    for source, symbol in cursor.fetchall():
        print(f"  {source:<60} [{symbol}]")


def main() -> int:
    """Run P4/L2 execution adaptation gates."""
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
        print("P4/L2 EXECUTION ADAPTATION: ALL GATES PASSED - CLOSURE VERIFIED")
    else:
        failed_gates = [gate for gate, ok, _ in GATE_RESULTS if not ok]
        print(f"P4/L2 EXECUTION ADAPTATION: FAILED GATES {failed_gates}")
    print("=" * 70)

    conn.close()
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
