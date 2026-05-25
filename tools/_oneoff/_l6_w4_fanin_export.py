"""Export W4 ADG fan-in JSON."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
db = max((REPO / "artifacts" / "adg").glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime)
conn = sqlite3.connect(db)


def fanin(resolved: str) -> list[dict]:
    rows = conn.execute(
        """
        SELECT n.resolved_path, n.layer, COUNT(*) AS c
        FROM edges e
        JOIN nodes d ON d.id = e.dst_id
        JOIN nodes n ON n.id = e.src_id
        WHERE d.resolved_path = ?
          AND e.relation_type = 'imports'
          AND n.resolved_path != ''
        GROUP BY n.resolved_path, n.layer
        ORDER BY c DESC
        """,
        (resolved,),
    ).fetchall()
    return [{"path": r[0], "layer": r[1], "count": int(r[2])} for r in rows]


def module_count(prefix: str) -> int:
    row = conn.execute(
        """
        SELECT COUNT(DISTINCT resolved_path)
        FROM nodes
        WHERE resolved_path LIKE ?
          AND entity_type = 'module'
        """,
        (prefix + "%",),
    ).fetchone()
    return int(row[0]) if row else 0


targets = [
    "agentic_core/L6_observability/promotion/generic_l6_profile_consumer.py",
    "agentic_core/L6_observability/promotion_gates.py",
    "agentic_core/L6_observability/flywheel_promoter.py",
    "agentic_core/L6_observability/otel_runtime_ingest.py",
]

out: dict = {
    "adg_snapshot": db.name,
    "architecture_path": "PATH_RENAME_CANONICAL",
    "fanin": {
        t: {"importers": fanin(t), "importer_count": len(fanin(t))} for t in targets
    },
    "module_counts": {
        "promotion_subdir": module_count("agentic_core/L6_observability/promotion/"),
        "shadow_eval": module_count("agentic_core/L6_observability/shadow_eval/"),
        "utils_evaluation": module_count("agentic_core/L6_observability/utils/evaluation/"),
        "sl_validators": module_count("system_learning/validators/"),
    },
}
conn.close()

dest = REPO / "docs/reports/cursor/l6_w4_adg_fanin_20260525.json"
dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
print(dest)
