"""Check each L0 violation line to determine if already lazy (inside function) or module-level."""

import pathlib
import sqlite3

DB = pathlib.Path("artifacts/adg/adg_indexed_03122026.sqlite")
conn = sqlite3.connect(DB)

rows = conn.execute(
    "SELECT e.source_file, e.symbol, e.line_no FROM edges e "
    "WHERE e.relation_type='violates' AND e.source_file LIKE '%L0_routing%' "
    "ORDER BY e.source_file, e.line_no",
).fetchall()

REPO = pathlib.Path(".")
print("=== L0 violations: module-level vs lazy ===\n")
module_level = []
lazy = []

for src, sym, lineno in rows:
    path = REPO / src
    if not path.exists():
        continue
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    if lineno is None or lineno < 1 or lineno > len(lines):
        continue
    line = lines[lineno - 1]
    # Check indentation — if indented, it's lazy/inside a function
    indent = len(line) - len(line.lstrip())
    kind = "LAZY" if indent > 0 else "MODULE-LEVEL"
    if indent > 0:
        lazy.append((src, lineno, sym, line.strip()))
    else:
        module_level.append((src, lineno, sym, line.strip()))

print(f"MODULE-LEVEL violations: {len(module_level)}")
for src, ln, sym, line in module_level:
    print(f"  {src}:{ln}  [{sym}]")
    print(f"    {line}")

print(f"\nLAZY (already inside function) violations: {len(lazy)}")
for src, ln, sym, line in lazy:
    print(f"  {src}:{ln}  [{sym}]")
    print(f"    {line}")

conn.close()
