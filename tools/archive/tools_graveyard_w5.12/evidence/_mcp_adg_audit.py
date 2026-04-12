"""ADG-guided MCP usage audit."""

import sqlite3
from pathlib import Path

DB = Path(r"c:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03132026_1424.sqlite")
db = sqlite3.connect(str(DB))
db.row_factory = sqlite3.Row
cur = db.cursor()

SEP = "=" * 70

# 1. sequential_thinking call sites
print(SEP)
print("1. SEQUENTIAL_THINKING CALL SITES")
print(SEP)
cur.execute("""
    SELECT DISTINCT n.resolved_path, e.symbol, e.line_no
    FROM nodes n JOIN edges e ON n.id = e.src_id
    WHERE e.symbol LIKE '%sequential_thinking%'
       OR e.symbol LIKE '%sequentialthinking%'
    ORDER BY n.resolved_path, CAST(e.line_no AS INT)
""")
rows = cur.fetchall()
for row in rows:
    print(f"  {row['resolved_path']}:{row['line_no']}  ->  {row['symbol']}")
if not rows:
    print("  (no edge-symbol hits - checking node names)")
    cur.execute("""
        SELECT DISTINCT resolved_path, adg_name FROM nodes
        WHERE adg_name LIKE '%sequential%' OR resolved_path LIKE '%sequential%'
        LIMIT 20
    """)
    for row in cur.fetchall():
        print(f"  {row['resolved_path']}  ::  {row['adg_name']}")

# 2. mcp12 direct references
print()
print(SEP)
print("2. mcp12_sequentialthinking DIRECT REFERENCES")
print(SEP)
cur.execute("""
    SELECT DISTINCT n.resolved_path, e.symbol, e.line_no
    FROM nodes n JOIN edges e ON n.id = e.src_id
    WHERE e.symbol LIKE '%mcp12%'
    ORDER BY n.resolved_path LIMIT 40
""")
rows = cur.fetchall()
for row in rows:
    print(f"  {row['resolved_path']}:{row['line_no']}  ->  {row['symbol']}")
if not rows:
    print("  (no mcp12_ edge references)")

# 3. playwright/fetch/brave/deepwiki gap audit
print()
print(SEP)
print("3. PLAYWRIGHT / FETCH / BRAVE / DEEPWIKI REFERENCE AUDIT")
print(SEP)
terms = [
    ("mcp9_playwright", "mcp9 Playwright"),
    ("mcp1_brave", "mcp1 Brave Search"),
    ("mcp4_fetch", "mcp4 Fetch"),
    ("mcp3_deepwiki", "mcp3 DeepWiki"),
    ("playwright", "playwright (any)"),
    ("brave_search", "brave_search (logical)"),
    ("deepwiki", "deepwiki (logical)"),
]
for term, label in terms:
    cur.execute(
        """
        SELECT DISTINCT n.resolved_path, e.symbol, e.line_no
        FROM nodes n JOIN edges e ON n.id = e.src_id
        WHERE e.symbol LIKE ?
        ORDER BY n.resolved_path LIMIT 10
    """,
        (f"%{term}%",),
    )
    rows = cur.fetchall()
    if rows:
        print(f"\n  [{label}] {len(rows)} reference(s)")
        for row in rows:
            print(f"    {row['resolved_path']}:{row['line_no']}  {row['symbol']}")
    else:
        print(f"\n  [{label}] -- NO REFERENCES FOUND  <- gap")

# 4. Top fan-in modules (best injection points)
print()
print(SEP)
print("4. TOP 15 HIGHEST FAN-IN MODULES (best MCP injection points)")
print(SEP)
cur.execute("""
    SELECT n.resolved_path, COUNT(e.id) AS fan_in
    FROM nodes n JOIN edges e ON n.id = e.dst_id
    WHERE n.entity_type = 'module'
    GROUP BY n.id ORDER BY fan_in DESC LIMIT 15
""")
for row in cur.fetchall():
    print(f"  {row['fan_in']:5d}  {row['resolved_path']}")

# 5. L6 observability / dashboard modules (playwright integration candidates)
print()
print(SEP)
print("5. L6 OBSERVABILITY MODULES (playwright integration candidates)")
print(SEP)
cur.execute("""
    SELECT resolved_path, adg_name FROM nodes
    WHERE layer = 'L6' AND entity_type = 'module'
    ORDER BY resolved_path LIMIT 20
""")
for row in cur.fetchall():
    print(f"  {row['resolved_path']}")

# 6. L2 execution tools (fetch/brave integration candidates)
print()
print(SEP)
print("6. L2 EXECUTION TOOLS (fetch/brave/deepwiki integration candidates)")
print(SEP)
cur.execute("""
    SELECT resolved_path, adg_name FROM nodes
    WHERE layer = 'L2' AND entity_type = 'module'
      AND (resolved_path LIKE '%research%'
        OR resolved_path LIKE '%search%'
        OR resolved_path LIKE '%fetch%'
        OR resolved_path LIKE '%web%'
        OR resolved_path LIKE '%retriev%'
        OR resolved_path LIKE '%egress%')
    ORDER BY resolved_path LIMIT 20
""")
for row in cur.fetchall():
    print(f"  {row['resolved_path']}")

db.close()
print()
print("Done.")
