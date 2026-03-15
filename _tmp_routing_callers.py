#!/usr/bin/env python3
"""Analyse the 12 uncovered routing sites - what exactly do they route through?"""

import os
import sqlite3

adg_dir = r"artifacts\adg"
sqls = sorted([f for f in os.listdir(adg_dir) if f.endswith(".sqlite")], reverse=True)
conn = sqlite3.connect(os.path.join(adg_dir, sqls[0]))
c = conn.cursor()

targets = [
    "agentic_core/L2_execution/enforcement/SovereignLLMGateway.py",
    "apps_lic/engines/lic_spine_adapter.py",
    "apps_rg/engines/rg_spine_adapter.py",
    "ops_scripts/dev_tools/l0_scripts/sovereign_mission_control_util.py",
]

print("=== routing edge details for key uncovered files ===")
for f in targets:
    c.execute(
        """
        SELECT e.relation_type, e.line_no, e.symbol
        FROM edges e JOIN nodes n ON e.src_id=n.id
        WHERE n.resolved_path=? AND e.relation_type IN (
            'routes_path','routes_through','calls','imports')
        AND e.relation_type != 'imports'
        ORDER BY e.line_no
    """,
        (f,),
    )
    rows = c.fetchall()
    print(f"\n  {f.split('/')[-1]}:")
    for r in rows:
        print(f"    line {r[1]:5}  {r[0]:25}  {r[2]}")

# Check if any of the 12 uncovered sites import DeterministicRoutingGateway or RoutePolicyGovernor
print("\n=== Do uncovered routing sites import the gateway/governor? ===")
c.execute("""
    SELECT DISTINCT n.resolved_path
    FROM edges e JOIN nodes n ON e.src_id=n.id
    WHERE e.relation_type='imports'
    AND (e.symbol LIKE '%DeterministicRoutingGateway%'
         OR e.symbol LIKE '%RoutePolicyGovernor%'
         OR e.symbol LIKE '%get_routing_gateway%'
         OR e.symbol LIKE '%get_route_policy_governor%')
""")
wired = [r[0] for r in c.fetchall()]
print(f"  Files importing gateway/governor: {len(wired)}")
for w in wired:
    print(f"    {w}")

# Check what DeterministicRoutingGateway / RoutePolicyGovernor are imported by
print("\n=== Who imports DeterministicRoutingGateway? ===")
c.execute("""
    SELECT DISTINCT n.resolved_path, n.layer
    FROM edges e JOIN nodes n ON e.src_id=n.id
    WHERE e.relation_type='imports'
    AND e.symbol LIKE '%deterministic_routing_gateway%'
    ORDER BY n.layer, n.resolved_path
""")
for r in c.fetchall():
    print(f"  [{r[1]:8}] {r[0]}")

# Check execution_gateway - it has replay coverage
print("\n=== execution_gateway.py - what does it do? ===")
c.execute("""
    SELECT e.relation_type, e.line_no, e.symbol
    FROM edges e JOIN nodes n ON e.src_id=n.id
    WHERE n.resolved_path='agentic_core/L0_routing/enforcement/execution_gateway.py'
    AND e.relation_type IN ('emits_replay_key','emits_determinism_digest','patches_time',
        'calls','routes_path','routes_through','imports')
    AND e.relation_type != 'imports'
    ORDER BY e.line_no
""")
rows = c.fetchall()
print("  execution_gateway.py edges:")
for r in rows:
    print(f"    line {r[1]:5}  {r[0]:30}  {r[2]}")

# Count total routing decisions needed to produce proofs
print("\n=== Full picture: routing vs proof ===")
c.execute("SELECT COUNT(*) FROM edges WHERE relation_type IN ('routes_path','routes_through')")
total_route = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM edges WHERE relation_type='proposal_commits_routing'")
total_commit = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM edges WHERE relation_type IN ('emits_replay_key','emits_determinism_digest')")
total_proof = c.fetchone()[0]
c.execute("""SELECT COUNT(*) FROM edges WHERE relation_type IN ('emits_replay_key','emits_determinism_digest')
    AND src_id IN (SELECT id FROM nodes WHERE layer NOT IN ('L_TEST'))""")
prod_proof = c.fetchone()[0]
print(f"  routes_path + routes_through: {total_route}")
print(f"  proposal_commits_routing:     {total_commit}")
print(f"  replay proof edges (total):   {total_proof}")
print(f"  replay proof edges (prod):    {prod_proof}")
print(
    f"  proof coverage: {prod_proof}/{total_route} = {prod_proof / total_route * 100:.1f}% of routing sites"
)

conn.close()
