"""One-shot baseline probe for Wave-1 hotspot plan. Reads SQLite directly."""
from __future__ import annotations
import sqlite3
import sys
from pathlib import Path

DB = Path("artifacts/adg/adg_indexed_04232026_2248.sqlite")


def main() -> int:
    if not DB.exists():
        print(f"MISSING: {DB}")
        return 1
    conn = sqlite3.connect(str(DB))
    c = conn.cursor()

    print("=" * 70)
    print("TABLES:")
    tables = [r[0] for r in c.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    print("  " + "\n  ".join(tables))

    print("\nVIEWS:")
    views = [r[0] for r in c.execute(
        "SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")]
    print("  " + "\n  ".join(views))

    # Violation counts
    if "violations" in tables:
        print("\n" + "=" * 70)
        print("VIOLATIONS BY CATEGORY:")
        rows = c.execute(
            "SELECT category, COUNT(*) FROM violations GROUP BY category "
            "ORDER BY COUNT(*) DESC LIMIT 30"
        ).fetchall()
        for cat, n in rows:
            print(f"  {n:>6}  {cat}")

    # Node/edge count
    for tbl in ("nodes", "edges"):
        if tbl in tables:
            n = c.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
            print(f"\n{tbl}: {n}")

    # Layer distribution
    if "nodes" in tables:
        print("\nNODES BY LAYER:")
        rows = c.execute(
            "SELECT layer, COUNT(*) FROM nodes GROUP BY layer ORDER BY layer"
        ).fetchall()
        for layer, n in rows:
            print(f"  {layer or '(none)':<20} {n}")

    # Key materialized views
    for v in (
        "mv_hotspot_centrality",
        "mv_debt_concentration_hotspots",
        "mv_graph_reverse_dependency_hotspots",
        "mv_exemptions_near_critical_paths",
    ):
        if v in views or v in tables:
            try:
                n = c.execute(f"SELECT COUNT(*) FROM {v}").fetchone()[0]
                print(f"\n{v}: {n} rows")
                cols = [d[0] for d in c.execute(
                    f"SELECT * FROM {v} LIMIT 0").description]
                print(f"  cols: {cols}")
            except sqlite3.Error as exc:
                print(f"  {v}: error {exc}")

    # P-views
    print("\nP-VIEWS (row counts):")
    for v in views:
        if v.startswith("v_p"):
            try:
                n = c.execute(f"SELECT COUNT(*) FROM {v}").fetchone()[0]
                print(f"  {v:<50} {n}")
            except sqlite3.Error as exc:
                print(f"  {v}: error {exc}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
