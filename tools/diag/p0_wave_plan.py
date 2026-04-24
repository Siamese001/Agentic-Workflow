"""ADG-accelerated P0 violation grouping for wave-based remediation plan."""

from __future__ import annotations

import collections
import re
import sqlite3
from pathlib import Path
from agentic_core.L0_routing.config.path_constants import ADG_ARTIFACTS_DIR
f"{ADG_ARTIFACTS_DIR}/adg_indexed_04172026_0522.sqlite"
DB = Path(f"{ADG_ARTIFACTS_DIR}/adg_indexed_04172026_0522.sqlite")
con = sqlite3.connect(DB)
cur = con.cursor()

# Sample evidence format
cur.execute("SELECT evidence FROM violations WHERE severity='P0' LIMIT 2")
for (ev,) in cur.fetchall():
    print("SAMPLE EVIDENCE:", repr((ev or "")[:400]))
print()

# Full P0 query
cur.execute(
    "SELECT file_path, violation_class, evidence, line_no "
    "FROM violations WHERE severity='P0' "
    "ORDER BY file_path, line_no"
)
rows = cur.fetchall()
print(f"Total P0 violations: {len(rows)}")

hop_counter: collections.Counter = collections.Counter()
by_file: dict = collections.defaultdict(list)

for fp, vc, ev, ln in rows:
    by_file[fp].append((vc, ev, ln))
    m = re.search(r"(L\d)[^L]*(L\d)", ev or "")
    if m:
        hop_counter[f"{m.group(1)}->{m.group(2)}"] += 1

print("\n--- Hop patterns ---")
for hop, cnt in hop_counter.most_common():
    print(f"  {hop}: {cnt}")

print("\n--- Files by P0 count (descending) ---")
for fp, items in sorted(by_file.items(), key=lambda x: -len(x[1])):
    short = fp.replace("agentic_core/", "").replace("agentic_core\\", "")
    print(f"  [{len(items):2d}] {short}")

con.close()
