import sqlite3

conn = sqlite3.connect(r"C:/Git/Agentic-Workflow/artifacts/adg/adg_indexed_03312026_1808.sqlite")
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("TABLES:", tables)
for t in tables:
    cur.execute(f"PRAGMA table_info({t})")
    cols = [r[1] for r in cur.fetchall()]
    print(f"  {t}: {cols}")
conn.close()
