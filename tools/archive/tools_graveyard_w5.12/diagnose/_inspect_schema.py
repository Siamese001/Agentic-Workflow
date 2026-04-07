import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADG_DIR = ROOT / "artifacts" / "adg"
db = sorted(ADG_DIR.glob("adg_indexed_*.sqlite"))[-1]
con = sqlite3.connect(db)

tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]
print("TABLES:", tables)
for t in tables:
    cols = [r[1] for r in con.execute(f"PRAGMA table_info({t})")]
    cnt = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"  {t}: {cols}  rows={cnt}")
con.close()
