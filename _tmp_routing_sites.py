#!/usr/bin/env python3
"""Find all routing decision sites and their replay coverage."""

import os
import sqlite3

adg_dir = r"artifacts\adg"
sqls = sorted([f for f in os.listdir(adg_dir) if f.endswith(".sqlite")], reverse=True)
db = os.path.join(adg_dir, sqls[0])
print(f"DB: {sqls[0]}")
conn = sqlite3.connect(db)
c = conn.cursor()

# 1. All routing decision sites (routes_path + routes_through) by file, layer
print("\n=== Routing decision sites by file (routes_path + routes_through) ===")
c.execute("""
    SELECT n.resolved_path, n.layer, e.relation_type, COUNT(*) as cnt
    FROM edges e JOIN nodes n ON e.src_id = n.id
    WHERE e.relation_type IN ('routes_path','routes_through')
    AND n.layer NOT IN ('L_TEST')
    GROUP BY n.resolved_path, n.layer, e.relation_type
    ORDER BY cnt DESC, n.layer
""")
rows = c.fetchall()
for r in rows:
    print(f"  [{r[1]:8}] {r[2]:20} cnt={r[3]:3}  {r[0]}")

# 2. Which routing sites also have replay artifacts?
print("\n=== Routing sites WITH replay coverage (emits_replay_key or emits_determinism_digest) ===")
c.execute("""
    SELECT DISTINCT n.resolved_path, n.layer
    FROM edges e JOIN nodes n ON e.src_id = n.id
    WHERE e.relation_type IN ('emits_replay_key','emits_determinism_digest','patches_time')
    AND n.layer NOT IN ('L_TEST')
    ORDER BY n.layer, n.resolved_path
""")
covered = c.fetchall()
for r in covered:
    print(f"  [{r[1]:8}] {r[0]}")

# 3. Routing sites WITHOUT replay coverage
print("\n=== Routing sites WITHOUT replay coverage ===")
c.execute("""
    SELECT DISTINCT n.resolved_path, n.layer
    FROM edges e JOIN nodes n ON e.src_id = n.id
    WHERE e.relation_type IN ('routes_path','routes_through')
    AND n.layer NOT IN ('L_TEST')
    AND n.resolved_path NOT IN (
        SELECT DISTINCT n2.resolved_path FROM edges e2
        JOIN nodes n2 ON e2.src_id = n2.id
        WHERE e2.relation_type IN ('emits_replay_key','emits_determinism_digest','patches_time')
    )
    ORDER BY n.layer, n.resolved_path
""")
uncovered = c.fetchall()
for r in uncovered:
    print(f"  [{r[1]:8}] {r[0]}")

print(f"\nSummary: {len(covered)} routing sites with replay, {len(uncovered)} without")

# 4. L0-specific routing sites
print("\n=== L0 routing decision sites ===")
c.execute("""
    SELECT n.resolved_path, e.relation_type, e.line_no, e.symbol, COUNT(*) as cnt
    FROM edges e JOIN nodes n ON e.src_id = n.id
    WHERE e.relation_type IN ('routes_path','routes_through','proposal_commits_routing')
    AND n.layer = 'L0'
    GROUP BY n.resolved_path, e.relation_type, e.line_no, e.symbol
    ORDER BY n.resolved_path, e.line_no
""")
for r in c.fetchall():
    print(f"  line {r[2]:5}  {r[1]:30}  {r[3]}  => {r[0]}")

conn.close()
