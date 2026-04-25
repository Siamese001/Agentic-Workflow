"""W7.5 per-file chain verification — production-importer fan-in check.

Lists each .py file in 9 candidate dead folders with their production imports
fan-in (excluding tests/, archives/, tools/debug, tools/diag, tools/archive).
A file with prod_fanin=0 is safe to archive.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

SNAPSHOT = "artifacts/adg/adg_indexed_04232026_1802.sqlite"
FOLDERS = [
    "agentic_core/L4_state/config",
    "agentic_core/L4_state/types",
    "agentic_core/L5_safety/config",
    "agentic_core/L5_safety/validators/static_checks",
    "apps_shared/spine",
    "apps_shared/validators",
]

EXCLUDE = (
    "tests/",
    "archives/",
    "tools/debug/",
    "tools/diag/",
    "tools/archive/",
    "tools/bench/",
)


def main() -> int:
    conn = sqlite3.connect(SNAPSHOT)
    for folder in FOLDERS:
        print(f"=== {folder} ===")
        rows = conn.execute(
            "SELECT resolved_path, id FROM nodes WHERE resolved_path LIKE ? AND entity_type = 'module'",
            (f"{folder}/%",),
        ).fetchall()
        for path, nid in rows:
            total = conn.execute(
                "SELECT COUNT(DISTINCT src_id) FROM edges WHERE dst_id = ? AND relation_type = 'imports'",
                (nid,),
            ).fetchone()[0]
            importers = conn.execute(
                "SELECT DISTINCT n.resolved_path FROM edges e "
                "JOIN nodes n ON e.src_id = n.id "
                "WHERE e.dst_id = ? AND e.relation_type = 'imports'",
                (nid,),
            ).fetchall()
            prod_importers = [
                p[0] for p in importers if p[0] and not any(p[0].startswith(x) for x in EXCLUDE)
            ]
            status = "ARCHIVABLE" if not prod_importers else "BLOCKED"
            print(f"  [{status}] {path}: total_imports_fanin={total} prod_importers={len(prod_importers)}")
            if prod_importers:
                for p in prod_importers[:5]:
                    print(f"      <- {p}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
