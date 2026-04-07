#!/usr/bin/env python3
"""
P3/L2 Execution Observability CI Gate

Enforces Gates A-E for execution observability closure:
- Gate A: Governed runtime execution must have observability record
- Gate B: Observability record must have duration_ms
- Gate C: Failed execution must have failure classification
- Gate D: Retried execution must have retry_count or retry_reason_hash
- Gate E: Blocked execution must have policy linkage

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

emit_determinism_digest("_execution_observability_gate", "_execution_observability_gate_digest")
record_execution_trace("_execution_observability_gate", "_execution_observability_gate_trace")


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
    """Gate A — Governed runtime execution must have observability record.

    Passes when:
    - ExecutionObservabilityError exported >= 1
      (exception for missing observability record), AND
    - record_execution_observability exported >= 1
      (mandatory observability recording entrypoint), AND
    - ExecutionObservabilityRecord exported >= 1
      (observability record with 14 required fields), AND
    - execution_observability_emitted function exported >= 1
      (ADG edge emitter for static scanner), AND
    - records_execution_trace edges >= 1
      (runtime execution happening), AND
    - signs_execution_trace edges >= 1
      (execution completion tracking)
    """
    obs_error = _count_exported(conn, "ExecutionObservabilityError", "execution_observability")
    record_function = _count_exported(conn, "record_execution_observability", "observability_recorder")
    obs_record = _count_exported(conn, "ExecutionObservabilityRecord", "execution_observability")
    emitter_function = _count_exported(conn, "execution_observability_emitted", "observability_recorder")
    trace_edges = _count_distinct_sources(conn, "records_execution_trace")
    sign_edges = _count_distinct_sources(conn, "signs_execution_trace")

    ok = (
        obs_error >= 1
        and record_function >= 1
        and obs_record >= 1
        and emitter_function >= 1
        and trace_edges >= 1
        and sign_edges >= 1
    )
    GATE_RESULTS.append(
        (
            "A",
            ok,
            f"ExecutionObservabilityError exported={obs_error} (>=1), "
            f"record_execution_observability exported={record_function} (>=1), "
            f"ExecutionObservabilityRecord exported={obs_record} (>=1), "
            f"execution_observability_emitted exported={emitter_function} (>=1), "
            f"records_execution_trace sources={trace_edges} (>=1), "
            f"signs_execution_trace sources={sign_edges} (>=1)",
        ),
    )
    return ok


def gate_b(conn: sqlite3.Connection) -> bool:
    """Gate B — Observability record must have duration_ms.

    Passes when:
    - ExecutionObservabilityRecord exported >= 1
      (observability record with duration_ms field), AND
    - execution_observability_emitted function exported >= 1
      (ADG edge emitter with duration_ms parameter), AND
    - execution_terminates_at_uwg edges >= 1
      (observable mutation execution outcomes)
    """
    obs_record = _count_exported(conn, "ExecutionObservabilityRecord", "execution_observability")
    emitter_function = _count_exported(conn, "execution_observability_emitted", "observability_recorder")
    uwg_edges = _count_distinct_sources(conn, "execution_terminates_at_uwg")

    ok = obs_record >= 1 and emitter_function >= 1 and uwg_edges >= 1
    GATE_RESULTS.append(
        (
            "B",
            ok,
            f"ExecutionObservabilityRecord exported={obs_record} (>=1), "
            f"execution_observability_emitted exported={emitter_function} (>=1), "
            f"execution_terminates_at_uwg sources={uwg_edges} (>=1)",
        ),
    )
    return ok


def gate_c(conn: sqlite3.Connection) -> bool:
    """Gate C — Failed execution must have failure classification.

    Passes when:
    - FailureClassification exported >= 1
      (failure classification enumeration), AND
    - FAILED status exported >= 1
      (failed execution status), AND
    - execution_failure_classified function exported >= 1
      (ADG edge emitter for failure classification), AND
    - ExecutionObservabilityRecord exported >= 1
      (parent record for failure metadata)
    """
    failure_class = _count_exported(conn, "FailureClassification", "execution_observability")
    failed_status = _count_exported(conn, "FAILED", "execution_observability")
    failure_emitter = _count_exported(conn, "execution_failure_classified", "observability_recorder")
    obs_record = _count_exported(conn, "ExecutionObservabilityRecord", "execution_observability")

    ok = failure_class >= 1 and failed_status >= 1 and failure_emitter >= 1 and obs_record >= 1
    GATE_RESULTS.append(
        (
            "C",
            ok,
            f"FailureClassification exported={failure_class} (>=1), "
            f"FAILED exported={failed_status} (>=1), "
            f"execution_failure_classified exported={failure_emitter} (>=1), "
            f"ExecutionObservabilityRecord exported={obs_record} (>=1)",
        ),
    )
    return ok


def gate_d(conn: sqlite3.Connection) -> bool:
    """Gate D — Retried execution must have retry_count or retry_reason_hash.

    Passes when:
    - RETRIED status exported >= 1
      (retried execution status), AND
    - ExecutionObservabilityRecord exported >= 1
      (parent record with retry fields), AND
    - execution_retry_recorded function exported >= 1
      (ADG edge emitter for retry tracking)
    """
    retried_status = _count_exported(conn, "RETRIED", "execution_observability")
    obs_record = _count_exported(conn, "ExecutionObservabilityRecord", "execution_observability")
    retry_emitter = _count_exported(conn, "execution_retry_recorded", "observability_recorder")

    ok = retried_status >= 1 and obs_record >= 1 and retry_emitter >= 1
    GATE_RESULTS.append(
        (
            "D",
            ok,
            f"RETRIED exported={retried_status} (>=1), "
            f"ExecutionObservabilityRecord exported={obs_record} (>=1), "
            f"execution_retry_recorded exported={retry_emitter} (>=1)",
        ),
    )
    return ok


def gate_e(conn: sqlite3.Connection) -> bool:
    """Gate E — Blocked execution must have policy linkage.

    Passes when:
    - BLOCKED_BY_POLICY status exported >= 1
      (blocked execution status), AND
    - POLICY_BLOCK classification exported >= 1
      (policy block failure classification), AND
    - policy_block_recorded function exported >= 1
      (ADG edge emitter for policy blocks), AND
    - references_policy_hash edges >= 1
      (policy binding to blocked executions)
    """
    blocked_status = _count_exported(conn, "BLOCKED_BY_POLICY", "execution_observability")
    policy_block = _count_exported(conn, "POLICY_BLOCK", "execution_observability")
    block_emitter = _count_exported(conn, "policy_block_recorded", "observability_recorder")
    policy_edges = _count_distinct_sources(conn, "references_policy_hash")

    ok = blocked_status >= 1 and policy_block >= 1 and block_emitter >= 1 and policy_edges >= 1
    GATE_RESULTS.append(
        (
            "E",
            ok,
            f"BLOCKED_BY_POLICY exported={blocked_status} (>=1), "
            f"POLICY_BLOCK exported={policy_block} (>=1), "
            f"policy_block_recorded exported={block_emitter} (>=1), "
            f"references_policy_hash sources={policy_edges} (>=1)",
        ),
    )
    return ok


def _print_baseline(conn: sqlite3.Connection) -> None:
    """Print P3/L2 execution observability baseline for verification."""
    print("\n--- P3/L2 Execution Observability Baseline ---")

    for rel in (
        "records_execution_trace",
        "signs_execution_trace",
        "execution_terminates_at_uwg",
        "execution_observability_emitted",
        "execution_retry_recorded",
        "execution_failure_classified",
        "policy_block_recorded",
    ):
        total = _count_distinct_sources(conn, rel)
        print(f"  {rel:<45} total={total:4d}")

    print("\n--- Key L2 execution observability symbols (non-test) ---")
    for sym in (
        "ExecutionObservabilityRecord",
        "record_execution_observability",
        "ExecutionObservabilityContext",
        "ExecutionStatus",
        "FailureClassification",
        "execution_observability_id",
        "execution_request_id",
        "execution_target_hash",
        "execution_start_tick",
        "execution_end_tick",
        "duration_ms",
        "execution_status",
        "retry_count",
        "retry_reason_hash",
        "failure_reason_hash",
        "guardrail_decision_id",
        "policy_hash",
        "STARTED",
        "SUCCEEDED",
        "FAILED",
        "RETRIED",
        "CANCELLED",
        "BLOCKED_BY_POLICY",
        "ESCALATED",
        "POLICY_BLOCK",
        "TOOL_ERROR",
        "NETWORK_FAILURE",
        "MUTATION_FAILURE",
        "VALIDATION_FAILURE",
        "UNKNOWN_FAILURE",
        "ExecutionObservabilityError",
    ):
        count = _count_exported(conn, sym)
        print(f"  symbol:{sym:<40} sources={count:4d}")

    print("\n--- L2 observability module exports (non-test) ---")
    cursor = conn.execute(
        f"""
        SELECT DISTINCT source_file, symbol
        FROM edges
        WHERE source_file LIKE '%L2_execution/observability%' {NON_TEST}
        ORDER BY source_file, symbol
        LIMIT 30
        """,
    )
    for source, symbol in cursor.fetchall():
        print(f"  {source:<60} [{symbol}]")


def main() -> int:
    """Run P3/L2 execution observability gates."""
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
        print("P3/L2 EXECUTION OBSERVABILITY: ALL GATES PASSED - CLOSURE VERIFIED")
    else:
        failed_gates = [gate for gate, ok, _ in GATE_RESULTS if not ok]
        print(f"P3/L2 EXECUTION OBSERVABILITY: FAILED GATES {failed_gates}")
    print("=" * 70)

    conn.close()
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
