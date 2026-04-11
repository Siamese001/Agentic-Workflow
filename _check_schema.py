#!/usr/bin/env python3
"""Check schema of key MV tables."""

import sqlite3
from pathlib import Path

adg_dir = Path('artifacts/adg')
sqlite_files = sorted(adg_dir.glob('adg_indexed_*.sqlite'))
sqlite_path = sqlite_files[-1]
conn = sqlite3.connect(str(sqlite_path))
cur = conn.cursor()

print("=== mv_snapshot_integrity_anomalies schema ===")
cur.execute("PRAGMA table_info(mv_snapshot_integrity_anomalies)")
for row in cur.fetchall():
    print(f"  {row[1]} ({row[2]})")

print("\n=== mv_hotspot_centrality schema ===")
cur.execute("PRAGMA table_info(mv_hotspot_centrality)")
for row in cur.fetchall():
    print(f"  {row[1]} ({row[2]})")

print("\n=== Sample from mv_hotspot_centrality ===")
cur.execute("SELECT * FROM mv_hotspot_centrality LIMIT 3")
cols = [d[0] for d in cur.description]
print(f"Columns: {cols}")
for row in cur.fetchall():
    print(row)

print("\n=== Why is fan_in always 0? ===")
cur.execute("SELECT COUNT(*) FROM mv_hotspot_centrality WHERE fan_in > 0")
print(f"Rows with fan_in > 0: {cur.fetchone()[0]}")

# Check if edges reference node IDs correctly
print("\n=== Edge src/dst ID sample ===")
cur.execute("SELECT src_id, dst_id, relation_type FROM edges WHERE relation_type IN ('imports', 'calls') LIMIT 5")
print("Sample edges (src_id, dst_id, type):")
for row in cur.fetchall():
    print(f"  {row}")

print("\n=== Node ID sample ===")
cur.execute("SELECT id, resolved_path FROM nodes WHERE entity_type='module' LIMIT 5")
print("Sample module node IDs:")
for row in cur.fetchall():
    print(f"  {row}")

print("\n=== Check join between edges and nodes ===")
cur.execute("""SELECT COUNT(*) FROM edges e 
    JOIN nodes n ON e.dst_id = n.id 
    WHERE e.relation_type IN ('imports', 'calls')""")
print(f"Joinable edges: {cur.fetchone()[0]}")

conn.close()
