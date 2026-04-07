"""Check ADG SQLite schema."""

import sqlite3
from pathlib import Path

db = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"), reverse=True)[0]
conn = sqlite3.connect(str(db))
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Tables:", [t[0] for t in tables])
for t in tables:
    cols = conn.execute(f"PRAGMA table_info({t[0]})").fetchall()
    print(f"  {t[0]}:", [c[1] for c in cols])
    sample = conn.execute(f"SELECT * FROM {t[0]} LIMIT 2").fetchall()
    for row in sample:
        print("   sample:", dict(zip([c[1] for c in cols], row)))
conn.close()
