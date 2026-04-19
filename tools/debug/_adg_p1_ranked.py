"""
ADG-first P1 HIGH ranked hotspot report.
Joins violations -> edges to get actual antipattern kind per site.
Ranks files by count, shows all sites with line + kind + symbol.
"""

import sqlite3
from pathlib import Path

_snapshots = sorted(
    Path("artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime, reverse=True
)
if not _snapshots:
    raise FileNotFoundError("No ADG snapshot found in artifacts/adg/")
DB = str(_snapshots[0])
print(f"Using snapshot: {_snapshots[0].name}")
conn = sqlite3.connect(DB)
cur = conn.cursor()

# 1. Full site list: violation -> edge -> kind + symbol
cur.execute("""
    SELECT v.id, v.file_path, v.line_no,
           e.edge_kind, e.symbol,
           n.layer
    FROM violations v
    LEFT JOIN edges e ON v.edge_id = e.id
    LEFT JOIN nodes n ON e.src_id = n.id
    WHERE v.severity='HIGH'
      AND (v.disposition IS NULL OR v.disposition NOT IN ('exempted','guardian_exempted','waived'))
    ORDER BY v.file_path, v.line_no
""")
sites = cur.fetchall()

# 2. Aggregate by file
from collections import defaultdict

file_sites = defaultdict(list)
for vid, fp, ln, ek, sym, layer in sites:
    file_sites[fp].append((ln, ek or "unknown", sym or "?", layer or "?"))

# 3. Kind breakdown summary
kind_count = defaultdict(int)
for fp, slist in file_sites.items():
    for ln, ek, sym, layer in slist:
        kind_count[ek] += 1

total_sites = sum(len(v) for v in file_sites.values())
print(f"=== P1 HIGH KIND BREAKDOWN (across all {total_sites} open sites) ===")
for kind, cnt in sorted(kind_count.items(), key=lambda x: -x[1]):
    print(f"  {cnt:5d}  {kind}")

# 4. Top 30 hotspot files ranked by count
ranked = sorted(file_sites.items(), key=lambda x: -len(x[1]))
print(f"\n=== TOP 30 P1 HIGH HOTSPOT FILES ===")
print("  #    n  file"[:80])
for i, (fp, slist) in enumerate(ranked[:30], 1):
    layer = slist[0][3] if slist else "?"
    print(f"{i:>3}  {len(slist):>3}  {fp:<80}  [{layer}]")
    for ln, ek, sym, _ in sorted(slist):
        print(f"          L{ln:<6} {ek:<35} catch={sym}")

# 5. Files with 2+ sites (highest-value targets for wave batching)
print(f"\n=== FILES WITH 2+ OPEN P1 SITES (prime batch targets) ===")
for fp, slist in ranked:
    if len(slist) >= 2:
        print(f"  {len(slist):>2}x  {fp}")
        for ln, ek, sym, layer in sorted(slist):
            print(f"         L{ln:<6} {ek:<35} catch={sym}  [{layer}]")

conn.close()
