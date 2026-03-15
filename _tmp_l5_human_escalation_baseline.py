"""P3/L5 Human Safety Escalation baseline audit."""

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
L5_FILTER = f"AND source_file LIKE '%L5_safety%' {FILTERS}"

print(f"DB: {db}\n")

print("=== Human safety escalation baseline (non-test) ===")
for rel in (
    "requires_human_review",
    "escalates_to_human",
    "validated_by_safety_plane",
    "human_escalation_emitted",
    "escalation_recorded",
    "reviewer_outcome_recorded",
    "escalation_blocked",
    "override_executed",
):
    total = _count_distinct_sources(conn, rel)
    l5 = _count_distinct_sources(conn, rel, L5_FILTER)
    print(f"  {rel:<45} total={total:4d}  L5={l5:4d}")

print("\n=== Key L5 human escalation symbols (non-test) ===")
for sym in (
    "HumanEscalationRecord",
    "escalate_for_human_review",
    "SafetyContext",
    "EscalationTriggerType",
    "ReviewerOutcome",
    "escalation_id",
    "run_id",
    "trace_id",
    "policy_hash",
    "action_class",
    "escalation_reason_hash",
    "escalation_trigger_type",
    "reviewer_queue_id",
    "reviewer_id",
    "reviewer_outcome",
    "override_flag",
    "final_decision_hash",
    "APPROVED",
    "DENIED",
    "MODIFIED",
    "ESCALATE_FURTHER",
    "DEFERRED",
    "HumanEscalationError",
):
    count = _count_exported(conn, sym)
    print(f"  symbol:{sym:<40} sources={count:4d}")

print("\n=== L5 safety source files (non-test) ===")
c.execute(
    f"SELECT DISTINCT source_file FROM edges WHERE source_file LIKE '%L5_safety%' {FILTERS} ORDER BY source_file LIMIT 30"
)
for (f,) in c.fetchall():
    print(" ", f)

print("\n=== requires_human_review edges (non-test, up to 15) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='requires_human_review' {FILTERS} LIMIT 15"
)
for r in c.fetchall():
    print(" ", r)

print("\n=== escalates_to_human edges (non-test, up to 15) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='escalates_to_human' {FILTERS} LIMIT 15"
)
for r in c.fetchall():
    print(" ", r)

print("\n=== validated_by_safety_plane edges (non-test, up to 15) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='validated_by_safety_plane' {FILTERS} LIMIT 15"
)
for r in c.fetchall():
    print(" ", r)

conn.close()
