#!/usr/bin/env python3
"""Current ADG state - all L0 gap metrics."""

import os
import sqlite3

adg_dir = r"artifacts\adg"
sqls = sorted([f for f in os.listdir(adg_dir) if f.endswith(".sqlite")], reverse=True)
conn = sqlite3.connect(os.path.join(adg_dir, sqls[0]))
c = conn.cursor()
print(f"DB: {sqls[0]}")

print("\n=== Edge counts (total / prod-only) ===")
for rel in [
    "routes_path",
    "routes_through",
    "proposal_commits_routing",
    "emits_replay_key",
    "emits_determinism_digest",
    "uses_wall_clock",
    "invokes_getattr_dynamic",
    "patches_time",
]:
    c.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (rel,))
    total = c.fetchone()[0]
    c.execute(
        """SELECT COUNT(*) FROM edges e JOIN nodes n ON e.src_id=n.id
                 WHERE e.relation_type=? AND n.layer NOT IN ('L_TEST')""",
        (rel,),
    )
    prod = c.fetchone()[0]
    print(f"  {rel:38} total={total:5}  prod={prod:5}")

print("\n=== Remaining uncovered routing sites (prod only) ===")
c.execute("""
    SELECT DISTINCT n.resolved_path, e.relation_type, e.line_no, n.layer
    FROM edges e JOIN nodes n ON e.src_id = n.id
    WHERE e.relation_type IN ('routes_path','routes_through')
    AND n.layer NOT IN ('L_TEST')
    AND n.resolved_path NOT IN (
        SELECT DISTINCT n2.resolved_path FROM edges e2
        JOIN nodes n2 ON e2.src_id = n2.id
        WHERE e2.relation_type IN ('emits_replay_key','emits_determinism_digest')
        AND n2.layer NOT IN ('L_TEST')
    )
    ORDER BY n.layer, n.resolved_path
""")
rows = c.fetchall()
print(f"  Count: {len(rows)}")
for r in rows:
    print(f"  [{r[3]:8}] line {r[2]:4}  {r[1]:20}  {r[0]}")

print("\n=== uses_wall_clock by layer (prod only, top 10) ===")
c.execute("""
    SELECT n.layer, n.resolved_path, COUNT(*) as cnt
    FROM edges e JOIN nodes n ON e.src_id=n.id
    WHERE e.relation_type='uses_wall_clock' AND n.layer NOT IN ('L_TEST')
    GROUP BY n.layer, n.resolved_path
    ORDER BY cnt DESC
    LIMIT 20
""")
for r in c.fetchall():
    print(f"  [{r[0]:8}] cnt={r[2]:3}  {r[1]}")

print("\n=== invokes_getattr_dynamic by layer (prod only, top 5 files) ===")
c.execute("""
    SELECT n.layer, n.resolved_path, COUNT(*) as cnt
    FROM edges e JOIN nodes n ON e.src_id=n.id
    WHERE e.relation_type='invokes_getattr_dynamic' AND n.layer NOT IN ('L_TEST')
    GROUP BY n.layer, n.resolved_path
    ORDER BY cnt DESC
    LIMIT 10
""")
for r in c.fetchall():
    print(f"  [{r[0]:8}] cnt={r[2]:3}  {r[1]}")

print("\n=== Summary ===")
c.execute("""SELECT COUNT(*) FROM edges e JOIN nodes n ON e.src_id=n.id
             WHERE e.relation_type IN ('routes_path','routes_through')
             AND n.layer NOT IN ('L_TEST')""")
total_route = c.fetchone()[0]
c.execute("""SELECT COUNT(*) FROM edges e JOIN nodes n ON e.src_id=n.id
             WHERE e.relation_type IN ('emits_replay_key','emits_determinism_digest')
             AND n.layer NOT IN ('L_TEST')""")
prod_proof = c.fetchone()[0]
print(f"  Prod routing sites: {total_route}")
print(f"  Prod replay proof edges: {prod_proof}")
print(f"  Coverage: {prod_proof / max(total_route, 1) * 100:.1f}%")

conn.close()
