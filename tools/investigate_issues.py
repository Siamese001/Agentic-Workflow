#!/usr/bin/env python3
"""Investigate test failures."""

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SQLITE_PATH = ROOT / "artifacts" / "adg" / "adg_indexed_03232026_0617.sqlite"

conn = sqlite3.connect(SQLITE_PATH)
cursor = conn.cursor()

print("=== INVESTIGATING DATA INTEGRITY ISSUES ===")

# 1. Check empty resolved_path
cursor.execute("SELECT entity_type, COUNT(*) FROM nodes WHERE resolved_path = '' OR resolved_path IS NULL GROUP BY entity_type")
resolved_path_issues = cursor.fetchall()
print(f"Empty resolved_path by entity_type: {resolved_path_issues}")

# 2. Check security violations
cursor.execute("""
    SELECT n_src.layer, COUNT(*) as count
    FROM edges e
    JOIN nodes n_src ON e.src_id = n_src.id
    WHERE e.relation_type IN ('reads_secret', 'accesses_credential')
    AND n_src.layer = 'L_TEST'
    GROUP BY n_src.layer
""")
security_violations = cursor.fetchall()
print(f"Security violations: {security_violations}")

# 3. Check disconnected replay keys
cursor.execute("""
    SELECT COUNT(*) as disconnected_replay_keys
    FROM edges e1
    WHERE e1.relation_type = 'emits_replay_key'
    AND NOT EXISTS (
        SELECT 1 FROM edges e2
        WHERE (e2.src_id = e1.dst_id OR e2.dst_id = e1.dst_id)
        AND e2.relation_type IN ('links_to_execution_trace', 'mutation_signature')
    )
""")
disconnected_keys = cursor.fetchone()[0]
print(f"Disconnected replay keys: {disconnected_keys}")

conn.close()
