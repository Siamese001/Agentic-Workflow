"""Query ADG SQLite for dead import candidates — safe waves only."""

import sqlite3
from collections import defaultdict
from pathlib import Path

adg_dir = Path("artifacts/adg")
dbs = sorted(adg_dir.glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime, reverse=True)
con = sqlite3.connect(dbs[0])

cur = con.execute(
    "SELECT n.resolved_path, e.symbol, e.line_no "
    "FROM edges e JOIN nodes n ON n.id = e.src_id "
    "WHERE e.relation_type = ? ORDER BY n.resolved_path, e.line_no",
    ("dead_imports",),
)
rows = cur.fetchall()
print(f"Total dead_import edges: {len(rows)}")

by_file: dict = defaultdict(list)
for path, sym, line in rows:
    by_file[path].append((line, sym))

# Safe waves: apps_* and agentic_core/* only, skip compat/shim/types/__init__/config files
safe = {}
for fpath, items in sorted(by_file.items()):
    if not (fpath.startswith("apps_") or fpath.startswith("agentic_core/")):
        continue
    name = Path(fpath).name
    if any(x in name for x in ["compat", "shim", "__init__", "_types", "config", "migrate"]):
        continue
    if "compat" in fpath or "shim" in fpath:
        continue
    safe[fpath] = items

print(f"\nSafe wave candidates: {len(safe)}")
for fpath, items in list(safe.items()):
    symbols = [s.split(".")[-1] for _, s in items]
    print(f"  {fpath}: {symbols}")

con.close()
