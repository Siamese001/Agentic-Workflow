"""Get all 145 P1 violations ranked by fan-in then count."""
import sqlite3
from pathlib import Path
from collections import defaultdict

snaps = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime, reverse=True)
DB = str(snaps[0])
conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("""
    SELECT v.id, v.file_path, v.line_no, e.edge_kind, e.symbol, n.layer
    FROM violations v
    LEFT JOIN edges e ON v.edge_id = e.id
    LEFT JOIN nodes n ON e.src_id = n.id
    WHERE v.severity='HIGH'
      AND (v.disposition IS NULL OR v.disposition NOT IN ('exempted','guardian_exempted','waived'))
    ORDER BY v.file_path, v.line_no
""")
sites = cur.fetchall()

cur.execute("""
    SELECT n.resolved_path, COUNT(DISTINCT e2.src_id) as fanin
    FROM nodes n
    JOIN edges e2 ON e2.dst_id = n.id AND e2.relation_type = 'imports'
    WHERE n.resolved_path IS NOT NULL
    GROUP BY n.resolved_path
""")
fanin = {r[0]: r[1] for r in cur.fetchall()}

file_sites = defaultdict(list)
for vid, fp, ln, ek, sym, layer in sites:
    file_sites[fp].append((ln, ek or "unknown", sym or "?", layer or "?"))

ranked = sorted(file_sites.items(), key=lambda x: (-fanin.get(x[0], 0), -len(x[1])))

print(f"Total: {len(sites)} sites in {len(file_sites)} files")
print()
idx = 0
for fp, slist in ranked:
    fi = fanin.get(fp, 0)
    layer = slist[0][3] if slist else "?"
    for ln, ek, sym, _ in sorted(slist):
        idx += 1
        print(f"{idx:>3}. {fp}:{ln}  [{ek}]  catch={sym}  fanin={fi}  layer={layer}")
conn.close()
