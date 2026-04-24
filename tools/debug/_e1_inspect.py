"""E.1 inspection — query v_p2_duplicated_adapters and related views."""
import sqlite3
import pathlib

snap = sorted(pathlib.Path("artifacts/adg").glob("adg_indexed_*.sqlite"))[-1]
print(f"snapshot: {snap.name}\n")
conn = sqlite3.connect(str(snap))
cur = conn.cursor()

# 1. Find all duplicate-related views
cur.execute("SELECT name FROM sqlite_master WHERE type='view' AND (name LIKE '%duplic%' OR name LIKE '%adapter%')")
print("duplicate/adapter views:", [r[0] for r in cur.fetchall()])

# 2. v_p2_duplicated_adapters
try:
    cur.execute("SELECT * FROM v_p2_duplicated_adapters LIMIT 50")
    cols = [d[0] for d in cur.description]
    print(f"\nv_p2_duplicated_adapters cols: {cols}")
    for row in cur.fetchall():
        print("  ", dict(zip(cols, row)))
except sqlite3.OperationalError as e:
    print(f"\nv_p2_duplicated_adapters not available: {e}")

# 3. Direct scan for redis / chromadb / sqlite3 client files
print("\n=== Scan nodes for adapter-like files ===")
for pat in ["%redis%client%", "%chroma%", "%sqlite%client%", "%sqlite%adapter%", "%redis%adapter%"]:
    cur.execute("SELECT file_path, layer, adg_name FROM nodes WHERE file_path LIKE ? AND file_path NOT LIKE '%archive%' AND file_path NOT LIKE '%__pycache__%' GROUP BY file_path ORDER BY file_path", (pat,))
    rows = cur.fetchall()
    if rows:
        print(f"\npattern {pat}:")
        for fp, layer, name in rows:
            print(f"  [{layer}] {fp}")
