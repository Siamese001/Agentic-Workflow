import sqlite3
from pathlib import Path

for ts in ["0713", "0720", "0721"]:
    p = Path(f"artifacts/adg/adg_indexed_04242026_{ts}.sqlite")
    if not p.exists():
        print(f"{ts}: missing")
        continue
    sz = p.stat().st_size
    try:
        c = sqlite3.connect(f"file:{p}?mode=ro", uri=True, timeout=1)
        tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        has_nodes = "nodes" in tables
        nc = c.execute("SELECT COUNT(*) FROM nodes").fetchone()[0] if has_nodes else "N/A"
        c.close()
        print(f"{ts}: size={sz:>12}  tables={len(tables):>3}  nodes={nc}")
    except sqlite3.Error as e:
        print(f"{ts}: size={sz:>12}  ERROR={e}")
