#!/usr/bin/env python3
"""Debug: edges reference symbols, not modules."""

import sqlite3
from pathlib import Path

adg_dir = Path('artifacts/adg')
sqlite_files = sorted(adg_dir.glob('adg_indexed_*.sqlite'))
sqlite_path = sqlite_files[-1]
conn = sqlite3.connect(str(sqlite_path))
cur = conn.cursor()

# Check what node type dst_id 76163 is
print('=== What is node 76163? ===')
cur.execute('SELECT id, entity_type, adg_name, resolved_path, identity_kind FROM nodes WHERE id = 76163')
row = cur.fetchone()
print(f'  {row}')

# Check edges to 76163
print('\n=== Edges to dst_id 76163 ===')
cur.execute("SELECT src_id, relation_type FROM edges WHERE dst_id = 76163 LIMIT 5")
for row in cur.fetchall():
    print(f'  from {row[0]} via {row[1]}')

# What is src_id 76163?
print('\n=== What node is src_id 76163? ===')
cur.execute('SELECT entity_type, adg_name FROM nodes WHERE id = 76163')
row = cur.fetchone()
print(f'  {row}')

# Count edges by target node type
print('\n=== Edge destination breakdown ===')
cur.execute("""
    SELECT n.entity_type, COUNT(*) as cnt
    FROM edges e
    JOIN nodes n ON e.dst_id = n.id
    WHERE e.relation_type IN ('imports', 'calls')
    GROUP BY n.entity_type
    ORDER BY cnt DESC
""")
for row in cur.fetchall():
    print(f'  {row[0]}: {row[1]}')

# The real issue: edges reference symbols, hotspot only looks at modules
# We need to aggregate at symbol level then roll up to module

print('\n=== Fix: Aggregate at symbol level then join to module ===')
cur.execute("""
    SELECT 
        n.resolved_path,
        COUNT(DISTINCT e.id) as inbound_count
    FROM nodes n
    JOIN nodes sym ON sym.resolved_path = n.resolved_path
    JOIN edges e ON e.dst_id = sym.id
    WHERE n.entity_type = 'module'
    AND sym.entity_type = 'symbol'
    AND e.relation_type IN ('imports', 'calls')
    GROUP BY n.id
    ORDER BY inbound_count DESC
    LIMIT 10
""")
for row in cur.fetchall():
    print(f'  {row[1]:5} {row[0][:50]}')

conn.close()
