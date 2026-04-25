"""One-shot tech debt review against latest ADG snapshot.

Uses SQLite directly (canonical truth per ADG invariants).
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DB = Path(r"artifacts/adg/adg_indexed_04232026_0925.sqlite")
GDB = Path(r"artifacts/adg/adg_graph_04232026_0925.sqlite")


def section(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def run(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list:
    return conn.execute(sql, params).fetchall()


def table_exists(conn: sqlite3.Connection, name: str) -> bool:
    return bool(conn.execute("SELECT 1 FROM sqlite_master WHERE name=? LIMIT 1", (name,)).fetchone())


def main() -> int:
    c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    # attach graph projection if present
    if GDB.exists():
        c.execute(f"ATTACH DATABASE 'file:{GDB.as_posix()}?mode=ro' AS g")

    # -------- Schema inventory --------
    section("0. SCHEMA INVENTORY — mv_* / v_p* / core tables")
    rows = run(
        c,
        """
        SELECT type, name FROM sqlite_master
         WHERE type IN ('table','view')
           AND (name LIKE 'mv_%' OR name LIKE 'v_p%'
                OR name IN ('violations','nodes','edges'))
         ORDER BY type, name
    """,
    )
    for t, n in rows:
        print(f"  [{t}] {n}")

    # graph projection
    if GDB.exists():
        g_rows = run(
            c,
            """
            SELECT type, name FROM g.sqlite_master
             WHERE type IN ('table','view') ORDER BY type, name
        """,
        )
        print("\n  -- graph projection (attached 'g') --")
        for t, n in g_rows:
            print(f"  [g.{t}] {n}")

    # -------- Violations by severity × class --------
    section("1. ANTI-PATTERN VIOLATIONS \u2014 severity \u00d7 class \u00d7 category")
    rows = run(
        c,
        """
        SELECT COALESCE(severity,'?') sev,
               COALESCE(violation_class,'?') vc,
               COALESCE(category,'?') cat,
               COUNT(*) n
          FROM violations
         GROUP BY sev, vc, cat
         ORDER BY sev, n DESC
    """,
    )
    cur = None
    for sev, vc, cat, n in rows:
        if sev != cur:
            print(f"\n  -- {sev} --")
            cur = sev
        print(f"    {n:5d}  [{vc}]  {cat}")

    # -------- Top files by violation count --------
    section("2. TOP 25 DEBT CONCENTRATION FILES (by violation count)")
    rows = run(
        c,
        """
        SELECT file_path,
               SUM(CASE WHEN severity='CRITICAL' THEN 1 ELSE 0 END) crit,
               SUM(CASE WHEN severity='HIGH'     THEN 1 ELSE 0 END) high,
               SUM(CASE WHEN severity='LOW'      THEN 1 ELSE 0 END) low,
               COUNT(*) total
          FROM violations
         GROUP BY file_path
         ORDER BY total DESC
         LIMIT 25
    """,
    )
    print(f"  {'CRIT':>4} {'HIGH':>4} {'LOW':>4} {'TOT':>4}  FILE")
    for f, cr, hi, lo, tot in rows:
        print(f"  {cr:>4} {hi:>4} {lo:>4} {tot:>4}  {f}")

    # -------- Fan-in hotspots (blast radius) --------
    section("3. TOP 25 FAN-IN (imports) \u2014 blast radius risk")
    rows = run(
        c,
        """
        SELECT n.resolved_path, COUNT(*) AS fanin
          FROM edges e
          JOIN nodes n ON n.id = e.dst_id
         WHERE e.relation_type='imports'
           AND n.resolved_path IS NOT NULL
         GROUP BY n.resolved_path
         ORDER BY fanin DESC
         LIMIT 25
    """,
    )
    for f, fi in rows:
        print(f"  {fi:>5}  {f}")

    # -------- Fan-out hotspots (orchestrators) --------
    section("4. TOP 25 FAN-OUT (imports) \u2014 orchestrator files")
    rows = run(
        c,
        """
        SELECT COALESCE(e.source_file, n.resolved_path) f, COUNT(*) AS fanout
          FROM edges e
          JOIN nodes n ON n.id = e.src_id
         WHERE e.relation_type='imports'
         GROUP BY f
         ORDER BY fanout DESC
         LIMIT 25
    """,
    )
    for f, fo in rows:
        print(f"  {fo:>5}  {f}")

    # -------- Impact-ranked hotspots --------
    section("5. IMPACT-RANKED HOTSPOTS (violations \u00d7 fan-in \u00d7 layer-mult)")
    print("  layer mult: L0/L5=2.0  L3/L4=1.75  L1/L2=1.0  L6=0.75")
    rows = run(
        c,
        """
        WITH v AS (
          SELECT file_path, COUNT(*) vcount,
                 SUM(CASE WHEN severity IN ('CRITICAL','HIGH') THEN 1 ELSE 0 END) crit
            FROM violations GROUP BY file_path
        ),
        fi AS (
          SELECT n.resolved_path AS fp, COUNT(*) fanin
            FROM edges e JOIN nodes n ON n.id=e.dst_id
           WHERE e.relation_type='imports'
             AND n.resolved_path IS NOT NULL
           GROUP BY n.resolved_path
        ),
        lyr AS (
          SELECT resolved_path AS fp, COALESCE(MIN(layer),'?') layer
            FROM nodes WHERE layer IS NOT NULL AND resolved_path IS NOT NULL
           GROUP BY resolved_path
        )
        SELECT v.file_path, COALESCE(l.layer,'?'), v.vcount, v.crit,
               COALESCE(fi.fanin,0) fanin,
               ROUND(
                 v.vcount *
                 (1.0 + CASE WHEN fi.fanin IS NULL OR fi.fanin=0 THEN 0
                             ELSE (LN(1.0+fi.fanin)/LN(10.0)) END) *
                 CASE COALESCE(l.layer,'?')
                   WHEN 'L0' THEN 2.0 WHEN 'L5' THEN 2.0
                   WHEN 'L3' THEN 1.75 WHEN 'L4' THEN 1.75
                   WHEN 'L6' THEN 0.75
                   ELSE 1.0 END, 2) AS impact
          FROM v
          LEFT JOIN fi ON fi.fp = v.file_path
          LEFT JOIN lyr l ON l.fp = v.file_path
         ORDER BY impact DESC
         LIMIT 30
    """,
    )
    print(f"  {'LYR':>3} {'VIO':>4} {'CRIT':>4} {'FI':>5} {'IMPACT':>8}  FILE")
    for f, layer, vc, crit, fi_, imp in rows:
        print(f"  {layer:>3} {vc:>4} {crit:>4} {fi_:>5} {imp:>8}  {f}")

    # -------- Materialized view snapshots --------
    mvs = [
        "mv_hotspot_centrality",
        "mv_debt_concentration_hotspots",
        "mv_graph_reverse_dependency_hotspots",
        "mv_graph_chokepoint_bridges",
        "mv_graph_critical_path_blast_radius",
        "mv_dependency_cone_risk",
        "mv_path_criticality_rollup",
        "mv_exemptions_near_critical_paths",
        "mv_high_fan_in_out_with_defects",
        "mv_repeated_p3_near_critical_paths",
        "mv_gateway_bypass_paths",
        "mv_new_write_bypass_paths",
        "mv_authority_boundary_breaches",
        "mv_manager_sprawl",
        "mv_untrusted_text_to_action_risk",
        "mv_tool_surface_overlap",
        "mv_provider_surface_sprawl",
    ]
    section("6. MATERIALIZED VIEWS — top rows where present")
    for mv in mvs:
        if not table_exists(c, mv):
            print(f"\n  [missing] {mv}")
            continue
        try:
            cols = [r[1] for r in run(c, f"PRAGMA table_info({mv})")]
            count = run(c, f"SELECT COUNT(*) FROM {mv}")[0][0]
            print(f"\n  -- {mv}  ({count} rows)  cols={cols[:6]} --")
            order_col = next(
                (
                    x
                    for x in cols
                    if x
                    in (
                        "impact_score",
                        "centrality_score",
                        "risk_score",
                        "blast_radius",
                        "fanin",
                        "fan_in",
                        "count",
                        "debt_score",
                    )
                ),
                cols[0],
            )
            sample = run(c, f"SELECT * FROM {mv} ORDER BY {order_col} DESC LIMIT 10")
            for row in sample:
                vals = [str(v)[:50] for v in row]
                print("   ", " | ".join(vals))
        except sqlite3.Error as exc:
            print(f"  [err {mv}] {exc}")

    # -------- P-views (pre-classified architectural concerns) --------
    section("7. P-VIEW COUNTS (pre-classified defect rows)")
    pviews = run(
        c,
        """
        SELECT name FROM sqlite_master
         WHERE type='view' AND name LIKE 'v_p%'
         ORDER BY name
    """,
    )
    for (name,) in pviews:
        try:
            n = run(c, f"SELECT COUNT(*) FROM {name}")[0][0]
            print(f"  {n:>6}  {name}")
        except sqlite3.Error as exc:
            print(f"  ERR    {name}  -- {exc}")

    # -------- Semantic edges (behavioral graph layer) --------
    section("8. SEMANTIC EDGE INVENTORY")
    rows = run(
        c,
        """
        SELECT relation_type, COUNT(*) AS n
          FROM edges
         GROUP BY relation_type
         ORDER BY n DESC
    """,
    )
    for rt, n in rows:
        print(f"  {n:>7}  {rt}")

    # -------- Guardian exemptions near critical paths --------
    if table_exists(c, "mv_exemptions_near_critical_paths"):
        section("9. GUARDIAN EXEMPTIONS NEAR CRITICAL PATHS")
        cols = [r[1] for r in run(c, "PRAGMA table_info(mv_exemptions_near_critical_paths)")]
        rows = run(c, "SELECT * FROM mv_exemptions_near_critical_paths LIMIT 15")
        print("  cols:", cols)
        for r in rows:
            print("   ", " | ".join(str(v)[:60] for v in r))

    # -------- Orphan & zero-caller risk --------
    section("10. LOW-UTILITY / ZERO-CALLER PRODUCTION FILES (P1 candidates)")
    if table_exists(c, "v_p1_zero_caller_infra"):
        n = run(c, "SELECT COUNT(*) FROM v_p1_zero_caller_infra")[0][0]
        print(f"  v_p1_zero_caller_infra rows: {n}")
        rows = run(c, "SELECT * FROM v_p1_zero_caller_infra LIMIT 15")
        cols = [r[1] for r in run(c, "PRAGMA table_info(v_p1_zero_caller_infra)")]
        print("  cols:", cols)
        for r in rows:
            print("   ", " | ".join(str(v)[:60] for v in r))
    else:
        print("  (view not present)")

    print("\n[done]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
