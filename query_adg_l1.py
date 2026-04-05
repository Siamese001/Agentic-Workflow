"""Query ADG SQLite database for L1_cognition structure."""

import sqlite3
from pathlib import Path

db_path = Path(r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_04052026_1133.sqlite")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", [t[0] for t in tables])

# Query L1_cognition nodes
cursor.execute("""
    SELECT adg_name, entity_type, identity_kind, resolved_path
    FROM nodes 
    WHERE resolved_path LIKE '%L1_cognition%'
    ORDER BY resolved_path
""")
l1_nodes = cursor.fetchall()
print(f"\nL1_cognition nodes ({len(l1_nodes)}):")
for node in l1_nodes[:100]:
    print(f"  {node[3]} - {node[0]} ({node[1]})")

conn.close()
