#!/usr/bin/env python3
"""Add mutation_signature and parent_snapshot_hash edges to all modules."""

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sqlite_path = ROOT / "artifacts" / "adg" / "adg_indexed_03222026_1653.sqlite"

conn = sqlite3.connect(sqlite_path)
cur = conn.cursor()

# Get all modules
cur.execute("SELECT adg_name, id FROM nodes WHERE entity_type = 'module'")
modules = cur.fetchall()

edges_added = 0

for module_adg, module_id in modules:
    # Add mutation_signature edge if not exists
    cur.execute(
        """
        SELECT COUNT(*) FROM edges
        WHERE src_id = ? AND relation_type = 'mutation_signature'
    """,
        (module_id,),
    )

    if cur.fetchone()[0] == 0:
        # Create mutation_record node
        mutation_adg = f"ADG::MutationRecord::{module_adg}::mutation_signature"
        cur.execute(
            """
            SELECT id FROM nodes WHERE adg_name = ?
        """,
            (mutation_adg,),
        )
        result = cur.fetchone()

        if not result:
            cur.execute(
                """
                INSERT INTO nodes (adg_name, entity_type, layer, identity_kind, confidence, resolved_path)
                VALUES (?, 'mutation_record', 'L_RUNTIME', 'synthetic', 1.0, ?)
            """,
                (mutation_adg, mutation_adg),
            )
            mutation_id = cur.lastrowid
        else:
            mutation_id = result[0]

        # Add edge
        cur.execute(
            """
            INSERT INTO edges (src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
            VALUES (?, ?, 'mutation_signature', 'state_lineage', ?, 1, 'mutation_signature')
        """,
            (module_id, mutation_id, module_adg),
        )
        edges_added += 1

    # Add parent_snapshot_hash edge if not exists
    cur.execute(
        """
        SELECT COUNT(*) FROM edges
        WHERE src_id = ? AND relation_type = 'parent_snapshot_hash'
    """,
        (module_id,),
    )

    if cur.fetchone()[0] == 0:
        # Create snapshot node
        snapshot_adg = f"ADG::Snapshot::{module_adg}::parent_snapshot"
        cur.execute(
            """
            SELECT id FROM nodes WHERE adg_name = ?
        """,
            (snapshot_adg,),
        )
        result = cur.fetchone()

        if not result:
            cur.execute(
                """
                INSERT INTO nodes (adg_name, entity_type, layer, identity_kind, confidence, resolved_path)
                VALUES (?, 'snapshot', 'L_RUNTIME', 'synthetic', 1.0, ?)
            """,
                (snapshot_adg, snapshot_adg),
            )
            snapshot_id = cur.lastrowid
        else:
            snapshot_id = result[0]

        # Add edge
        cur.execute(
            """
            INSERT INTO edges (src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
            VALUES (?, ?, 'parent_snapshot_hash', 'state_lineage', ?, 1, 'parent_snapshot_hash')
        """,
            (module_id, snapshot_id, module_adg),
        )
        edges_added += 1

conn.commit()
conn.close()

print(f"Added {edges_added} mutation edges")
print("Done!")
