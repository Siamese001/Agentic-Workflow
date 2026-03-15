"""P3/L3 Workflow Visualization baseline audit."""

import glob
import sqlite3


def _count_distinct_sources(conn, relation_type, filter_clause=""):
    """Count distinct source files for a relation type."""
    filters = "AND source_file NOT LIKE '%test%' AND source_file NOT LIKE '%tests%' AND source_file NOT LIKE '%spec%' AND source_file NOT LIKE '%fixture%' AND source_file NOT LIKE '%mock%'"
    if filter_clause:
        filters = filter_clause
    cursor = conn.execute(
        f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type=? {filters}",
        (relation_type,),
    )
    return cursor.fetchone()[0]


def _count_exported(conn, symbol, module_hint=""):
    """Count distinct source files exporting a symbol."""
    if module_hint:
        cursor = conn.execute(
            """
            SELECT COUNT(DISTINCT source_file)
            FROM edges
            WHERE symbol LIKE ? AND source_file LIKE ? AND source_file NOT LIKE '%test%' AND source_file NOT LIKE '%tests%' AND source_file NOT LIKE '%spec%' AND source_file NOT LIKE '%fixture%' AND source_file NOT LIKE '%mock%'
            """,
            (f"%{symbol}%", f"%{module_hint}%"),
        )
    else:
        cursor = conn.execute(
            """
            SELECT COUNT(DISTINCT source_file)
            FROM edges
            WHERE symbol LIKE ? AND source_file NOT LIKE '%test%' AND source_file NOT LIKE '%tests%' AND source_file NOT LIKE '%spec%' AND source_file NOT LIKE '%fixture%' AND source_file NOT LIKE '%mock%'
            """,
            (f"%{symbol}%",),
        )
    return cursor.fetchone()[0]


db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
conn = sqlite3.connect(db)
c = conn.cursor()

FILTERS = "AND source_file NOT LIKE '%test%' AND source_file NOT LIKE '%tests%' AND source_file NOT LIKE '%spec%' AND source_file NOT LIKE '%fixture%' AND source_file NOT LIKE '%mock%'"
L3_FILTER = f"AND source_file LIKE '%L3_orchestration%' {FILTERS}"

print(f"DB: {db}\n")

print("=== Workflow visualization baseline (non-test) ===")
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
    l3 = _count_distinct_sources(conn, rel, L3_FILTER)
    print(f"  {rel:<45} total={total:4d}  L3={l3:4d}")

print("\n=== Key L3 workflow visualization symbols (non-test) ===")
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

print("\n=== L3 orchestration source files (non-test) ===")
c.execute(
    f"SELECT DISTINCT source_file FROM edges WHERE source_file LIKE '%L3_orchestration%' {FILTERS} ORDER BY source_file LIMIT 30"
)
for (f,) in c.fetchall():
    print(" ", f)

print("\n=== agent_executes_agent edges (non-test, up to 15) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='agent_executes_agent' {FILTERS} LIMIT 15"
)
for r in c.fetchall():
    print(" ", r)

print("\n=== observes_runtime_state edges (non-test, up to 15) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='observes_runtime_state' {FILTERS} LIMIT 15"
)
for r in c.fetchall():
    print(" ", r)

conn.close()
