"""Export net P2 antipattern sites for burndown."""
from __future__ import annotations

import json
import logging
import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from agentic_core.adg.artifact.multi_writer import has_guardian_for_violation

ADG_DIR = REPO / "artifacts" / "adg"
db = max(ADG_DIR.glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime)
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute(
    """
    SELECT v.file_path, v.line_no, e.edge_kind, e.source_file
    FROM violations v
    JOIN edges e ON v.edge_id = e.id
    WHERE v.category = 'antipattern' AND v.severity = 'MEDIUM'
    """
)
targets: list[list] = []
for fpath, lno, edge_kind, src in cur.fetchall():
    sf = (src or fpath or "").replace("\\", "/")
    if has_guardian_for_violation(sf, int(lno or 0), edge_kind or ""):
        continue
    norm = sf.replace("\\", "/")
    if "/tests/" in norm or norm.startswith("tests/"):
        continue
    targets.append([sf, int(lno), edge_kind or "", ""])

out = ADG_DIR / f"p2_burndown_targets_{db.stem.replace('adg_indexed_', '')}.json"
out.write_text(json.dumps(targets, indent=2), encoding="utf-8")
logging.info("C3 write receipt: tools/_oneoff/_export_p2_net_targets.py write side effect recorded")
print(out.name, len(targets), targets)
