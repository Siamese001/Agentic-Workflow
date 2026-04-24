import sqlite3
from pathlib import Path
p = Path("artifacts/adg/adg_indexed_04242026_0720.sqlite")
print(f"exists={p.exists()}  size={p.stat().st_size if p.exists() else 'N/A'}")
c = sqlite3.connect(str(p))
tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY 1").fetchall()]
print(f"tables ({len(tables)}): {tables[:15]}")
if "nodes" in tables:
    print(f"nodes count: {c.execute('SELECT COUNT(*) FROM nodes').fetchone()[0]}")
