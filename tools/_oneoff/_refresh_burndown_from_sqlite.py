"""Filter guardian-exempted violations in latest ADG sqlite and refresh burndown table."""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from agentic_core.adg.artifact.multi_writer import _filter_guardian_exempted_violations
from tools.generate.reporting.reports import _print_defect_table

ADG_DIR = REPO / "artifacts" / "adg"
db = max(ADG_DIR.glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime)
conn = sqlite3.connect(db)
removed = _filter_guardian_exempted_violations(conn)
conn.commit()
conn.close()
print(f"filtered={removed} db={db.name}")
_print_defect_table({}, [], sqlite_path=db)
