import sqlite3

conn = sqlite3.connect("C:/Git/Agentic-Workflow/artifacts/adg/adg_indexed_03222026_1653.sqlite")
cur = conn.cursor()

# Check determinism edges
determinism_edges = [
    "determinism_seed",
    "emits_determinism_digest",
    "mutation_signature",
    "parent_snapshot_hash",
]
for edge in determinism_edges:
    cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type = ?", (edge,))
    print(f"{edge}: {cur.fetchone()[0]}")

# Get total modules
cur.execute('SELECT COUNT(*) FROM nodes WHERE entity_type = "module"')
total_modules = cur.fetchone()[0]
print(f"Total modules: {total_modules}")

conn.close()
