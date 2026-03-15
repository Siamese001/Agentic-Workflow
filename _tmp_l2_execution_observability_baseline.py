"""P3/L2 Execution Observability baseline audit."""

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
L2_FILTER = f"AND source_file LIKE '%L2_execution%' {FILTERS}"

print(f"DB: {db}\n")

print("=== Execution observability baseline (non-test) ===")
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
    l2 = _count_distinct_sources(conn, rel, L2_FILTER)
    print(f"  {rel:<45} total={total:4d}  L2={l2:4d}")

print("\n=== Key L2 execution observability symbols (non-test) ===")
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

print("\n=== L2 execution source files (non-test) ===")
c.execute(
    f"SELECT DISTINCT source_file FROM edges WHERE source_file LIKE '%L2_execution%' {FILTERS} ORDER BY source_file LIMIT 30"
)
for (f,) in c.fetchall():
    print(" ", f)

print("\n=== records_execution_trace edges (non-test, up to 15) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='records_execution_trace' {FILTERS} LIMIT 15"
)
for r in c.fetchall():
    print(" ", r)

print("\n=== signs_execution_trace edges (non-test, up to 15) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='signs_execution_trace' {FILTERS} LIMIT 15"
)
for r in c.fetchall():
    print(" ", r)

conn.close()
