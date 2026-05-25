"""W4 ADG fan-in probe for L6_observability passive drift (read-only)."""
from __future__ import annotations

import json
import sqlite3
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ADG_DIR = REPO / "artifacts" / "adg"
TARGETS = [
    "agentic_core/L6_observability/promotion/generic_l6_profile_consumer.py",
    "agentic_core/L6_observability/promotion_gates.py",
    "agentic_core/L6_observability/flywheel_promoter.py",
    "agentic_core/L6_observability/otel_runtime_ingest.py",
]


def latest_db() -> Path:
    return max(ADG_DIR.glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime)


def fanin_for(conn: sqlite3.Connection, resolved: str) -> list[tuple[str, str, int]]:
    """Return (importer_path, layer, count) for imports edges into target module."""
    mod_name = f"ADG::Module::{resolved}"
    dst = conn.execute(
        "SELECT id FROM nodes WHERE adg_name = ? LIMIT 1", (mod_name,)
    ).fetchone()
    if not dst:
        return []
    rows = conn.execute(
        """
        SELECT n.resolved_path, n.layer, COUNT(*) AS c
        FROM edges e
        JOIN nodes n ON n.id = e.src_id
        WHERE e.dst_id = ?
          AND e.relation_type = 'imports'
          AND n.resolved_path != ''
        GROUP BY n.resolved_path, n.layer
        ORDER BY c DESC, n.resolved_path
        """,
        (dst[0],),
    ).fetchall()
    return [(r[0], r[1] or "?", int(r[2])) for r in rows]


def fanout_from_prefix(conn: sqlite3.Connection, prefix: str) -> list[str]:
    rows = conn.execute(
        """
        SELECT DISTINCT n.resolved_path
        FROM nodes n
        WHERE n.resolved_path LIKE ?
        ORDER BY n.resolved_path
        """,
        (prefix + "%",),
    ).fetchall()
    return [r[0] for r in rows]


def main() -> None:
    db = latest_db()
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    out: dict = {"adg_snapshot": db.name, "targets": {}, "prefix_modules": {}}
    for t in TARGETS:
        out["targets"][t] = {
            "fanin": fanin_for(conn, t),
            "fanin_count": len(fanin_for(conn, t)),
        }
    for prefix, label in (
        ("agentic_core/L6_observability/promotion/", "promotion_subdir"),
        ("agentic_core/L6_observability/shadow_eval/", "shadow_eval"),
        ("agentic_core/L6_observability/utils/evaluation/", "utils_evaluation"),
        ("system_learning/validators/", "sl_validators"),
    ):
        mods = fanout_from_prefix(conn, prefix)
        out["prefix_modules"][label] = {"prefix": prefix, "module_count": len(mods), "modules": mods}
    conn.close()
    dest = REPO / "docs/reports/cursor/l6_w4_adg_fanin_20260525.json"
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(dest.as_posix())
    for t in TARGETS:
        fi = out["targets"][t]["fanin"]
        print(f"\n{t} fanin={len(fi)}")
        for path, layer, c in fi[:8]:
            print(f"  [{layer}] {path} ({c})")


if __name__ == "__main__":
    main()
