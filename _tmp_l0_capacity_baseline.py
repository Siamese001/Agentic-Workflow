"""P3/L0 Routing Capacity Governance baseline audit."""

import glob
import sqlite3

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
conn = sqlite3.connect(db)
c = conn.cursor()

FILTERS = "AND source_file NOT LIKE '%test%' AND source_file NOT LIKE '%tests%' AND source_file NOT LIKE '%spec%' AND source_file NOT LIKE '%fixture%' AND source_file NOT LIKE '%mock%'"
L0_FILTER = f"AND source_file LIKE '%L0_routing%' {FILTERS}"

print(f"DB: {db}\n")

print("=== Routing capacity baseline (non-test) ===")
for rel in (
    "routes_path",
    "routes_through",
    "proposal_commits_routing",
    "records_execution_trace",
    "capacity_snapshot_emitted",
    "capacity_aware_routing",
    "route_chosen_with_capacity",
):
    c.execute(f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type=? {FILTERS}", (rel,))
    total = c.fetchone()[0]
    c.execute(f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type=? {L0_FILTER}", (rel,))
    l0 = c.fetchone()[0]
    print(f"  {rel:<45} total={total:4d}  L0={l0:4d}")

print("\n=== Key capacity symbols (non-test) ===")
for sym in (
    "CapacitySnapshot",
    "choose_route_with_capacity",
    "RoutingCapacityContext",
    "CapacityDecisionReason",
    "capacity_snapshot_id",
    "candidate_route_count",
    "candidate_capacity_hash",
    "chosen_route_hash",
    "queue_depth_by_candidate",
    "in_flight_work_by_candidate",
    "recent_latency_by_candidate",
    "failure_rate_by_candidate",
    "degraded_route_flags",
    "capacity_decision_reason_hash",
    "HEALTHY",
    "DEGRADED",
    "SATURATED",
    "UNAVAILABLE",
    "RoutingCapacityError",
):
    c.execute(f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE symbol LIKE ? {FILTERS}", (f"%{sym}%",))
    n = c.fetchone()[0]
    print(f"  symbol:{sym:<40} sources={n:4d}")

print("\n=== L0 routing source files (non-test) ===")
c.execute(
    f"SELECT DISTINCT source_file FROM edges WHERE source_file LIKE '%L0_routing%' {FILTERS} ORDER BY source_file LIMIT 30"
)
for (f,) in c.fetchall():
    print(" ", f)

print("\n=== routes_path edges (non-test, up to 15) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='routes_path' {FILTERS} LIMIT 15"
)
for r in c.fetchall():
    print(" ", r)

print("\n=== proposal_commits_routing edges (non-test, up to 15) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='proposal_commits_routing' {FILTERS} LIMIT 15"
)
for r in c.fetchall():
    print(" ", r)

conn.close()
