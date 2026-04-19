"""Probe ADG SQLite schema and P1 HIGH hotspots."""

import sqlite3
import json

DB = r"artifacts/adg/adg_indexed_04192026_1335.sqlite"
conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cur.fetchall()]
print("TABLES:", tables)

for t in tables:
    cur.execute(f"PRAGMA table_info({t})")
    cols = [(r[1], r[2]) for r in cur.fetchall()]
    print(f"\nSCHEMA {t}: {cols}")

conn.close()
