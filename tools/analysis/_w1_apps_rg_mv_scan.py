"""W1 — MV / violations / P-view scan over apps_rg surface."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SNAPSHOT = REPO / "artifacts" / "adg" / "adg_indexed_05052026_0722.sqlite"
OUT = REPO / "artifacts" / "_w1_apps_rg_mv_scan.json"


def fetchall_dicts(cur, sql, params=()):
    cur.execute(sql, params)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def safe(cur, sql, params=()):
    try:
        return fetchall_dicts(cur, sql, params)
    except sqlite3.Error as ex:
        return [{"error": str(ex)}]


def main() -> None:
    conn = sqlite3.connect(str(SNAPSHOT))
    cur = conn.cursor()
    out: dict = {"snapshot": str(SNAPSHOT.relative_to(REPO))}

    # Violations table schema + apps_rg slice
    out["violations_columns"] = safe(cur, "PRAGMA table_info(violations)")
    out["violations_summary"] = safe(cur, """
        SELECT severity, COUNT(*) AS n
        FROM violations
        GROUP BY severity
        ORDER BY n DESC
    """)

    # Try a path-aware scan if violations has a path column
    cols = {row.get("name") for row in out["violations_columns"] if isinstance(row, dict)}
    if "resolved_path" in cols:
        out["violations_apps_rg"] = safe(cur, """
            SELECT severity, defect_kind, resolved_path, COUNT(*) AS n
            FROM violations
            WHERE resolved_path LIKE 'apps_rg/%'
            GROUP BY severity, defect_kind, resolved_path
            ORDER BY n DESC
            LIMIT 50
        """)

    # Hotspot centrality slice
    out["mv_hotspot_centrality_top_apps_rg"] = safe(cur, """
        SELECT *
        FROM mv_hotspot_centrality
        WHERE resolved_path LIKE 'apps_rg/%'
        ORDER BY degree_centrality DESC
        LIMIT 30
    """)

    # Reverse-dependency hotspot
    out["mv_graph_reverse_dependency_hotspots_apps_rg"] = safe(cur, """
        SELECT *
        FROM mv_graph_reverse_dependency_hotspots
        WHERE resolved_path LIKE 'apps_rg/%'
        LIMIT 30
    """)

    # Provider surface sprawl — apps_rg slice
    out["mv_provider_surface_sprawl_apps_rg"] = safe(cur, """
        SELECT *
        FROM mv_provider_surface_sprawl
        WHERE resolved_path LIKE 'apps_rg/%'
        LIMIT 30
    """)

    # Gateway bypass paths — apps_rg slice
    out["mv_gateway_bypass_paths_apps_rg"] = safe(cur, """
        SELECT *
        FROM mv_gateway_bypass_paths
        WHERE resolved_path LIKE 'apps_rg/%' OR src_path LIKE 'apps_rg/%' OR dst_path LIKE 'apps_rg/%'
        LIMIT 30
    """)

    # invokes_provider edges where src is under apps_rg/
    out["invokes_provider_from_apps_rg"] = safe(cur, """
        SELECT e.id AS edge_id, e.relation_type,
               sn.id AS src_id, sn.resolved_path AS src_path, sn.adg_name AS src_name,
               dn.id AS dst_id, dn.resolved_path AS dst_path, dn.adg_name AS dst_name
        FROM edges e
        JOIN nodes sn ON sn.id = e.src_id
        JOIN nodes dn ON dn.id = e.dst_id
        WHERE e.relation_type = 'invokes_provider'
          AND sn.resolved_path LIKE 'apps_rg/%'
        ORDER BY sn.resolved_path
        LIMIT 100
    """)

    # antipattern edges anchored in apps_rg/
    out["antipattern_in_apps_rg"] = safe(cur, """
        SELECT e.symbol AS antipattern_kind, COUNT(*) AS n
        FROM edges e
        JOIN nodes sn ON sn.id = e.src_id
        WHERE e.relation_type = 'antipattern'
          AND sn.resolved_path LIKE 'apps_rg/%'
        GROUP BY e.symbol
        ORDER BY n DESC
        LIMIT 30
    """)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"[w1-mv-scan] wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
