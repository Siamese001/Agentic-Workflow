"""Export net P1 antipattern sites (violations minus guardian) for burndown."""
from __future__ import annotations

import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from agentic_core.adg.artifact.multi_writer import has_guardian_for_violation

_PROD_LAYERS = (
    "L0",
    "L1",
    "L2",
    "L3",
    "L4",
    "L5",
    "L6",
    "L_PG",
    "L_APP",
    "L_RUNTIME",
)
ADG_DIR = REPO / "artifacts" / "adg"
db = max(ADG_DIR.glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime)
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute(
    """
    SELECT v.file_path, v.line_no, v.severity, e.edge_kind, e.source_file, n.layer
    FROM violations v
    JOIN edges e ON v.edge_id = e.id
    JOIN nodes n ON e.src_id = n.id
    WHERE v.category = 'antipattern'
      AND v.severity IN ('HIGH', 'CRITICAL')
    ORDER BY v.file_path, v.line_no
    """
)
rows = cur.fetchall()
targets: list[list] = []
by_kind: dict[str, int] = defaultdict(int)
prod_by_kind: dict[str, int] = defaultdict(int)
for fpath, lno, sev, edge_kind, src, layer in rows:
    sf = (src or fpath or "").replace("\\", "/")
    if has_guardian_for_violation(sf, int(lno or 0), edge_kind or ""):
        continue
    norm = sf.replace("\\", "/")
    if "/tests/" in norm or norm.startswith("tests/") or "conftest" in norm:
        continue
    targets.append([sf, int(lno), edge_kind or "", ""])
    by_kind[edge_kind or "unknown"] += 1
    if layer in _PROD_LAYERS:
        prod_by_kind[edge_kind or "unknown"] += 1

out = ADG_DIR / f"p1_burndown_targets_{db.stem.replace('adg_indexed_', '')}.json"
out.write_text(json.dumps(targets, indent=2), encoding="utf-8")
print(out.name, "sites", len(targets))
for k, n in sorted(by_kind.items(), key=lambda x: -x[1]):
    print(f"  {k}: {n} (prod {prod_by_kind.get(k, 0)})")
