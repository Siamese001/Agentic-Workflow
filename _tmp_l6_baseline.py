"""P2/L6 Performance Observability baseline audit."""

import glob
import sqlite3

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
conn = sqlite3.connect(db)
c = conn.cursor()

FILTERS = "AND source_file NOT LIKE '%test%' AND source_file NOT LIKE '%tests%' AND source_file NOT LIKE '%spec%' AND source_file NOT LIKE '%fixture%' AND source_file NOT LIKE '%mock%'"
L6_FILTER = f"AND source_file LIKE '%L6%' {FILTERS}"

print(f"DB: {db}\n")

print("=== Runtime edge counts (non-test) ===")
for rel in (
    "records_execution_trace",
    "routes_path",
    "routes_through",
    "agent_executes_agent",
    "writes_through",
    "performance_record_emitted",
    "stage_latency_measured",
):
    c.execute(f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type=? {FILTERS}", (rel,))
    total = c.fetchone()[0]
    c.execute(f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type=? {L6_FILTER}", (rel,))
    l6 = c.fetchone()[0]
    print(f"  {rel:<45} total={total:4d}  L6={l6:4d}")

print("\n=== L6 key symbols (non-test) ===")
for sym in (
    "PerformanceRecord",
    "record_stage_performance",
    "PerformanceContext",
    "StageOwner",
    "performance_record_id",
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
    "PerformanceMissingError",
    "BudgetViolationError",
):
    c.execute(f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE symbol LIKE ? {FILTERS}", (f"%{sym}%",))
    n = c.fetchone()[0]
    print(f"  symbol:{sym:<40} sources={n:4d}")

print("\n=== L6 non-test source files ===")
c.execute(
    f"SELECT DISTINCT source_file FROM edges WHERE source_file LIKE '%L6%' {FILTERS} ORDER BY source_file LIMIT 60"
)
for (f,) in c.fetchall():
    print(" ", f)

print("\n=== records_execution_trace edges (non-test, up to 20) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='records_execution_trace' {FILTERS} LIMIT 20"
)
for r in c.fetchall():
    print(" ", r)

print("\n=== routes_path edges (non-test, up to 20) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='routes_path' {FILTERS} LIMIT 20"
)
for r in c.fetchall():
    print(" ", r)

print("\n=== agent_executes_agent edges (non-test, up to 20) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='agent_executes_agent' {FILTERS} LIMIT 20"
)
for r in c.fetchall():
    print(" ", r)

conn.close()
