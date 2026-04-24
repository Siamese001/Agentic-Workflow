"""SSOT-violation report driven by ADG graph layer.

Scans a snapshot for:
  1. Hardcoded path/layer/provider literals captured in `violations.evidence`
  2. Duplicate symbol definitions (same adg_name resolved across multiple files)
  3. Duplicated infra adapters (v_p2_duplicated_adapters)
  4. Authority boundary breaches, gateway bypasses, new cross-layer edges (MVs)
  5. Mis-layered / zero-caller infra (P1 views)
"""

from __future__ import annotations
import sqlite3
import sys
from pathlib import Path
from agentic_core.L0_routing.config.path_constants import ADG_ARTIFACTS_DIR

DEFAULT = Path("artifacts/adg/adg_indexed_04212026_0433.sqlite")

HARDCODED_LITERALS = [
    "D:\\",
    "C:\\",
    "C:/",
    "D:/",
    "/home/",
    "/mnt/",
    "L0_routing",
    "L1_cognition",
    "L2_execution",
    "L3_orchestration",
    "L4_state",
    "L5_safety",
    "L6_observability",
    "localhost",
    "127.0.0.1",
    "http://",
    "https://",
    "sk-",
    "api_key",
    "API_KEY",
    "SSOT",
    "agentic_core/",
    "apps_shared/",
    ADG_ARTIFACTS_DIR + "/",
]


def section(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def run(snap: Path) -> None:
    con = sqlite3.connect(snap)
    print(f"snapshot: {snap}")
    (nc,) = con.execute("SELECT COUNT(*) FROM nodes").fetchone()
    (ec,) = con.execute("SELECT COUNT(*) FROM edges").fetchone()
    print(f"nodes={nc}  edges={ec}")

    # 1) Hardcoded literals in violations.evidence
    section("1. Hardcoded literals in violations.evidence (SSOT-breaking strings)")
    placeholders = " OR ".join(["evidence LIKE ?"] * len(HARDCODED_LITERALS))
    params = [f"%{s}%" for s in HARDCODED_LITERALS]
    rows = con.execute(
        f"SELECT category, evidence, file_path, line_no, severity "
        f"FROM violations WHERE {placeholders} "
        f"ORDER BY severity DESC, file_path LIMIT 80",
        params,
    ).fetchall()
    print(f"matches={len(rows)} (showing up to 80)")
    for cat, ev, fp, ln, sev in rows:
        print(f"  [{sev:<6}] {cat:<14} {fp}:{ln}  ev={ev!r}")

    # Aggregate by literal keyword
    print("\n-- counts per literal --")
    for lit in HARDCODED_LITERALS:
        (c,) = con.execute("SELECT COUNT(*) FROM violations WHERE evidence LIKE ?", (f"%{lit}%",)).fetchone()
        if c:
            print(f"  {lit:<25} {c}")

    # 2) Duplicate symbol definitions — same adg_name at >=2 resolved_path
    section("2. Duplicate symbol definitions (same adg_name, multiple files)")
    rows = con.execute(
        """
        SELECT adg_name, COUNT(DISTINCT resolved_path) AS paths,
               GROUP_CONCAT(DISTINCT resolved_path) AS files
        FROM nodes
        WHERE entity_type IN ('class','function','constant','variable')
          AND resolved_path IS NOT NULL AND resolved_path <> ''
        GROUP BY adg_name
        HAVING paths >= 2
        ORDER BY paths DESC
        LIMIT 30
        """
    ).fetchall()
    print(f"duplicate-name symbols={len(rows)} (top 30)")
    for nm, p, files in rows:
        print(f"  {nm:<55} paths={p}  {files[:160]}")

    # 3) Duplicated infra adapters
    section("3. v_p2_duplicated_adapters")
    for r in con.execute("SELECT * FROM v_p2_duplicated_adapters"):
        print(" ", r)

    # 4) Authority / gateway / cross-layer MVs
    def dump(view: str, limit: int = 15) -> None:
        section(f"MV: {view}")
        try:
            cols = [d[0] for d in con.execute(f"SELECT * FROM {view} LIMIT 0").description]
            (total,) = con.execute(f"SELECT COUNT(*) FROM {view}").fetchone()
            print(f"rows={total}  cols={cols}")
            for r in con.execute(f"SELECT * FROM {view} LIMIT {limit}"):
                print(" ", r)
        except sqlite3.Error as exc:
            print(f"  ERR {exc}")

    dump("mv_authority_boundary_breaches")
    dump("mv_gateway_bypass_paths")
    dump("mv_new_cross_layer_dependencies")
    dump("mv_graph_vs_report_mismatches")
    dump("mv_provider_surface_sprawl")
    dump("mv_manager_sprawl")

    # 5) P0/P1 SSOT-breach views
    section("5. P0/P1 SSOT-breach P-views (any non-empty rows)")
    from tqdm import tqdm as _tqdm  # progress per rule §16

    _p_views = [
        r[0]
        for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='view' "
            "AND (name LIKE 'v_p0_%' OR name LIKE 'v_p1_%') ORDER BY name"
        )
    ]
    for name in _tqdm(_p_views, desc="Scanning P-views", unit="view"):
        try:
            (c,) = con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()
        except sqlite3.Error:
            c = -1
        if c:
            print(f"\n  # {name}  rows={c}")
            for r in con.execute(f"SELECT * FROM {name} LIMIT 10"):
                print("   ", r)
        else:
            print(f"  {name}: 0")

    con.close()


def main() -> int:
    snap = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    if not snap.exists():
        print(f"snapshot not found: {snap}", file=sys.stderr)
        return 2
    run(snap)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
