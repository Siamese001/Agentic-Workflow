"""P3/L6 Observability Dashboard baseline audit."""

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
L6_FILTER = f"AND source_file LIKE '%L6%' {FILTERS}"

print(f"DB: {db}\n")

print("=== Observability dashboard baseline (non-test) ===")
for rel in (
    "records_execution_trace",
    "invokes_eval",
    "escalates_to_human",
    "requires_human_review",
    "routes_path",
    "routes_through",
    "dashboard_aggregated",
    "health_computed",
    "metrics_collected",
    "snapshot_persisted",
    "query_exposed",
):
    total = _count_distinct_sources(conn, rel)
    l6 = _count_distinct_sources(conn, rel, L6_FILTER)
    print(f"  {rel:<45} total={total:4d}  L6={l6:4d}")

print("\n=== Key L6 dashboard symbols (non-test) ===")
for sym in (
    "DashboardAggregate",
    "aggregate_runtime_observability",
    "DashboardSnapshot",
    "HealthFlag",
    "TelemetryWindow",
    "DashboardPolicy",
    "dashboard_snapshot_id",
    "snapshot_tick",
    "active_run_count",
    "routing_throughput",
    "reasoning_throughput",
    "execution_success_rate",
    "execution_failure_rate",
    "policy_block_rate",
    "human_escalation_rate",
    "queue_depth_summary",
    "median_latency_by_stage",
    "p95_latency_by_stage",
    "degraded_component_flags",
    "HEALTHY",
    "DEGRADED",
    "CRITICAL",
    "UNKNOWN",
):
    count = _count_exported(conn, sym)
    print(f"  symbol:{sym:<40} sources={count:4d}")

print("\n=== L6 source files (non-test) ===")
c.execute(
    f"SELECT DISTINCT source_file FROM edges WHERE source_file LIKE '%L6%' {FILTERS} ORDER BY source_file LIMIT 30"
)
for (f,) in c.fetchall():
    print(" ", f)

print("\n=== records_execution_trace edges (non-test, up to 15) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='records_execution_trace' {FILTERS} LIMIT 15"
)
for r in c.fetchall():
    print(" ", r)

print("\n=== routes_through edges (non-test, up to 15) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='routes_through' {FILTERS} LIMIT 15"
)
for r in c.fetchall():
    print(" ", r)

print("\n=== escalates_to_human edges (non-test, up to 15) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='escalates_to_human' {FILTERS} LIMIT 15"
)
for r in c.fetchall():
    print(" ", r)

conn.close()
