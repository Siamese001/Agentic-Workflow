import sqlite3

DB = r"c:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03132026_0558.sqlite"
conn = sqlite3.connect(DB)
c = conn.cursor()

print("=== ArchitectureGovernorAgent: invokes_getattr_dynamic detail ===")
c.execute("""
    SELECT e.source_file, e.line_no, e.symbol
    FROM edges e
    WHERE e.relation_type='invokes_getattr_dynamic'
      AND e.source_file LIKE '%ArchitectureGovernorAgent%'
    ORDER BY e.line_no
""")
for row in c.fetchall():
    print(f"  line {row[1]}: {row[2]}")

print("\n=== execute_ssot.py: invokes_getattr_dynamic detail (first 20) ===")
c.execute("""
    SELECT e.line_no, e.symbol
    FROM edges e
    WHERE e.relation_type='invokes_getattr_dynamic'
      AND e.source_file LIKE '%execute_ssot%'
    ORDER BY e.line_no
    LIMIT 20
""")
for row in c.fetchall():
    print(f"  line {row[0]}: {row[1]}")

print("\n=== SovereignBaseAgent.py: invokes_getattr_dynamic detail ===")
c.execute("""
    SELECT e.line_no, e.symbol
    FROM edges e
    WHERE e.relation_type='invokes_getattr_dynamic'
      AND e.source_file LIKE '%SovereignBaseAgent%'
    ORDER BY e.line_no
""")
for row in c.fetchall():
    print(f"  line {row[0]}: {row[1]}")

print("\n=== TOP invokes_eval sources with line numbers ===")
c.execute("""
    SELECT e.source_file, e.line_no, e.symbol
    FROM edges e
    WHERE e.relation_type='invokes_eval'
      AND e.source_file NOT LIKE '%test%'
    ORDER BY e.source_file, e.line_no
    LIMIT 30
""")
for row in c.fetchall():
    print(f"  {row[0]}:{row[1]}: {row[2]}")

print("\n=== TOP invokes_dynamic (non-test) ===")
c.execute("""
    SELECT e.source_file, e.line_no, e.symbol
    FROM edges e
    WHERE e.relation_type='invokes_dynamic'
      AND e.source_file NOT LIKE '%test%'
    ORDER BY e.source_file, e.line_no
    LIMIT 30
""")
for row in c.fetchall():
    print(f"  {row[0]}:{row[1]}: {row[2]}")

conn.close()
