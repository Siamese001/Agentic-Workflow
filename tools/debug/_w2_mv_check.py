import sqlite3, pathlib

p = sorted(pathlib.Path("artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda x: x.stat().st_mtime)[-1]
c = sqlite3.connect(p)
print(f"snap: {p.name}")
tables = [
    r[0]
    for r in c.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'mv_trace%' OR name LIKE 'mv_eval%'"
    )
]
print(f"trace/eval MVs present: {tables}")
for t in tables:
    n = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"  {t}: {n} rows")
