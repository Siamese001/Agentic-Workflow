"""P4/L0 Routing Optimization baseline audit."""

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
L0_FILTER = f"AND source_file LIKE '%L0%' {FILTERS}"

print(f"DB: {db}\n")

print("=== Routing optimization baseline (non-test) ===")
for rel in (
    "routes_path",
    "routes_through",
    "records_execution_trace",
    "optimizes_routing",
    "routing_policy_adapted",
    "routing_optimization_persisted",
    "route_candidate_ranked",
    "routing_governance_approved",
    "historical_outcomes_analyzed",
):
    total = _count_distinct_sources(conn, rel)
    l0 = _count_distinct_sources(conn, rel, L0_FILTER)
    print(f"  {rel:<45} total={total:4d}  L0={l0:4d}")

print("\n=== Key L0 routing optimization symbols (non-test) ===")
for sym in (
    "RoutingOptimizationRecord",
    "optimize_routing_policy",
    "RoutingOptimizationError",
    "routing_optimization_id",
    "optimization_window_start",
    "optimization_window_end",
    "route_candidate_hash",
    "historical_success_rate",
    "historical_failure_rate",
    "median_latency_ms",
    "p95_latency_ms",
    "cost_estimate",
    "recommended_route_rank",
    "optimization_reason_hash",
):
    count = _count_exported(conn, sym)
    print(f"  symbol:{sym:<40} sources={count:4d}")

print("\n=== L0 source files (non-test) ===")
c.execute(
    f"SELECT DISTINCT source_file FROM edges WHERE source_file LIKE '%L0%' {FILTERS} ORDER BY source_file LIMIT 30"
)
for (f,) in c.fetchall():
    print(" ", f)

print("\n=== routes_path edges (non-test, up to 15) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='routes_path' {FILTERS} LIMIT 15"
)
for r in c.fetchall():
    print(" ", r)

print("\n=== routes_through edges (non-test, up to 15) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='routes_through' {FILTERS} LIMIT 15"
)
for r in c.fetchall():
    print(" ", r)

print("\n=== records_execution_trace edges (non-test, up to 15) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='records_execution_trace' {FILTERS} LIMIT 15"
)
for r in c.fetchall():
    print(" ", r)

conn.close()
