"""Pull top Wave-1 targets from ADG SQLite. Direct read, no MCP."""

from __future__ import annotations
import sqlite3
import sys
from pathlib import Path

DB = Path("artifacts/adg/adg_indexed_04232026_2248.sqlite")

LAYER_MULT = {
    "L0": 2.0,
    "L5": 2.0,
    "L3": 1.75,
    "L4": 1.75,
    "L1": 1.0,
    "L2": 1.0,
    "L6": 0.75,
}


def main() -> int:
    conn = sqlite3.connect(str(DB))
    c = conn.cursor()

    print("=" * 80)
    print("TOP 25 DEBT HOTSPOTS (mv_debt_concentration_hotspots)")
    print("=" * 80)
    rows = c.execute(
        "SELECT file, layer, p0_count, p1_count, p2_count, p3_count, "
        "total_violations, total_debt_score "
        "FROM mv_debt_concentration_hotspots "
        "ORDER BY total_debt_score DESC LIMIT 25"
    ).fetchall()
    print(f"{'file':<70} {'layer':<10} {'P0':>3} {'P1':>4} {'P2':>4} {'P3':>4} {'TOT':>4} {'score':>7}")
    for f, layer, p0, p1, p2, p3, tot, score in rows:
        short = f if len(f) <= 70 else "..." + f[-67:]
        print(f"{short:<70} {layer or '':<10} {p0:>3} {p1:>4} {p2:>4} {p3:>4} {tot:>4} {score:>7.1f}")

    print("\n" + "=" * 80)
    print("TOP 15 REVERSE-DEPENDENCY HOTSPOTS (mv_graph_reverse_dependency_hotspots)")
    print("=" * 80)
    rows = c.execute(
        "SELECT file_path, layer, direct_inbound, hop2_inbound, "
        "reverse_dependency_score, layer_criticality_weight "
        "FROM mv_graph_reverse_dependency_hotspots "
        "ORDER BY reverse_dependency_score DESC LIMIT 15"
    ).fetchall()
    print(f"{'file':<65} {'layer':<8} {'fanin':>6} {'hop2':>6} {'score':>8} {'wt':>4}")
    for f, layer, fi, h2, sc, wt in rows:
        short = f if len(f) <= 65 else "..." + f[-62:]
        print(f"{short:<65} {layer or '':<8} {fi:>6} {h2:>6} {sc:>8.1f} {wt:>4}")

    # Antipattern breakdown by kind
    print("\n" + "=" * 80)
    print("ANTIPATTERN BREAKDOWN BY KIND")
    print("=" * 80)
    cols = [d[0] for d in c.execute("SELECT * FROM violations LIMIT 0").description]
    print(f"violations cols: {cols}")
    # try common kind columns
    for col in ("kind", "violation_kind", "subtype", "rule", "rule_id"):
        if col in cols:
            rows = c.execute(
                f"SELECT {col}, COUNT(*) FROM violations WHERE category='antipattern' "
                f"GROUP BY {col} ORDER BY COUNT(*) DESC LIMIT 20"
            ).fetchall()
            for k, n in rows:
                print(f"  {n:>6}  {k}")
            break

    # Top centrality (for SSOT extraction candidates)
    print("\n" + "=" * 80)
    print("TOP 15 CENTRALITY NODES (mv_hotspot_centrality — fan-in drivers)")
    print("=" * 80)
    rows = c.execute(
        "SELECT adg_name, layer, resolved_path, fan_in, fan_out, degree_centrality "
        "FROM mv_hotspot_centrality "
        "ORDER BY fan_in DESC LIMIT 15"
    ).fetchall()
    for name, layer, path, fi, fo, dc in rows:
        short_path = (path or "")[-50:]
        print(f"  fan_in={fi:>4} fan_out={fo:>3} L={layer or '-':<4} {name[:40]:<40} {short_path}")

    # Exemptions near critical paths — top by criticality
    print("\n" + "=" * 80)
    print("TOP 15 EXEMPTIONS NEAR CRITICAL PATHS")
    print("=" * 80)
    rows = c.execute(
        "SELECT file, layer, exemption_kind, criticality_score, proximity_flag "
        "FROM mv_exemptions_near_critical_paths "
        "ORDER BY criticality_score DESC LIMIT 15"
    ).fetchall()
    for f, layer, kind, sc, prox in rows:
        short = f if len(f) <= 55 else "..." + f[-52:]
        print(f"  {short:<55} L={layer or '-':<4} {kind:<25} score={sc:>6.1f} {prox}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
