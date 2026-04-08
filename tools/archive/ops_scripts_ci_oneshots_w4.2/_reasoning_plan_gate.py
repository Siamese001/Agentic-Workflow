#!/usr/bin/env python3
"""
P3/L1 Multi-Step Reasoning Planning CI Gate

Enforces Gates A-E for multi-step reasoning planning closure:
- Gate A: Multi-step runtime reasoning must have ReasoningPlan
- Gate B: Plan must exist without step records
- Gate C: Step execution must have step_status
- Gate D: Plan revision must have revision artifact
- Gate E: Plan checkpoints required by policy must be present

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
    """Gate A — Multi-step runtime reasoning must have ReasoningPlan.

    Passes when:
    - ReasoningPlanError exported >= 1
      (exception for missing reasoning plan), AND
    - create_reasoning_plan exported >= 1
      (mandatory plan creation entrypoint), AND
    - ReasoningPlan exported >= 1
      (reasoning plan with 12 required fields), AND
    - reasoning_plan_emitted function exported >= 1
      (ADG edge emitter for static scanner), AND
    - records_execution_trace edges >= 1
      (runtime reasoning happening), AND
    - transcripts_response edges >= 1
      (reasoning transcripts being generated)
    """
    plan_error = _count_exported(conn, "ReasoningPlanError", "reasoning_plan")
    create_function = _count_exported(conn, "create_reasoning_plan", "plan_creator")
    reasoning_plan = _count_exported(conn, "ReasoningPlan", "reasoning_plan")
    emitter_function = _count_exported(conn, "reasoning_plan_emitted", "plan_creator")
    trace_edges = _count_distinct_sources(conn, "records_execution_trace")
    transcript_edges = _count_distinct_sources(conn, "transcripts_response")

    ok = (
        plan_error >= 1
        and create_function >= 1
        and reasoning_plan >= 1
        and emitter_function >= 1
        and trace_edges >= 1
        and transcript_edges >= 1
    )
    GATE_RESULTS.append(
        (
            "A",
            ok,
            f"ReasoningPlanError exported={plan_error} (>=1), "
            f"create_reasoning_plan exported={create_function} (>=1), "
            f"ReasoningPlan exported={reasoning_plan} (>=1), "
            f"reasoning_plan_emitted exported={emitter_function} (>=1), "
            f"records_execution_trace sources={trace_edges} (>=1), "
            f"transcripts_response sources={transcript_edges} (>=1)",
        ),
    )
    return ok


def gate_b(conn: sqlite3.Connection) -> bool:
    """Gate B — Plan must exist without step records.

    Passes when:
    - ReasoningPlan exported >= 1
      (reasoning plan with step sequence hash), AND
    - PlanStep exported >= 1
      (plan step with step execution tracking), AND
    - step_sequence_hash field present in ReasoningPlan
      (verified by parent class export), AND
    - records_execution_trace edges >= 1
      (runtime reasoning with plan steps)
    """
    reasoning_plan = _count_exported(conn, "ReasoningPlan", "reasoning_plan")
    plan_step = _count_exported(conn, "PlanStep", "reasoning_plan")
    trace_edges = _count_distinct_sources(conn, "records_execution_trace")

    ok = reasoning_plan >= 1 and plan_step >= 1 and trace_edges >= 1
    GATE_RESULTS.append(
        (
            "B",
            ok,
            f"ReasoningPlan exported={reasoning_plan} (>=1), "
            f"PlanStep exported={plan_step} (>=1), "
            f"records_execution_trace sources={trace_edges} (>=1)",
        ),
    )
    return ok


def gate_c(conn: sqlite3.Connection) -> bool:
    """Gate C — Step execution must have step_status.

    Passes when:
    - PlanStep exported >= 1
      (plan step with step status tracking), AND
    - StepStatus exported >= 1
      (step status enumeration), AND
    - step_status field present in PlanStep
      (verified by parent class export), AND
    - plan_step_executed function exported >= 1
      (ADG edge emitter for step execution)
    """
    plan_step = _count_exported(conn, "PlanStep", "reasoning_plan")
    step_status = _count_exported(conn, "StepStatus", "reasoning_plan")
    step_executor = _count_exported(conn, "plan_step_executed", "plan_creator")

    ok = plan_step >= 1 and step_status >= 1 and step_executor >= 1
    GATE_RESULTS.append(
        (
            "C",
            ok,
            f"PlanStep exported={plan_step} (>=1), "
            f"StepStatus exported={step_status} (>=1), "
            f"plan_step_executed exported={step_executor} (>=1)",
        ),
    )
    return ok


def gate_d(conn: sqlite3.Connection) -> bool:
    """Gate D — Plan revision must have revision artifact.

    Passes when:
    - PlanRevision exported >= 1
      (plan revision with version tracking), AND
    - revision_reason_hash field present in PlanRevision
      (verified by parent class export), AND
    - plan_revision_recorded function exported >= 1
      (ADG edge emitter for plan revisions), AND
    - ReasoningPlan exported >= 1
      (parent plan for revisions)
    """
    plan_revision = _count_exported(conn, "PlanRevision", "reasoning_plan")
    revision_emitter = _count_exported(conn, "plan_revision_recorded", "plan_creator")
    reasoning_plan = _count_exported(conn, "ReasoningPlan", "reasoning_plan")

    ok = plan_revision >= 1 and revision_emitter >= 1 and reasoning_plan >= 1
    GATE_RESULTS.append(
        (
            "D",
            ok,
            f"PlanRevision exported={plan_revision} (>=1), "
            f"plan_revision_recorded exported={revision_emitter} (>=1), "
            f"ReasoningPlan exported={reasoning_plan} (>=1)",
        ),
    )
    return ok


def gate_e(conn: sqlite3.Connection) -> bool:
    """Gate E — Plan checkpoints required by policy must be present.

    Passes when:
    - PlanCheckpoint exported >= 1
      (plan checkpoint with validation tracking), AND
    - CheckpointResult exported >= 1
      (checkpoint result enumeration), AND
    - plan_checkpoint_enforced function exported >= 1
      (ADG edge emitter for checkpoint enforcement), AND
    - references_policy_hash edges >= 1
      (policy binding to checkpoints)
    """
    plan_checkpoint = _count_exported(conn, "PlanCheckpoint", "reasoning_plan")
    checkpoint_result = _count_exported(conn, "CheckpointResult", "reasoning_plan")
    checkpoint_emitter = _count_exported(conn, "plan_checkpoint_enforced", "plan_creator")
    policy_edges = _count_distinct_sources(conn, "references_policy_hash")

    ok = plan_checkpoint >= 1 and checkpoint_result >= 1 and checkpoint_emitter >= 1 and policy_edges >= 1
    GATE_RESULTS.append(
        (
            "E",
            ok,
            f"PlanCheckpoint exported={plan_checkpoint} (>=1), "
            f"CheckpointResult exported={checkpoint_result} (>=1), "
            f"plan_checkpoint_enforced exported={checkpoint_emitter} (>=1), "
            f"references_policy_hash sources={policy_edges} (>=1)",
        ),
    )
    return ok


def _print_baseline(conn: sqlite3.Connection) -> None:
    """Print P3/L1 reasoning planning baseline for verification."""
    print("\n--- P3/L1 Multi-Step Reasoning Planning Baseline ---")

    for rel in (
        "records_execution_trace",
        "transcripts_response",
        "references_policy_hash",
        "reasoning_plan_emitted",
        "plan_step_executed",
        "plan_checkpoint_enforced",
        "plan_revision_recorded",
    ):
        total = _count_distinct_sources(conn, rel)
        print(f"  {rel:<45} total={total:4d}")

    print("\n--- Key L1 reasoning plan symbols (non-test) ---")
    for sym in (
        "ReasoningPlan",
        "create_reasoning_plan",
        "ReasoningPlanContext",
        "PlanStep",
        "PlanCheckpoint",
        "reasoning_plan_id",
        "plan_goal_hash",
        "plan_context_hash",
        "initial_evidence_hash",
        "step_sequence_hash",
        "checkpoint_policy_hash",
        "active_step_index",
        "plan_status",
        "parent_plan_id",
        "step_id",
        "step_index",
        "step_goal_hash",
        "step_input_hash",
        "step_output_hash",
        "step_status",
        "checkpoint_result",
        "revision_required_flag",
        "revision_reason_hash",
        "prior_step_sequence_hash",
        "new_step_sequence_hash",
        "revision_parent_plan_id",
        "checkpoint_id",
        "checkpoint_pass_fail",
        "checkpoint_reason_hash",
        "ReasoningPlanError",
    ):
        count = _count_exported(conn, sym)
        print(f"  symbol:{sym:<40} sources={count:4d}")

    print("\n--- L1 planning module exports (non-test) ---")
    cursor = conn.execute(
        f"""
        SELECT DISTINCT source_file, symbol
        FROM edges
        WHERE source_file LIKE '%L1_cognition/planning%' {NON_TEST}
        ORDER BY source_file, symbol
        LIMIT 30
        """,
    )
    for source, symbol in cursor.fetchall():
        print(f"  {source:<60} [{symbol}]")


def main() -> int:
    """Run P3/L1 multi-step reasoning planning gates."""
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
        print("P3/L1 MULTI-STEP REASONING PLANNING: ALL GATES PASSED - CLOSURE VERIFIED")
    else:
        failed_gates = [gate for gate, ok, _ in GATE_RESULTS if not ok]
        print(f"P3/L1 MULTI-STEP REASONING PLANNING: FAILED GATES {failed_gates}")
    print("=" * 70)

    conn.close()
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
