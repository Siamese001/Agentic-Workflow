"""Probe schema then find modules missing emits_metric_event."""
import sqlite3, glob, os

db_files = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)
db = db_files[-1]
print(f"Using: {db}")
conn = sqlite3.connect(db)

# Show tables
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print(f"Tables: {[t[0] for t in tables]}")

# Show columns of first table
for t in tables:
    cols = conn.execute(f"PRAGMA table_info({t[0]})").fetchall()
    print(f"\n{t[0]} columns: {[c[1] for c in cols]}")

# Show sample relation types
for t in tables:
    try:
        sample = conn.execute(f"SELECT * FROM {t[0]} LIMIT 3").fetchall()
        print(f"\n{t[0]} sample: {sample}")
    except:
        pass

# Find relation_type or edge_type column
for t in tables:
    cols = [c[1] for c in conn.execute(f"PRAGMA table_info({t[0]})").fetchall()]
    for c in cols:
        if 'type' in c.lower() or 'relation' in c.lower() or 'edge' in c.lower():
            distinct = conn.execute(f"SELECT DISTINCT [{c}] FROM {t[0]} LIMIT 20").fetchall()
            print(f"\n{t[0]}.{c} distinct: {[d[0] for d in distinct]}")

conn.close()
