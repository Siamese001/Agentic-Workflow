"""P3/L1 Multi-Step Reasoning Planning baseline audit."""

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


db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
conn = sqlite3.connect(db)
c = conn.cursor()

FILTERS = "AND source_file NOT LIKE '%test%' AND source_file NOT LIKE '%tests%' AND source_file NOT LIKE '%spec%' AND source_file NOT LIKE '%fixture%' AND source_file NOT LIKE '%mock%'"
L1_FILTER = f"AND source_file LIKE '%L1_cognition%' {FILTERS}"

print(f"DB: {db}\n")

print("=== Reasoning plan baseline (non-test) ===")
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
    l1 = _count_distinct_sources(conn, rel, L1_FILTER)
    print(f"  {rel:<45} total={total:4d}  L1={l1:4d}")

print("\n=== Key L1 reasoning plan symbols (non-test) ===")
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
    c.execute(f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE symbol LIKE ? {FILTERS}", (f"%{sym}%",))
    n = c.fetchone()[0]
    print(f"  symbol:{sym:<40} sources={n:4d}")

print("\n=== L1 reasoning source files (non-test) ===")
c.execute(
    f"SELECT DISTINCT source_file FROM edges WHERE source_file LIKE '%L1_cognition%' {FILTERS} ORDER BY source_file LIMIT 30"
)
for (f,) in c.fetchall():
    print(" ", f)

print("\n=== records_execution_trace edges (non-test, up to 15) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='records_execution_trace' {FILTERS} LIMIT 15"
)
for r in c.fetchall():
    print(" ", r)

print("\n=== transcripts_response edges (non-test, up to 15) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='transcripts_response' {FILTERS} LIMIT 15"
)
for r in c.fetchall():
    print(" ", r)

conn.close()
