"""Generate static test-gap report (basename match + ADG fan-in bands).

Writes: ``docs/reports/test_hotspot_gaps_<snapshot_date>.md``

Companion to ``hotspot_coverage_report.py`` (MV × coverage). This report answers
"does a ``test_<leaf>.py`` exist anywhere?" — not behavioral coverage.

Usage:
    python tools/analysis/test_hotspot_gaps_report.py
    python tools/analysis/test_hotspot_gaps_report.py --adg artifacts/adg/adg_indexed_05242026_2005.sqlite
"""

from __future__ import annotations

__adg_consumer_mode__ = "inventory"

import argparse
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
CORE = REPO / "agentic_core"
TESTS = REPO / "tests"
ADG_DIR = REPO / "artifacts" / "adg"
REPORTS = REPO / "docs" / "reports"
APP_PREFIX = "apps_"

_BANDS = (
    ("P1_critical_fanin_ge_10", 10, None, "Test next — central dependency"),
    ("P2_high_fanin_5_to_9", 5, 9, "Test soon — significant blast radius"),
    ("P3_medium_fanin_2_to_4", 2, 4, "Backlog — moderate impact"),
    ("P4_low_fanin_1", 1, 1, "Optional — single consumer"),
    ("P5_isolated_fanin_0", 0, 0, "Likely dead code — verify before testing"),
)


def _resolve_snapshot(adg: Path | None) -> Path:
    import os

    override = os.environ.get("ADG_SNAPSHOT", "").strip()
    if override:
        p = Path(override)
        if not p.is_absolute():
            p = REPO / p
        if not p.exists():
            raise FileNotFoundError(f"ADG_SNAPSHOT not found: {p}")
        return p.resolve()
    if adg is not None:
        p = adg if adg.is_absolute() else REPO / adg
        if not p.exists():
            raise FileNotFoundError(f"--adg not found: {p}")
        return p.resolve()
    candidates = [
        c
        for c in ADG_DIR.glob("adg_indexed_*.sqlite")
        if "99999999" not in c.name and c.stat().st_size > 50_000_000
    ]
    if not candidates:
        raise FileNotFoundError("no adg_indexed_*.sqlite under artifacts/adg/")
    return max(candidates, key=lambda p: p.stat().st_mtime)


ARCHIVE_MARKER = "_archived_obsolete"


def _test_basenames() -> set[str]:
    if not TESTS.exists():
        return set()
    return {
        p.name
        for p in TESTS.rglob("test_*.py")
        if ARCHIVE_MARKER not in p.parts
    }


def _core_modules() -> list[tuple[str, Path]]:
    rows: list[tuple[str, Path]] = []
    for py in sorted(CORE.rglob("*.py")):
        if py.name == "__init__.py":
            continue
        rel = py.relative_to(REPO)
        mod = ".".join(rel.with_suffix("").parts)
        rows.append((mod, py))
    return rows


def _fan_in_by_path(con: sqlite3.Connection) -> dict[str, int]:
    """File-level fan-in: distinct source files with an edge into any node in dst file."""
    rows = con.execute(
        """
        SELECT dst.resolved_path AS path, COUNT(DISTINCT src.resolved_path) AS fan_in
        FROM edges e
        JOIN nodes dst ON dst.id = e.dst_id
        JOIN nodes src ON src.id = e.src_id
        WHERE dst.resolved_path LIKE 'agentic_core/%'
          AND dst.resolved_path LIKE '%.py'
          AND src.resolved_path IS NOT NULL
        GROUP BY dst.resolved_path
        """
    ).fetchall()
    return {str(r[0]): int(r[1]) for r in rows}


def _app_from_path(path: str) -> str | None:
    first = str(path or "").split("/", 1)[0]
    return first if first.startswith(APP_PREFIX) else None


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO.resolve()))
    except ValueError:
        return str(path)


def _apps_adg_test_reachability(con: sqlite3.Connection) -> list[dict[str, Any]]:
    """ADG-backed apps_* test reachability from ``covers`` edges.

    ``coverage_by_path`` is coverage.py line/branch ingestion. It can be empty
    for an app even when ADG has app nodes, hotspot MVs, and test ``covers``
    edges. This table exposes the apps signal directly so the markdown report
    does not imply that coverage_by_path is the only indicator.
    """
    apps: dict[str, dict[str, Any]] = {}

    def bucket(app: str) -> dict[str, Any]:
        return apps.setdefault(
            app,
            {
                "app": app,
                "adg_source_paths": set(),
                "hotspot_paths": set(),
                "coverage_by_path_rows": set(),
                "covered_paths": set(),
                "covering_tests": set(),
                "covers_edges": 0,
            },
        )

    for (path,) in con.execute(
        """
        SELECT DISTINCT resolved_path
        FROM nodes
        WHERE resolved_path LIKE 'apps_%/%.py'
        """
    ):
        app = _app_from_path(str(path))
        if app:
            bucket(app)["adg_source_paths"].add(str(path))

    for (path,) in con.execute(
        """
        SELECT DISTINCT resolved_path
        FROM mv_hotspot_centrality
        WHERE resolved_path LIKE 'apps_%/%.py'
        """
    ):
        app = _app_from_path(str(path))
        if app:
            bucket(app)["hotspot_paths"].add(str(path))

    for (path,) in con.execute(
        """
        SELECT DISTINCT resolved_path
        FROM coverage_by_path
        WHERE resolved_path LIKE 'apps_%/%.py'
        """
    ):
        app = _app_from_path(str(path))
        if app:
            bucket(app)["coverage_by_path_rows"].add(str(path))

    for source_file, dst_path, edge_count in con.execute(
        """
        SELECT e.source_file, dst.resolved_path, COUNT(*) AS edge_count
        FROM edges e
        JOIN nodes dst ON dst.id = e.dst_id
        WHERE e.relation_type = 'covers'
          AND e.source_file LIKE 'tests/%'
          AND dst.resolved_path LIKE 'apps_%/%.py'
        GROUP BY e.source_file, dst.resolved_path
        """
    ):
        app = _app_from_path(str(dst_path))
        if not app:
            continue
        row = bucket(app)
        row["covered_paths"].add(str(dst_path))
        row["covering_tests"].add(str(source_file))
        row["covers_edges"] += int(edge_count)

    out: list[dict[str, Any]] = []
    for app, row in sorted(apps.items()):
        hotspot_paths = set(row["hotspot_paths"])
        covered_paths = set(row["covered_paths"])
        out.append(
            {
                "app": app,
                "adg_source_paths": len(row["adg_source_paths"]),
                "hotspot_paths": len(hotspot_paths),
                "covered_paths": len(covered_paths),
                "covering_tests": len(row["covering_tests"]),
                "coverage_by_path_rows": len(row["coverage_by_path_rows"]),
                "covers_edges": int(row["covers_edges"]),
                "hotspot_paths_without_covers": len(hotspot_paths - covered_paths),
            }
        )
    return out


def _top_uncovered_app_hotspots(
    con: sqlite3.Connection,
    *,
    limit: int = 50,
) -> list[dict[str, Any]]:
    rows = con.execute(
        """
        WITH covered AS (
            SELECT DISTINCT dst.resolved_path AS path
            FROM edges e
            JOIN nodes dst ON dst.id = e.dst_id
            WHERE e.relation_type = 'covers'
              AND e.source_file LIKE 'tests/%'
              AND dst.resolved_path LIKE 'apps_%/%.py'
        )
        SELECT h.resolved_path, h.fan_in, h.fan_out, h.degree, h.degree_centrality
        FROM mv_hotspot_centrality h
        LEFT JOIN covered c ON c.path = h.resolved_path
        WHERE h.resolved_path LIKE 'apps_%/%.py'
          AND c.path IS NULL
        ORDER BY h.degree_centrality DESC, h.degree DESC, h.resolved_path ASC
        LIMIT ?
        """,
        (int(limit),),
    ).fetchall()
    out: list[dict[str, Any]] = []
    for path, fan_in, fan_out, degree, centrality in rows:
        out.append(
            {
                "app": _app_from_path(str(path)) or "",
                "path": str(path),
                "fan_in": int(fan_in or 0),
                "fan_out": int(fan_out or 0),
                "degree": int(degree or 0),
                "degree_centrality": float(centrality or 0.0),
            }
        )
    return out


def _band(fan_in: int) -> str:
    for band_id, lo, hi, _ in _BANDS:
        if hi is None and fan_in >= lo:
            return band_id
        if hi is not None and lo <= fan_in <= hi:
            return band_id
    return "P5_isolated_fanin_0"


def _layer_from_mod(mod: str) -> str:
    parts = mod.split(".")
    if len(parts) < 2:
        return "(root)"
    second = parts[1]
    if second.startswith("L") and "_" in second:
        return second
    return second


def render(snapshot: Path) -> str:
    test_names = _test_basenames()
    modules = _core_modules()
    con = sqlite3.connect(f"file:{snapshot}?mode=ro", uri=True)
    try:
        fan_in = _fan_in_by_path(con)
        apps_reachability = _apps_adg_test_reachability(con)
        uncovered_app_hotspots = _top_uncovered_app_hotspots(con)
        commit = con.execute(
            "SELECT value FROM meta WHERE key='commit_sha' LIMIT 1"
        ).fetchone()
    finally:
        con.close()

    gaps: list[dict[str, Any]] = []
    covered = 0
    for mod, py in modules:
        leaf = py.stem
        if f"test_{leaf}.py" in test_names:
            covered += 1
        else:
            rel = py.relative_to(REPO).as_posix()
            fi = fan_in.get(rel, 0)
            gaps.append(
                {
                    "mod": mod,
                    "layer": _layer_from_mod(mod),
                    "fan_in": fi,
                    "band": _band(fi),
                }
            )

    total = len(modules)
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    snap_label = snapshot.name
    commit_sha = commit[0] if commit else "unknown"

    lines: list[str] = []
    a = lines.append
    a("# Test Hotspot Gap Report")
    a("")
    a(f"ADG Provenance: backend=sqlite, snapshot={snap_label}")
    a(f"Generated: {ts}")
    a(f"Commit SHA: `{commit_sha}`")
    a("")
    a("## Summary")
    a("")
    a(f"- **Total agentic_core modules (excl. __init__):** {total}")
    a(f"- **Modules with matching test_<name>.py:** {covered} ({100 * covered // total if total else 0}%)")
    a(f"- **Remaining gaps:** {len(gaps)}")
    a("")
    if apps_reachability:
        apps_with_hotspots = sum(1 for r in apps_reachability if r["hotspot_paths"])
        apps_hotspots = sum(int(r["hotspot_paths"]) for r in apps_reachability)
        apps_covered_paths = sum(int(r["covered_paths"]) for r in apps_reachability)
        apps_covering_tests = sum(int(r["covering_tests"]) for r in apps_reachability)
        a(f"- **apps_* packages with ADG hotspot paths:** {apps_with_hotspots}")
        a(f"- **apps_* ADG hotspot paths:** {apps_hotspots}")
        a(f"- **apps_* paths reached by test `covers` edges:** {apps_covered_paths}")
        a(f"- **apps_* distinct covering tests (`covers` source_file):** {apps_covering_tests}")
        a("")
    a("> **W2 note:** P3 modules may have behavioral coverage in")
    a("> `tests/agentic_core/test_p3_w2_hotspot_behavior.py` without a basename match.")
    a("> See `artifacts/test_inventory/w2_basename_collision_audit.md`.")
    a("")
    a("## apps_* ADG Test-Reachability Indicator")
    a("")
    a(
        "This table is ADG-backed. `coverage_by_path` is coverage.py line/branch ingestion; "
        "`covers` edges are the ADG test-reachability indicator from `tests/%` to app paths. "
        "A zero `coverage_by_path` row count does not mean the app is absent from ADG."
    )
    a("")
    a(
        "| App | ADG source paths | Hotspot paths | Paths reached by `covers` | "
        "Distinct covering tests | `covers` edges | `coverage_by_path` rows | Hotspot paths without `covers` |"
    )
    a("|---|---:|---:|---:|---:|---:|---:|---:|")
    for row in apps_reachability:
        a(
            f"| `{row['app']}` | {row['adg_source_paths']} | {row['hotspot_paths']} | "
            f"{row['covered_paths']} | {row['covering_tests']} | {row['covers_edges']} | "
            f"{row['coverage_by_path_rows']} | {row['hotspot_paths_without_covers']} |"
        )
    if not apps_reachability:
        a("| _(none)_ | 0 | 0 | 0 | 0 | 0 | 0 | 0 |")
    a("")
    a("## Top Uncovered apps_* Hotspots by ADG Centrality")
    a("")
    a("| App | Fan-in | Fan-out | Degree | Centrality | Path |")
    a("|---|---:|---:|---:|---:|---|")
    for row in uncovered_app_hotspots:
        a(
            f"| `{row['app']}` | {row['fan_in']} | {row['fan_out']} | {row['degree']} | "
            f"{row['degree_centrality']:.6f} | `{row['path']}` |"
        )
    if not uncovered_app_hotspots:
        a("| _(none)_ | 0 | 0 | 0 | 0.000000 | _(none)_ |")
    a("")
    a("## Gaps by Priority Band (fan-in)")
    a("")
    a("| Band | Fan-in range | Gap count | Action |")
    a("|---|---|---|---|")
    for band_id, lo, hi, action in _BANDS:
        rng = f">= {lo}" if hi is None else (f"{lo}" if lo == hi else f"{lo}–{hi}")
        cnt = sum(1 for g in gaps if g["band"] == band_id)
        a(f"| {band_id} | {rng} | {cnt} | {action} |")
    a("")

    by_layer: dict[str, list[dict[str, Any]]] = {}
    for g in gaps:
        by_layer.setdefault(g["layer"], []).append(g)

    a("## Gaps by Layer")
    a("")
    a("| Layer | Gap count | Top gap (fanin) | Top gap module |")
    a("|---|---|---|---|")
    for layer in sorted(by_layer, key=lambda k: (-len(by_layer[k]), k)):
        items = sorted(by_layer[layer], key=lambda x: (-x["fan_in"], x["mod"]))
        top = items[0]
        a(
            f"| {layer} | {len(items)} | {top['fan_in']} | `{top['mod']}` |"
        )
    a("")

    for band_id, lo, hi, _ in _BANDS:
        title_lo = f">= {lo}" if hi is None else f"{lo}-{hi}" if lo != hi else "1"
        section_gaps = [g for g in gaps if g["band"] == band_id]
        if band_id == "P1_critical_fanin_ge_10":
            heading = "## P1 Critical Gaps (full list, fan-in >= 10)"
        elif band_id == "P2_high_fanin_5_to_9":
            heading = "## P2 High Gaps (full list, fan-in 5-9)"
        elif band_id == "P3_medium_fanin_2_to_4":
            heading = "## P3 Medium Gaps (top 100 of band, fan-in 2-4)"
        else:
            continue
        a(heading)
        a("")
        a("| Fan-in | Layer | Module |")
        a("|---|---|---|")
        ordered = sorted(section_gaps, key=lambda x: (-x["fan_in"], x["mod"]))
        limit = 100 if band_id.startswith("P3") else len(ordered)
        for g in ordered[:limit]:
            a(f"| {g['fan_in']} | {g['layer']} | `{g['mod']}` |")
        a("")
        suffix = f" (showing top {limit})" if limit < len(ordered) else ""
        label = band_id.split("_")[0]
        a(f"**{label} total: {len(section_gaps)}{suffix}**")
        a("")

    a("## Notes")
    a("")
    a("- Coverage measured by basename match: `tests/**/test_<leaf>.py`.")
    a("- Some matches may be name-collisions across layers (e.g. two modules named `types.py`).")
    a("- P5 (fanin=0) modules likely indicate dead code or test-only modules — verify before adding tests.")
    a("- For risk × pytest coverage bands use `artifacts/test_inventory/hotspot_coverage_priority.md`.")
    a(
        "- Renderer: `tools/analysis/test_hotspot_gaps_report.py`."
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--adg", type=Path, default=None)
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output path (default: docs/reports/test_hotspot_gaps_<date>.md)",
    )
    args = parser.parse_args(argv)
    snapshot = _resolve_snapshot(args.adg)
    date_token = datetime.now(timezone.utc).strftime("%m%d%Y")
    out = args.out or (REPORTS / f"test_hotspot_gaps_{date_token}.md")
    out = out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    md = render(snapshot)
    out.write_text(md, encoding="utf-8")
    print(f"[test_hotspot_gaps_report] snapshot={snapshot.name}")
    print(f"[test_hotspot_gaps_report] wrote {_rel(out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
