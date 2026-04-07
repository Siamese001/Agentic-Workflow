import sqlite3

DB = r"c:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03132026_0558.sqlite"
conn = sqlite3.connect(DB)
c = conn.cursor()

print("=== TOP FILES: writes_to (ungoverned) ===")
c.execute("""
    SELECT source_file, COUNT(*) as cnt
    FROM edges
    WHERE relation_type='writes_to'
    GROUP BY source_file
    ORDER BY cnt DESC
    LIMIT 20
""")
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]}")

print("\n=== TOP FILES: invokes_eval ===")
c.execute("""
    SELECT source_file, COUNT(*) as cnt
    FROM edges
    WHERE relation_type='invokes_eval'
    GROUP BY source_file
    ORDER BY cnt DESC
    LIMIT 15
""")
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]}")

print("\n=== TOP FILES: invokes_dynamic ===")
c.execute("""
    SELECT source_file, COUNT(*) as cnt
    FROM edges
    WHERE relation_type='invokes_dynamic'
    GROUP BY source_file
    ORDER BY cnt DESC
    LIMIT 15
""")
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]}")

print("\n=== TOP FILES: accesses_credential ===")
c.execute("""
    SELECT source_file, COUNT(*) as cnt
    FROM edges
    WHERE relation_type='accesses_credential'
    GROUP BY source_file
    ORDER BY cnt DESC
    LIMIT 15
""")
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]}")

print("\n=== TOP FILES: reads_secret ===")
c.execute("""
    SELECT source_file, COUNT(*) as cnt
    FROM edges
    WHERE relation_type='reads_secret'
    GROUP BY source_file
    ORDER BY cnt DESC
    LIMIT 15
""")
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]}")

print("\n=== ElevatorShaft / semantic_clock nodes ===")
c.execute(
    "SELECT adg_name, entity_type, layer, resolved_path FROM nodes WHERE adg_name LIKE '%ElevatorShaft%' LIMIT 10",
)
for row in c.fetchall():
    print(f"  {row}")
c.execute(
    "SELECT adg_name, entity_type, layer, resolved_path FROM nodes WHERE adg_name LIKE '%semantic_clock%' LIMIT 10",
)
for row in c.fetchall():
    print(f"  {row}")

conn.close()
