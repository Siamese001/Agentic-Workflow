#!/usr/bin/env python3
"""Debug mv_hotspot_centrality fan_in issue."""

import sqlite3
from pathlib import Path

adg_dir = Path("artifacts/adg")
sqlite_files = sorted(adg_dir.glob("adg_indexed_*.sqlite"))
sqlite_path = sqlite_files[-1]
conn = sqlite3.connect(str(sqlite_path))
cur = conn.cursor()

# Check edge table structure
print("=== Edge table structure ===")
cur.execute("PRAGMA table_info(edges)")
for row in cur.fetchall():
    print(f"  {row}")

# Check edge IDs
print("\n=== Edge ID sample ===")
cur.execute(
    "SELECT id, src_id, dst_id, relation_type FROM edges WHERE relation_type IN ('imports', 'calls') LIMIT 5"
)
for row in cur.fetchall():
    print(f"  {row}")

# Check if join works
print("\n=== Test join ===")
cur.execute("""
    SELECT n.id, n.resolved_path, COUNT(e.id) as cnt
    FROM nodes n
    LEFT JOIN edges e ON e.dst_id = n.id AND e.relation_type IN ('imports', 'calls')
    WHERE n.entity_type = 'module'
    GROUP BY n.id
    ORDER BY cnt DESC
    LIMIT 10
""")
for row in cur.fetchall():
    print(f"  {row}")

# Check which nodes actually have inbound edges
print("\n=== Nodes with most inbound edges ===")
cur.execute("""
    SELECT e.dst_id, COUNT(*) as cnt
    FROM edges e
    WHERE e.relation_type IN ('imports', 'calls')
    GROUP BY e.dst_id
    ORDER BY cnt DESC
    LIMIT 10
""")
for row in cur.fetchall():
    print(f"  dst_id={row[0]} count={row[1]}")

# Check if those dst_ids exist in nodes table
print("\n=== Verify dst_ids exist in nodes ===")
cur.execute("""
    SELECT e.dst_id, n.id, n.resolved_path, COUNT(*) as cnt
    FROM edges e
    JOIN nodes n ON e.dst_id = n.id
    WHERE e.relation_type IN ('imports', 'calls')
    AND n.entity_type = 'module'
    GROUP BY e.dst_id
    ORDER BY cnt DESC
    LIMIT 10
""")
for row in cur.fetchall():
    path = row[2][:40] if row[2] else "None"
    print(f"  edge_dst={row[0]} node_id={row[1]} file={path} count={row[3]}")

conn.close()
print("\n=== Debug complete ===")
