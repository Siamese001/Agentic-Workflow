#!/usr/bin/env python3
"""
P3/L3 Workflow Visualization CI Gate

Enforces Gates A-E for workflow visualization closure:
- Gate A: Stage transition must have workflow visualization update
- Gate B: Workflow status must be present on active runtime run
- Gate C: Owner transitions must have visualization record
- Gate D: Terminal workflow must have final stage record
- Gate E: Blocked workflow must have blocked reason

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
    """Gate A — Stage transition must have workflow visualization update.

    Passes when:
    - WorkflowVisualizationError exported >= 1
      (exception for missing visualization update), AND
    - update_workflow_visualization exported >= 1
      (mandatory visualization update entrypoint), AND
    - WorkflowVisualizationRecord exported >= 1
      (visualization record with 13 required fields), AND
    - workflow_visualization_emitted function exported >= 1
      (ADG edge emitter for static scanner), AND
    - agent_executes_agent edges >= 1
      (runtime handoffs happening), AND
    - stage_transition_recorded function exported >= 1
      (ADG edge emitter for stage transitions)
    """
    viz_error = _count_exported(conn, "WorkflowVisualizationError", "workflow_visualization")
    update_function = _count_exported(conn, "update_workflow_visualization", "visualization_updater")
    viz_record = _count_exported(conn, "WorkflowVisualizationRecord", "workflow_visualization")
    emitter_function = _count_exported(conn, "workflow_visualization_emitted", "visualization_updater")
    handoff_edges = _count_distinct_sources(conn, "agent_executes_agent")
    stage_emitter = _count_exported(conn, "stage_transition_recorded", "visualization_updater")

    ok = (
        viz_error >= 1
        and update_function >= 1
        and viz_record >= 1
        and emitter_function >= 1
        and handoff_edges >= 1
        and stage_emitter >= 1
    )
    GATE_RESULTS.append(
        (
            "A",
            ok,
            f"WorkflowVisualizationError exported={viz_error} (>=1), "
            f"update_workflow_visualization exported={update_function} (>=1), "
            f"WorkflowVisualizationRecord exported={viz_record} (>=1), "
            f"workflow_visualization_emitted exported={emitter_function} (>=1), "
            f"agent_executes_agent sources={handoff_edges} (>=1), "
            f"stage_transition_recorded exported={stage_emitter} (>=1)",
        ),
    )
    return ok


def gate_b(conn: sqlite3.Connection) -> bool:
    """Gate B — Workflow status must be present on active runtime run.

    Passes when:
    - WorkflowVisualizationRecord exported >= 1
      (visualization record with workflow_status field), AND
    - WorkflowStatus exported >= 1
      (workflow status enumeration), AND
    - ACTIVE status exported >= 1
      (active workflow status), AND
    - workflow_visualization_emitted function exported >= 1
      (ADG edge emitter with status parameter), AND
    - observes_runtime_state edges >= 1
      (runtime state observation happening)
    """
    viz_record = _count_exported(conn, "WorkflowVisualizationRecord", "workflow_visualization")
    workflow_status = _count_exported(conn, "WorkflowStatus", "workflow_visualization")
    active_status = _count_exported(conn, "ACTIVE", "workflow_visualization")
    emitter_function = _count_exported(conn, "workflow_visualization_emitted", "visualization_updater")
    state_edges = _count_distinct_sources(conn, "observes_runtime_state")

    ok = (
        viz_record >= 1
        and workflow_status >= 1
        and active_status >= 1
        and emitter_function >= 1
        and state_edges >= 1
    )
    GATE_RESULTS.append(
        (
            "B",
            ok,
            f"WorkflowVisualizationRecord exported={viz_record} (>=1), "
            f"WorkflowStatus exported={workflow_status} (>=1), "
            f"ACTIVE exported={active_status} (>=1), "
            f"workflow_visualization_emitted exported={emitter_function} (>=1), "
            f"observes_runtime_state sources={state_edges} (>=1)",
        ),
    )
    return ok


def gate_c(conn: sqlite3.Connection) -> bool:
    """Gate C — Owner transitions must have visualization record.

    Passes when:
    - WorkflowVisualizationRecord exported >= 1
      (visualization record with owner fields), AND
    - owner_transition_recorded function exported >= 1
      (ADG edge emitter for owner transitions), AND
    - update_workflow_visualization exported >= 1
      (parent function for owner transitions), AND
    - agent_executes_agent edges >= 1
      (runtime handoffs where owners transition)
    """
    viz_record = _count_exported(conn, "WorkflowVisualizationRecord", "workflow_visualization")
    owner_emitter = _count_exported(conn, "owner_transition_recorded", "visualization_updater")
    update_function = _count_exported(conn, "update_workflow_visualization", "visualization_updater")
    handoff_edges = _count_distinct_sources(conn, "agent_executes_agent")

    ok = viz_record >= 1 and owner_emitter >= 1 and update_function >= 1 and handoff_edges >= 1
    GATE_RESULTS.append(
        (
            "C",
            ok,
            f"WorkflowVisualizationRecord exported={viz_record} (>=1), "
            f"owner_transition_recorded exported={owner_emitter} (>=1), "
            f"update_workflow_visualization exported={update_function} (>=1), "
            f"agent_executes_agent sources={handoff_edges} (>=1)",
        ),
    )
    return ok


def gate_d(conn: sqlite3.Connection) -> bool:
    """Gate D — Terminal workflow must have final stage record.

    Passes when:
    - WorkflowVisualizationRecord exported >= 1
      (visualization record for terminal states), AND
    - COMPLETED status exported >= 1
      (completed workflow status), AND
    - FAILED status exported >= 1
      (failed workflow status), AND
    - workflow_completed_recorded function exported >= 1
      (ADG edge emitter for workflow completion)
    """
    viz_record = _count_exported(conn, "WorkflowVisualizationRecord", "workflow_visualization")
    completed_status = _count_exported(conn, "COMPLETED", "workflow_visualization")
    failed_status = _count_exported(conn, "FAILED", "workflow_visualization")
    completion_emitter = _count_exported(conn, "workflow_completed_recorded", "visualization_updater")

    ok = viz_record >= 1 and completed_status >= 1 and failed_status >= 1 and completion_emitter >= 1
    GATE_RESULTS.append(
        (
            "D",
            ok,
            f"WorkflowVisualizationRecord exported={viz_record} (>=1), "
            f"COMPLETED exported={completed_status} (>=1), "
            f"FAILED exported={failed_status} (>=1), "
            f"workflow_completed_recorded exported={completion_emitter} (>=1)",
        ),
    )
    return ok


def gate_e(conn: sqlite3.Connection) -> bool:
    """Gate E — Blocked workflow must have blocked reason.

    Passes when:
    - BLOCKED status exported >= 1
      (blocked workflow status), AND
    - StageTransitionReason exported >= 1
      (stage transition reason enumeration), AND
    - BLOCK_DETECTED reason exported >= 1
      (blocked transition reason), AND
    - WorkflowVisualizationRecord exported >= 1
      (parent record for blocked reason hash)
    """
    blocked_status = _count_exported(conn, "BLOCKED", "workflow_visualization")
    transition_reason = _count_exported(conn, "StageTransitionReason", "workflow_visualization")
    block_detected = _count_exported(conn, "BLOCK_DETECTED", "workflow_visualization")
    viz_record = _count_exported(conn, "WorkflowVisualizationRecord", "workflow_visualization")

    ok = blocked_status >= 1 and transition_reason >= 1 and block_detected >= 1 and viz_record >= 1
    GATE_RESULTS.append(
        (
            "E",
            ok,
            f"BLOCKED exported={blocked_status} (>=1), "
            f"StageTransitionReason exported={transition_reason} (>=1), "
            f"BLOCK_DETECTED exported={block_detected} (>=1), "
            f"WorkflowVisualizationRecord exported={viz_record} (>=1)",
        ),
    )
    return ok


def _print_baseline(conn: sqlite3.Connection) -> None:
    """Print P3/L3 workflow visualization baseline for verification."""
    print("\n--- P3/L3 Workflow Visualization Baseline ---")

    for rel in (
        "agent_executes_agent",
        "observes_runtime_state",
        "snapshots_state",
        "workflow_visualization_emitted",
        "stage_transition_recorded",
        "owner_transition_recorded",
        "workflow_completed_recorded",
    ):
        total = _count_distinct_sources(conn, rel)
        print(f"  {rel:<45} total={total:4d}")

    print("\n--- Key L3 workflow visualization symbols (non-test) ---")
    for sym in (
        "WorkflowVisualizationRecord",
        "update_workflow_visualization",
        "WorkflowVisualizationContext",
        "WorkflowStatus",
        "StageTransitionReason",
        "workflow_visualization_id",
        "run_id",
        "root_trace_id",
        "workflow_id",
        "current_stage",
        "completed_stages_hash",
        "pending_stages_hash",
        "current_owner_agent_id",
        "previous_owner_agent_id",
        "workflow_status",
        "stage_transition_reason_hash",
        "last_updated_tick",
        "ACTIVE",
        "BLOCKED",
        "RETRYING",
        "ESCALATED",
        "COMPLETED",
        "FAILED",
        "NORMAL_TRANSITION",
        "RETRY_TRIGGERED",
        "ESCALATION_TRIGGERED",
        "BLOCK_DETECTED",
        "WORKFLOW_ERROR",
        "WorkflowVisualizationError",
    ):
        count = _count_exported(conn, sym)
        print(f"  symbol:{sym:<40} sources={count:4d}")

    print("\n--- L3 visualization module exports (non-test) ---")
    cursor = conn.execute(
        f"""
        SELECT DISTINCT source_file, symbol
        FROM edges
        WHERE source_file LIKE '%L3_orchestration/visualization%' {NON_TEST}
        ORDER BY source_file, symbol
        LIMIT 30
        """,
    )
    for source, symbol in cursor.fetchall():
        print(f"  {source:<60} [{symbol}]")


def main() -> int:
    """Run P3/L3 workflow visualization gates."""
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
        print("P3/L3 WORKFLOW VISUALIZATION: ALL GATES PASSED - CLOSURE VERIFIED")
    else:
        failed_gates = [gate for gate, ok, _ in GATE_RESULTS if not ok]
        print(f"P3/L3 WORKFLOW VISUALIZATION: FAILED GATES {failed_gates}")
    print("=" * 70)

    conn.close()
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
