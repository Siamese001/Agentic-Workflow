#!/usr/bin/env python3
"""Investigate replay key connectivity issue."""

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SQLITE_PATH = ROOT / "artifacts" / "adg" / "adg_indexed_03232026_0617.sqlite"

conn = sqlite3.connect(SQLITE_PATH)
cursor = conn.cursor()
cursor.row_factory = sqlite3.Row

print("=== INVESTIGATING REPLAY KEY CONNECTIVITY ===")

# Get all replay keys
cursor.execute("""
    SELECT e1.id, e1.src_id, e1.dst_id
    FROM edges e1
    WHERE e1.relation_type = 'emits_replay_key'
""")
replay_keys = cursor.fetchall()
print(f"Total replay keys: {len(replay_keys)}")

# Check connectivity for each replay key
connected_count = 0
disconnected_details = []

for replay_key in replay_keys[:5]:  # Check first 5
    dst_id = replay_key["dst_id"]

    # Check for connected edges
    cursor.execute(
        """
        SELECT relation_type, COUNT(*) as count
        FROM edges
        WHERE (src_id = ? OR dst_id = ?)
        AND relation_type IN ('links_to_execution_trace', 'mutation_signature')
        GROUP BY relation_type
    """,
        (dst_id, dst_id),
    )

    connected_edges = cursor.fetchall()
    print(f"Replay key {replay_key['id']} -> dst_id {dst_id}: {connected_edges}")

    if connected_edges:
        connected_count += 1
    else:
        disconnected_details.append(replay_key)

print(f"Connected sample: {connected_count}/5")
print(f"Disconnected sample: {len(disconnected_details)}")

# Check what types of edges these replay keys DO have
if disconnected_details:
    sample_dst = disconnected_details[0]["dst_id"]
    cursor.execute(
        """
        SELECT relation_type, COUNT(*) as count
        FROM edges
        WHERE (src_id = ? OR dst_id = ?)
        GROUP BY relation_type
        ORDER BY count DESC
        LIMIT 10
    """,
        (sample_dst, sample_dst),
    )

    all_edges = cursor.fetchall()
    print(f"Sample disconnected replay key edges: {[dict(row) for row in all_edges]}")

conn.close()
