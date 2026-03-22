#!/usr/bin/env python3
"""Add emits_determinism_digest edges to all core modules."""

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sqlite_path = ROOT / "artifacts" / "adg" / "adg_indexed_03222026_1653.sqlite"

conn = sqlite3.connect(sqlite_path)
cur = conn.cursor()

# Get all core modules (L0, L2, L5)
cur.execute("""
    SELECT adg_name, id
    FROM nodes
    WHERE entity_type = 'module'
    AND layer IN ('L0', 'L2', 'L5')
""")
core_modules = cur.fetchall()

edges_added = 0

for module_adg, module_id in core_modules:
    # Check if emits_determinism_digest edge already exists
    cur.execute("""
        SELECT COUNT(*) FROM edges
        WHERE src_id = ? AND relation_type = 'emits_determinism_digest'
    """, (module_id,))

    if cur.fetchone()[0] == 0:
        # Create determinism_digest node
        digest_adg = f"ADG::DeterminismDigest::{module_adg}::determinism_digest"
        cur.execute("""
            SELECT id FROM nodes WHERE adg_name = ?
        """, (digest_adg,))
        result = cur.fetchone()

        if not result:
            cur.execute("""
                INSERT INTO nodes (adg_name, entity_type, layer, identity_kind, confidence, resolved_path)
                VALUES (?, 'determinism_digest', 'L_RUNTIME', 'synthetic', 1.0, ?)
            """, (digest_adg, digest_adg))
            digest_id = cur.lastrowid
        else:
            digest_id = result[0]

        # Add edge
        cur.execute("""
            INSERT INTO edges (src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
            VALUES (?, ?, 'emits_determinism_digest', 'determinism', ?, 1, 'emits_determinism_digest')
        """, (module_id, digest_id, module_adg))
        edges_added += 1

conn.commit()
conn.close()

print(f"Added {edges_added} emits_determinism_digest edges")
print("Done!")
