"""
ADG Structural Outputs — W3.2

Produces four structural analyses from the ADG SQLite:
  1. Burndown table   — violation counts by layer pair, trending over time
  2. Blast radius     — transitive fan-in depth for a given module (or top-N hotspots)
  3. Seam detection   — all cross-layer boundary edges grouped by layer pair
  4. Centrality       — top-N modules by fan-in (most imported/called)

Usage:
  python tools/adg/structural_outputs.py                  # all four, auto-finds latest sqlite
  python tools/adg/structural_outputs.py --mode burndown
  python tools/adg/structural_outputs.py --mode blast-radius --target agentic_core/L0_routing/router.py
  python tools/adg/structural_outputs.py --mode seams
  python tools/adg/structural_outputs.py --mode centrality --top 20
  python tools/adg/structural_outputs.py --sqlite artifacts/adg/adg_indexed_<ts>.sqlite
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .claude/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _find_latest_sqlite() -> Path:
    adg_dir = ROOT / "artifacts" / "adg"
    candidates = sorted(adg_dir.glob("adg_indexed_*.sqlite"), reverse=True)
    if not candidates:
        print("[structural_outputs] ERROR: No adg_indexed_*.sqlite found in artifacts/adg/", file=sys.stderr)
        sys.exit(1)
    return candidates[0]


def _require_positive(value: int, name: str) -> int:
    if value <= 0:
        raise ValueError(f"{name} must be > 0 (got {value})")
    return value


def burndown_table(conn: sqlite3.Connection) -> dict:
    """Layer-pair violation counts — the 'burndown' of P1 defects."""
    cur = conn.cursor()

    rows = cur.execute(
        """
        SELECT
            n_src.layer AS src_layer,
            n_dst.layer AS dst_layer,
            COUNT(*) AS violation_count,
            GROUP_CONCAT(DISTINCT e.source_file) AS sample_files
        FROM edges e
        JOIN nodes n_src ON e.src_id = n_src.id
        JOIN nodes n_dst ON e.dst_id = n_dst.id
        WHERE e.relation_type = 'violates'
        GROUP BY n_src.layer, n_dst.layer
        ORDER BY violation_count DESC
    """
    ).fetchall()

    total = cur.execute(
        "SELECT COUNT(*) FROM edges WHERE relation_type='violates'",
    ).fetchone()[0]

    layer_totals: dict[str, int] = {}
    for src, dst, cnt, _ in rows:
        layer_totals[src or "?"] = layer_totals.get(src or "?", 0) + cnt

    result = {
        "total_violations": total,
        "by_layer_pair": [
            {
                "src_layer": r[0] or "?",
                "dst_layer": r[1] or "?",
                "count": r[2],
                "sample_files": (r[3] or "").split(",")[:3],
            }
            for r in rows
        ],
        "by_src_layer": dict(sorted(layer_totals.items(), key=lambda x: x[1], reverse=True)),
    }
    return result


def blast_radius(conn: sqlite3.Connection, target: str | None = None, top_n: int = 10) -> dict:
    """
    Transitive fan-in: how many modules would be affected if target changed?
    If target is None, returns top_n highest-blast-radius modules.
    """
    cur = conn.cursor()
    top_n = _require_positive(top_n, "top_n")

    if target:
        node_row = cur.execute(
            "SELECT id, adg_name, layer, resolved_path FROM nodes WHERE resolved_path LIKE ? OR adg_name LIKE ? LIMIT 1",
            (f"%{target}%", f"%{target}%"),
        ).fetchone()
        if not node_row:
            return {"error": f"Module not found: {target}"}
        node_id, adg_name, layer, resolved_path = node_row

        visited: set[int] = set()
        frontier = {node_id}
        depth = 0
        depth_map: dict[int, int] = {node_id: 0}

        while frontier:
            next_frontier: set[int] = set()
            placeholders = ",".join("?" for _ in frontier)
            importers = cur.execute(
                f"SELECT src_id FROM edges WHERE dst_id IN ({placeholders}) AND relation_type IN ('imports','calls')",
                list(frontier),
            ).fetchall()
            for (src_id,) in importers:
                if src_id not in visited and src_id != node_id:
                    next_frontier.add(src_id)
                    depth_map[src_id] = depth + 1
            visited.update(frontier)
            frontier = next_frontier - visited
            depth += 1
            if depth > 20:
                break

        affected_node_ids = sorted(
            (nid for nid in depth_map if nid != node_id),
            key=lambda nid: (depth_map[nid], nid),
        )
        node_details: dict[int, tuple[str | None, str | None, str | None]] = {}
        if affected_node_ids:
            rows = cur.execute(
                f"SELECT id, adg_name, layer, resolved_path FROM nodes WHERE id IN ({','.join('?' for _ in affected_node_ids)})",
                affected_node_ids,
            ).fetchall()
            node_details = {row[0]: (row[1], row[2], row[3]) for row in rows}

        return {
            "target": adg_name,
            "target_layer": layer,
            "target_resolved_path": resolved_path,
            "blast_radius_depth": max(depth_map.values(), default=0),
            "affected_module_count": len(affected_node_ids),
            "affected_modules": [
                {
                    "adg_name": node_details.get(nid, (None, None, None))[0],
                    "layer": node_details.get(nid, (None, None, None))[1],
                    "resolved_path": node_details.get(nid, (None, None, None))[2],
                    "depth": depth_map[nid],
                }
                for nid in affected_node_ids[:50]
            ],
        }

    rows = cur.execute(
        """
        SELECT
            n.adg_name,
            n.layer,
            n.resolved_path,
            COUNT(DISTINCT e.src_id) AS direct_fan_in
        FROM nodes n
        JOIN edges e ON e.dst_id = n.id
        WHERE e.relation_type IN ('imports', 'calls')
        GROUP BY n.id
        ORDER BY direct_fan_in DESC
        LIMIT ?
    """,
        (top_n,),
    ).fetchall()

    return {
        "mode": "top_n_hotspots",
        "top_n": top_n,
        "hotspots": [
            {
                "adg_name": r[0],
                "layer": r[1],
                "resolved_path": r[2],
                "direct_fan_in": r[3],
            }
            for r in rows
        ],
    }


def seam_detection(conn: sqlite3.Connection) -> dict:
    """All cross-layer boundary edges — the architectural seams."""
    cur = conn.cursor()

    seam_rows = cur.execute(
        """
        SELECT
            n_src.layer AS src_layer,
            n_dst.layer AS dst_layer,
            e.relation_type,
            COUNT(*) AS edge_count,
            COUNT(DISTINCT e.source_file) AS file_count
        FROM edges e
        JOIN nodes n_src ON e.src_id = n_src.id
        JOIN nodes n_dst ON e.dst_id = n_dst.id
        WHERE n_src.layer IS NOT NULL
          AND n_dst.layer IS NOT NULL
          AND n_src.layer != n_dst.layer
          AND e.relation_type IN ('imports', 'calls', 'violates')
        GROUP BY n_src.layer, n_dst.layer, e.relation_type
        ORDER BY edge_count DESC
        LIMIT 100
    """
    ).fetchall()

    total_cross = cur.execute(
        """
        SELECT COUNT(*)
        FROM edges e
        JOIN nodes n_src ON e.src_id = n_src.id
        JOIN nodes n_dst ON e.dst_id = n_dst.id
        WHERE n_src.layer IS NOT NULL
          AND n_dst.layer IS NOT NULL
          AND n_src.layer != n_dst.layer
          AND e.relation_type IN ('imports', 'calls')
    """
    ).fetchone()[0]

    total_violations = cur.execute(
        "SELECT COUNT(*) FROM edges WHERE relation_type='violates'",
    ).fetchone()[0]

    return {
        "total_cross_layer_edges": total_cross,
        "total_violations": total_violations,
        "seams": [
            {
                "src_layer": r[0],
                "dst_layer": r[1],
                "relation_type": r[2],
                "edge_count": r[3],
                "file_count": r[4],
            }
            for r in seam_rows
        ],
    }


def centrality(conn: sqlite3.Connection, top_n: int = 20) -> dict:
    """Top-N modules by fan-in (most imported/called) — highest centrality."""
    cur = conn.cursor()
    top_n = _require_positive(top_n, "top_n")

    rows = cur.execute(
        """
        SELECT
            n.adg_name,
            n.layer,
            n.resolved_path,
            COUNT(DISTINCT e_in.src_id) AS fan_in,
            COUNT(DISTINCT e_out.dst_id) AS fan_out
        FROM nodes n
        JOIN edges e_in ON e_in.dst_id = n.id AND e_in.relation_type IN ('imports','calls')
        LEFT JOIN edges e_out ON e_out.src_id = n.id AND e_out.relation_type IN ('imports','calls')
        GROUP BY n.id
        ORDER BY fan_in DESC
        LIMIT ?
    """,
        (top_n,),
    ).fetchall()

    total_modules = cur.execute(
        "SELECT COUNT(*) FROM nodes",
    ).fetchone()[0]

    return {
        "total_modules": total_modules,
        "top_n": top_n,
        "nodes": [
            {
                "adg_name": r[0],
                "layer": r[1],
                "resolved_path": r[2],
                "fan_in": r[3],
                "fan_out": r[4],
                "centrality_score": round(r[3] / max(total_modules, 1), 4),
            }
            for r in rows
        ],
    }


def _print_burndown(data: dict) -> None:
    print(f"\n[ADG] Burndown Table — {data['total_violations']} total P1 violations")
    if not data["by_layer_pair"]:
        print("  No violations found — clean!")
        return
    H = "+----------+----------+-------+"
    print(H)
    print("| Src      | Dst      | Count |")
    print(H)
    for row in data["by_layer_pair"]:
        src = (row["src_layer"] or "?")[:8]
        dst = (row["dst_layer"] or "?")[:8]
        print(f"| {src:<8} | {dst:<8} | {row['count']:5} |")
    print(H)


def _print_blast_radius(data: dict, target: str | None) -> None:
    if "error" in data:
        print(f"\n[ADG] Blast Radius: {data['error']}")
        return
    if target:
        print(f"\n[ADG] Blast Radius — {data['target']} (layer: {data['target_layer']})")
        print(f"  Depth:           {data['blast_radius_depth']}")
        print(f"  Affected modules: {data['affected_module_count']}")
    else:
        print(f"\n[ADG] Top-{data['top_n']} Highest Blast Radius (by direct fan-in)")
        H = "+------+----------+------------------------------------------------------+"
        print(H)
        print("| FanIn| Layer    | Module                                               |")
        print(H)
        for h in data["hotspots"]:
            name = h["adg_name"][:52] if h["adg_name"] else ""
            layer = (h["layer"] or "?")[:8]
            print(f"| {h['direct_fan_in']:4} | {layer:<8} | {name:<52} |")
        print(H)


def _print_seams(data: dict) -> None:
    print(
        f"\n[ADG] Seam Detection — {data['total_cross_layer_edges']} cross-layer edges, {data['total_violations']} violations"
    )
    H = "+----------+----------+----------+-------+-------+"
    print(H)
    print("| Src      | Dst      | Type     | Edges | Files |")
    print(H)
    for s in data["seams"][:30]:
        src = (s["src_layer"] or "?")[:8]
        dst = (s["dst_layer"] or "?")[:8]
        rel = s["relation_type"][:8]
        print(f"| {src:<8} | {dst:<8} | {rel:<8} | {s['edge_count']:5} | {s['file_count']:5} |")
    print(H)


def _print_centrality(data: dict) -> None:
    print(f"\n[ADG] Centrality — top {data['top_n']} of {data['total_modules']} modules by fan-in")
    H = "+------+------+----------+------------------------------------------------------+"
    print(H)
    print("| FanIn| FanO | Layer    | Module                                               |")
    print(H)
    for n in data["nodes"]:
        name = n["adg_name"][:52] if n["adg_name"] else ""
        layer = (n["layer"] or "?")[:8]
        print(f"| {n['fan_in']:4} | {n['fan_out']:4} | {layer:<8} | {name:<52} |")
    print(H)


def main() -> None:
    parser = argparse.ArgumentParser(description="ADG Structural Outputs (W3.2)")
    parser.add_argument("--sqlite", help="Path to ADG SQLite file (auto-detected if omitted)")
    parser.add_argument(
        "--mode", choices=["burndown", "blast-radius", "seams", "centrality", "all"], default="all"
    )
    parser.add_argument("--target", help="Module path for blast-radius mode")
    parser.add_argument("--top", type=int, default=20, help="Top-N for centrality/blast-radius")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of tables")
    args = parser.parse_args()

    if args.top <= 0:
        parser.error("--top must be > 0")

    sqlite_path = Path(args.sqlite) if args.sqlite else _find_latest_sqlite()
    if not sqlite_path.exists():
        print(f"[structural_outputs] ERROR: SQLite not found: {sqlite_path}", file=sys.stderr)
        sys.exit(1)

    print(f"[ADG] Structural Outputs — {sqlite_path.name}")
    conn = sqlite3.connect(str(sqlite_path))

    output: dict = {}

    try:
        if args.mode in ("burndown", "all"):
            data = burndown_table(conn)
            output["burndown"] = data
            if not args.json:
                _print_burndown(data)

        if args.mode in ("blast-radius", "all"):
            data = blast_radius(conn, target=args.target, top_n=args.top)
            output["blast_radius"] = data
            if not args.json:
                _print_blast_radius(data, args.target)

        if args.mode in ("seams", "all"):
            data = seam_detection(conn)
            output["seams"] = data
            if not args.json:
                _print_seams(data)

        if args.mode in ("centrality", "all"):
            data = centrality(conn, top_n=args.top)
            output["centrality"] = data
            if not args.json:
                _print_centrality(data)

    finally:
        conn.close()

    if args.json:
        print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
