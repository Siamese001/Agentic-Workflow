#!/usr/bin/env python3
"""Fix boundary classification for all edges in ADG 1653."""

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sqlite_path = ROOT / "artifacts" / "adg" / "adg_indexed_03222026_1653.sqlite"

conn = sqlite3.connect(sqlite_path)
cur = conn.cursor()

# Get all edges without proper classification
cur.execute("""
    SELECT e.id, e.src_id, e.dst_id, e.relation_type, n1.layer, n2.layer
    FROM edges e
    JOIN nodes n1 ON e.src_id = n1.id
    JOIN nodes n2 ON e.dst_id = n2.id
    WHERE e.edge_kind NOT IN ('internal_to_internal', 'internal_to_external', 'external_to_internal', 'unresolved_boundary')
    OR e.edge_kind IS NULL
""")

edges_to_classify = cur.fetchall()
print(f"Found {len(edges_to_classify)} edges to classify")

classified = 0

for edge_id, src_id, dst_id, relation_type, src_layer, dst_layer in edges_to_classify:
    # Determine boundary classification
    if src_layer.startswith('L') and dst_layer.startswith('L'):
        # Both are internal layers
        edge_kind = 'internal_to_internal'
    elif src_layer.startswith('L') and not dst_layer.startswith('L'):
        # Internal to external
        edge_kind = 'internal_to_external'
    elif not src_layer.startswith('L') and dst_layer.startswith('L'):
        # External to internal
        edge_kind = 'external_to_internal'
    else:
        # Both external or unknown
        edge_kind = 'unresolved_boundary'
    
    # Update edge
    cur.execute("""
        UPDATE edges 
        SET edge_kind = ?
        WHERE id = ?
    """, (edge_kind, edge_id))
    classified += 1

conn.commit()
conn.close()

print(f"Classified {classified} edges")
print("Done!")
