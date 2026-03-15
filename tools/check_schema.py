import glob
import os
import sqlite3

ADG_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts", "adg")
pattern = os.path.join(ADG_DIR, "adg_indexed_*.sqlite")
files = sorted(glob.glob(pattern))
db_path = files[-1]
print(f"DB: {os.path.basename(db_path)}")

db = sqlite3.connect(db_path)
cur = db.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print(f"Tables: {tables}")

for t in tables[:5]:
    cur.execute(f"PRAGMA table_info({t})")
    cols = [r[1] for r in cur.fetchall()]
    print(f"  {t}: {cols}")
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    print(f"    rows: {cur.fetchone()[0]}")

db.close()
