"""ADG-based MCP usage analysis."""

import sqlite3

DB = r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03132026_0558.sqlite"

conn = sqlite3.connect(DB)
cursor = conn.cursor()

# ── 1. All MCP-related nodes ──────────────────────────────────────────────────
print("\n=== MCP NODES (by entity_type) ===")
cursor.execute("""
    SELECT entity_type, COUNT(*) as cnt
    FROM nodes
    WHERE adg_name LIKE '%mcp%' OR adg_name LIKE '%MCP%'
    GROUP BY entity_type ORDER BY cnt DESC
""")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

# ── 2. All mcp-prefixed symbols (mcp0_, mcp1_, etc.) ─────────────────────────
print("\n=== MCP TOOL CALL SYMBOLS (mcp0..mcp9 prefixes) ===")
cursor.execute("""
    SELECT adg_name, entity_type, layer, resolved_path
    FROM nodes
    WHERE adg_name LIKE 'mcp%\\_' ESCAPE '\\'
       OR adg_name LIKE 'mcp0\\_%' ESCAPE '\\'
       OR adg_name LIKE 'mcp1\\_%' ESCAPE '\\'
       OR adg_name LIKE 'mcp4\\_%' ESCAPE '\\'
       OR adg_name LIKE 'mcp5\\_%' ESCAPE '\\'
       OR adg_name LIKE 'mcp6\\_%' ESCAPE '\\'
       OR adg_name LIKE 'mcp8\\_%' ESCAPE '\\'
       OR adg_name LIKE 'mcp9\\_%' ESCAPE '\\'
    ORDER BY adg_name
    LIMIT 100
""")
mcp_symbols = cursor.fetchall()
for row in mcp_symbols:
    print(f"  {row[0]} | {row[1]} | L={row[2]} | {row[3]}")

# ── 3. Which layers/modules reference MCP tools most ─────────────────────────
print("\n=== MCP USAGE BY LAYER (edge sources) ===")
cursor.execute("""
    SELECT n.layer, COUNT(*) as cnt
    FROM edges e
    JOIN nodes n ON e.src_id = n.id
    WHERE e.symbol LIKE 'mcp%'
    GROUP BY n.layer ORDER BY cnt DESC
""")
for row in cursor.fetchall():
    print(f"  Layer {row[0]}: {row[1]} refs")

# ── 4. Most referenced MCP symbols ───────────────────────────────────────────
print("\n=== TOP 30 MCP SYMBOLS BY REFERENCE COUNT ===")
cursor.execute("""
    SELECT e.symbol, COUNT(*) as cnt
    FROM edges e
    WHERE e.symbol LIKE 'mcp%'
    GROUP BY e.symbol ORDER BY cnt DESC
    LIMIT 30
""")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

# ── 5. Files that call MCP tools most ────────────────────────────────────────
print("\n=== TOP 20 FILES USING MCP TOOLS ===")
cursor.execute("""
    SELECT e.source_file, COUNT(*) as cnt
    FROM edges e
    WHERE e.symbol LIKE 'mcp%'
    GROUP BY e.source_file ORDER BY cnt DESC
    LIMIT 20
""")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

# ── 6. Modules doing HTTP/requests without MCP fetch ─────────────────────────
print("\n=== MODULES USING 'requests' or 'urllib' (not MCP fetch) ===")
cursor.execute("""
    SELECT DISTINCT n.resolved_path, n.layer
    FROM nodes n
    JOIN edges e ON e.src_id = n.id
    WHERE (e.symbol LIKE '%requests%' OR e.symbol LIKE '%urllib%' OR e.symbol LIKE '%httpx%')
      AND e.symbol NOT LIKE 'mcp%'
    ORDER BY n.layer
    LIMIT 30
""")
for row in cursor.fetchall():
    print(f"  {row[0]} (L{row[1]})")

# ── 7. Modules doing file I/O without MCP filesystem ─────────────────────────
print("\n=== MODULES USING open()/os.path WITHOUT MCP filesystem ===")
cursor.execute("""
    SELECT n.resolved_path, n.layer, COUNT(*) as cnt
    FROM nodes n
    JOIN edges e ON e.src_id = n.id
    WHERE (e.symbol = 'open' OR e.symbol LIKE 'os.path%' OR e.symbol LIKE 'pathlib%')
      AND n.resolved_path NOT LIKE '%test%'
      AND n.resolved_path NOT LIKE '%ops_script%'
    GROUP BY n.resolved_path ORDER BY cnt DESC
    LIMIT 20
""")
for row in cursor.fetchall():
    print(f"  {row[0]} (L{row[1]}): {row[2]} calls")

# ── 8. Modules doing git operations without MCP ──────────────────────────────
print("\n=== MODULES USING subprocess/git WITHOUT MCP git ===")
cursor.execute("""
    SELECT DISTINCT n.resolved_path, n.layer
    FROM nodes n
    JOIN edges e ON e.src_id = n.id
    WHERE (e.symbol LIKE '%subprocess%' OR e.symbol LIKE '%git%')
      AND e.symbol NOT LIKE 'mcp0%'
      AND n.resolved_path NOT LIKE '%test%'
    ORDER BY n.layer
    LIMIT 30
""")
for row in cursor.fetchall():
    print(f"  {row[0]} (L{row[1]})")

# ── 9. MCP coverage by layer ──────────────────────────────────────────────────
print("\n=== MCP COVERAGE SUMMARY BY LAYER ===")
cursor.execute("""
    SELECT layer, COUNT(DISTINCT id) as total_nodes
    FROM nodes
    WHERE resolved_path IS NOT NULL
    GROUP BY layer ORDER BY layer
""")
layer_totals = {r[0]: r[1] for r in cursor.fetchall()}

cursor.execute("""
    SELECT n.layer, COUNT(DISTINCT n.id) as mcp_users
    FROM nodes n
    JOIN edges e ON e.src_id = n.id
    WHERE e.symbol LIKE 'mcp%'
    GROUP BY n.layer ORDER BY n.layer
""")
for row in cursor.fetchall():
    layer = row[0]
    total = layer_totals.get(layer, 1)
    pct = row[1] / total * 100
    print(f"  L{layer}: {row[1]}/{total} nodes use MCP ({pct:.1f}%)")

conn.close()
print("\nDone.")
