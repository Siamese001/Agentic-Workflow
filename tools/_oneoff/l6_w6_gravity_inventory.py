"""Emit L6→L0..L5 gravity edge inventory from latest ADG snapshot."""
from __future__ import annotations

import json
import sqlite3
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ADG_DIR = REPO / "artifacts" / "adg"
OUT = REPO / "docs/reports/cursor/l6_w6_gravity_edge_inventory_fresh.json"


def _latest_snapshot() -> Path:
    candidates = sorted(ADG_DIR.glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        raise FileNotFoundError(f"No adg_indexed_*.sqlite under {ADG_DIR}")
    return candidates[0]


def main() -> None:
    snapshot = _latest_snapshot()
    con = sqlite3.connect(snapshot)
    layers = ("L0", "L1", "L2", "L3", "L4", "L5")
    ph = ",".join("?" * len(layers))
    rows = con.execute(
        f"""
        SELECT src.resolved_path, tgt.resolved_path, tgt.layer
        FROM edges e
        JOIN nodes src ON e.src_id = src.id
        JOIN nodes tgt ON e.dst_id = tgt.id
        WHERE e.relation_type = 'imports'
          AND src.layer = 'L6'
          AND tgt.layer IN ({ph})
          AND (
            src.resolved_path LIKE 'agentic_core/L6_observability/%'
            OR src.resolved_path LIKE 'agentic_core/L6_system_learning/%'
          )
        """,
        layers,
    ).fetchall()
    con.close()

    by_source: dict[str, list[dict[str, str]]] = defaultdict(list)
    for src, tgt, layer in rows:
        by_source[src].append({"target": tgt, "layer": layer})

    payload = {
        "plan_id": "l6-reorg-deferred-followup-f3a9c2",
        "snapshot": str(snapshot.relative_to(REPO)).replace("\\", "/"),
        "distinct_import_edges": len(rows),
        "source_file_count": len(by_source),
        "by_source": dict(sorted(by_source.items())),
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO)} snapshot={payload['snapshot']} edges={len(rows)} sources={len(by_source)}")


if __name__ == "__main__":
    main()
