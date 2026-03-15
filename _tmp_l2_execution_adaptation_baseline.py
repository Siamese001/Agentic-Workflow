"""P4/L2 Execution Adaptation baseline audit."""

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
L2_FILTER = f"AND source_file LIKE '%L2%' {FILTERS}"

print(f"DB: {db}\n")

print("=== Execution adaptation baseline (non-test) ===")
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
    l2 = _count_distinct_sources(conn, rel, L2_FILTER)
    print(f"  {rel:<45} total={total:4d}  L2={l2:4d}")

print("\n=== Key L2 execution adaptation symbols (non-test) ===")
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

print("\n=== L2 source files (non-test) ===")
c.execute(
    f"SELECT DISTINCT source_file FROM edges WHERE source_file LIKE '%L2%' {FILTERS} ORDER BY source_file LIMIT 30"
)
for (f,) in c.fetchall():
    print(" ", f)

print("\n=== records_execution_trace edges (non-test, up to 15) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='records_execution_trace' {FILTERS} LIMIT 15"
)
for r in c.fetchall():
    print(" ", r)

print("\n=== invokes_dynamic edges (non-test, up to 15) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='invokes_dynamic' {FILTERS} LIMIT 15"
)
for r in c.fetchall():
    print(" ", r)

conn.close()
