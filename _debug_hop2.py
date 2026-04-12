#!/usr/bin/env python3
"""Debug hop-2 computation."""

import sqlite3
from pathlib import Path

adg_dir = Path("artifacts/adg")
sqlite_files = sorted(adg_dir.glob("adg_indexed_*.sqlite"))
sqlite_path = sqlite_files[-1]
conn = sqlite3.connect(str(sqlite_path))
cur = conn.cursor()

print("=== Testing hop-2 logic ===")

# Find a module that should have hop-2 importers
# Module A imports B, Module B imports C
# So C should have A as a hop-2 importer

# First, find modules with high direct fan-in
print("\nTop 5 modules by direct fan-in:")
cur.execute("""
    SELECT node_id, resolved_path, direct_fan_in
    FROM mv_dependency_cone_risk
    ORDER BY direct_fan_in DESC
    LIMIT 5
""")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1][:50]} ({row[2]} direct)")

# Test the hop-2 query manually for one module
print("\n=== Manual hop-2 test for lifecycle_trace_contracts ===")
cur.execute("""
    SELECT n.id, n.resolved_path
    FROM nodes n
    WHERE n.resolved_path LIKE '%lifecycle_trace_contract%'
    AND n.entity_type = 'module'
    LIMIT 1
""")
row = cur.fetchone()
if row:
    target_id, target_path = row
    print(f"Target: {target_path} (id={target_id})")

    # Find direct importers
    print("\nDirect importers (hop-1):")
    cur.execute(
        """
        SELECT DISTINCT src.resolved_path
        FROM edges e
        JOIN nodes dst ON e.dst_id = dst.id
        JOIN nodes src ON e.src_id = src.id
        WHERE dst.resolved_path = ?
        AND e.relation_type IN ('imports', 'calls')
        AND dst.resolved_path IS NOT NULL
        AND src.resolved_path IS NOT NULL
        LIMIT 5
    """,
        (target_path,),
    )
    for r in cur.fetchall():
        print(f"  -> {r[0]}")

    # Find hop-2 importers
    print("\nHop-2 importers (A -> B -> target):")
    cur.execute(
        """
        SELECT DISTINCT hop0_src.resolved_path
        FROM edges e1
        JOIN edges e2 ON e2.src_id = e1.dst_id
        JOIN nodes hop0_src ON e1.src_id = hop0_src.id
        JOIN nodes hop1_mid ON e1.dst_id = hop1_mid.id AND e2.src_id = hop1_mid.id
        JOIN nodes hop2_dst ON e2.dst_id = hop2_dst.id
        WHERE hop2_dst.resolved_path = ?
        AND e1.relation_type IN ('imports', 'calls')
        AND e2.relation_type IN ('imports', 'calls')
        AND hop0_src.resolved_path IS NOT NULL
        AND hop2_dst.resolved_path IS NOT NULL
        AND hop0_src.resolved_path != hop2_dst.resolved_path
        LIMIT 5
    """,
        (target_path,),
    )
    rows = cur.fetchall()
    if rows:
        for r in rows:
            print(f"  -> {r[0]}")
    else:
        print("  (none found)")

# Check if there are any edges matching the pattern
print("\n=== Raw hop-2 edge count ===")
cur.execute("""
    SELECT COUNT(*)
    FROM edges e1
    JOIN edges e2 ON e2.src_id = e1.dst_id
    WHERE e1.relation_type IN ('imports', 'calls')
    AND e2.relation_type IN ('imports', 'calls')
""")
print(f"Total e1->e2 chains: {cur.fetchone()[0]}")

conn.close()
