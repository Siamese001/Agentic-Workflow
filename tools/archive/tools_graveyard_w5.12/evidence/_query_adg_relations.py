import sqlite3

DB = r"c:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03132026_0558.sqlite"
conn = sqlite3.connect(DB)
c = conn.cursor()

print("=== NODE / EDGE COUNTS ===")
c.execute("SELECT COUNT(*) FROM nodes")
print("nodes:", c.fetchone()[0])
c.execute("SELECT COUNT(*) FROM edges")
print("edges:", c.fetchone()[0])

print("\n=== TOP RELATION TYPES ===")
c.execute(
    "SELECT relation_type, COUNT(*) as cnt FROM edges GROUP BY relation_type ORDER BY cnt DESC LIMIT 25",
)
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]}")

print("\n=== GOVERNANCE PLANE (ChatGPT-claimed relations) ===")
gov_relations = [
    "reads_policy_state",
    "references_policy_hash",
    "writes_through",
    "guards_replay",
    "reads_governed_config",
    "execution_terminates_at_uwg",
    "verifies_policy",
    "observes_policy_state",
    "emits_replay_key",
]
for rel in gov_relations:
    c.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (rel,))
    print(f"  {rel}: {c.fetchone()[0]}")

print("\n=== WRITE SURFACE ===")
for rel in ["writes_to", "writes_through", "execution_terminates_at_uwg"]:
    c.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (rel,))
    print(f"  {rel}: {c.fetchone()[0]}")

print("\n=== DETERMINISM RISK VECTORS (ChatGPT-claimed) ===")
for rel in ["reads_runtime_state", "reads_env", "uses_wall_clock", "guards_replay"]:
    c.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (rel,))
    print(f"  {rel}: {c.fetchone()[0]}")

print("\n=== ACTUAL DISTINCT RELATION_TYPES (full list) ===")
c.execute("SELECT DISTINCT relation_type FROM edges ORDER BY relation_type")
for row in c.fetchall():
    print(f"  {row[0]}")

conn.close()
