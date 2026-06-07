"""Generate the Hotspot × Coverage priority report.

Plan: `docs/archive/windsurf/legacy-tree/plans/hotspot-coverage-pipeline-c4e8d2.md` (W3)

Reads: `mv_hotspot_coverage_risk` from the latest ADG snapshot.
Writes: `artifacts/test_inventory/hotspot_coverage_priority.md`

Output shape (matches the user's bottom diagram from the framing doc):

    | Hotspot | Risk | Coverage | Read |
    | L4 state writer | High | Low | urgent test gap |

Plus distribution tables, per-layer breakdown, and the top-N P1_URGENT list.

Usage:
    python tools/analysis/hotspot_coverage_report.py
    python tools/analysis/hotspot_coverage_report.py --adg <path> --top 25
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .cursor/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import argparse
import sqlite3
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO_ROOT / "artifacts" / "test_inventory" / "hotspot_coverage_priority.md"
DEFAULT_TOP = 25


def _latest_snapshot() -> Path:
    import os

    override = os.environ.get("ADG_SNAPSHOT", "").strip()
    if override:
        p = Path(override)
        if not p.is_absolute():
            p = REPO_ROOT / p
        if not p.exists():
            raise FileNotFoundError(f"ADG_SNAPSHOT not found: {p}")
        return p.resolve()
    adg_dir = REPO_ROOT / "artifacts" / "adg"
    candidates = [
        c
        for c in adg_dir.glob("adg_indexed_*.sqlite")
        if "99999999" not in c.name and c.stat().st_size > 50_000_000
    ]
    if not candidates:
        raise FileNotFoundError("no ADG snapshot found in artifacts/adg/")
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _read(adg_path: Path, top: int) -> dict[str, Any]:
    """Pull all data needed for the report from `mv_hotspot_coverage_risk`."""
    if not adg_path.exists():
        raise FileNotFoundError(f"ADG snapshot not found: {adg_path}")

    con = sqlite3.connect(f"file:{adg_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row

    # Verify the MV exists. If not, return a clear "phase_f never ran" state.
    has_mv = con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='mv_hotspot_coverage_risk'"
    ).fetchone()
    if not has_mv:
        con.close()
        return {"missing_mv": True, "snapshot_path": str(adg_path)}

    total = con.execute("SELECT COUNT(*) FROM mv_hotspot_coverage_risk").fetchone()[0]

    # Priority-band distribution
    priority_dist = list(
        con.execute(
            "SELECT priority_band, COUNT(*) AS n FROM mv_hotspot_coverage_risk "
            "GROUP BY priority_band ORDER BY priority_band"
        )
    )

    # Risk × coverage matrix
    rcov = list(
        con.execute(
            "SELECT risk_band, coverage_band, COUNT(*) AS n "
            "FROM mv_hotspot_coverage_risk "
            "GROUP BY risk_band, coverage_band "
            "ORDER BY risk_band, coverage_band"
        )
    )

    # Per-layer breakdown
    layer_dist = list(
        con.execute(
            "SELECT layer, "
            "  SUM(CASE WHEN priority_band = 'P1_URGENT' THEN 1 ELSE 0 END) AS p1, "
            "  SUM(CASE WHEN priority_band = 'P2_GAP'    THEN 1 ELSE 0 END) AS p2, "
            "  SUM(CASE WHEN priority_band = 'P3_OK'     THEN 1 ELSE 0 END) AS p3, "
            "  SUM(CASE WHEN priority_band = 'P4_LOW'    THEN 1 ELSE 0 END) AS p4, "
            "  SUM(CASE WHEN priority_band = 'P5_NOOP'   THEN 1 ELSE 0 END) AS p5, "
            "  COUNT(*) AS total "
            "FROM mv_hotspot_coverage_risk "
            "GROUP BY layer "
            "ORDER BY p1 DESC, p2 DESC, total DESC"
        )
    )

    # Top-N P1_URGENT and P2_GAP rows
    p1_top = list(
        con.execute(
            "SELECT file, layer, criticality_score, fan_in, fan_out, "
            "  violation_count, coverage_pct, mock_count "
            "FROM mv_hotspot_coverage_risk "
            "WHERE priority_band = 'P1_URGENT' "
            "ORDER BY criticality_score DESC LIMIT ?",
            (top,),
        )
    )
    p2_top = list(
        con.execute(
            "SELECT file, layer, criticality_score, fan_in, fan_out, "
            "  violation_count, coverage_pct, mock_count "
            "FROM mv_hotspot_coverage_risk "
            "WHERE priority_band = 'P2_GAP' "
            "ORDER BY criticality_score DESC LIMIT ?",
            (top,),
        )
    )

    # Coverage data presence stats
    cov_stats = con.execute(
        "SELECT "
        "  SUM(CASE WHEN coverage_pct >= 0.0 THEN 1 ELSE 0 END) AS measured, "
        "  SUM(CASE WHEN coverage_pct < 0.0  THEN 1 ELSE 0 END) AS absent, "
        "  AVG(CASE WHEN coverage_pct >= 0.0 THEN coverage_pct ELSE NULL END) AS avg_pct "
        "FROM mv_hotspot_coverage_risk"
    ).fetchone()

    snapshot_id = con.execute("SELECT value FROM meta WHERE key='commit_sha' LIMIT 1").fetchone()
    snapshot_id = snapshot_id["value"] if snapshot_id else "unknown"

    con.close()

    return {
        "missing_mv": False,
        "snapshot_path": str(adg_path),
        "snapshot_id": snapshot_id,
        "total": total,
        "priority_dist": [dict(r) for r in priority_dist],
        "risk_x_coverage": [dict(r) for r in rcov],
        "layer_dist": [dict(r) for r in layer_dist],
        "p1_top": [dict(r) for r in p1_top],
        "p2_top": [dict(r) for r in p2_top],
        "cov_stats": dict(cov_stats),
    }


def _format(data: dict[str, Any]) -> str:
    """Render the report as markdown."""
    if data.get("missing_mv"):
        return (
            "# Hotspot × Coverage Priority — Report\n\n"
            f"⚠️  `mv_hotspot_coverage_risk` is missing in snapshot "
            f"`{data['snapshot_path']}`.\n\n"
            "The Phase F materialized view has not been generated. "
            "Regenerate the ADG with `python tools/generate_full_adg.py` "
            "to populate it. See plan "
            "`docs/archive/windsurf/legacy-tree/plans/hotspot-coverage-pipeline-c4e8d2.md` for context.\n"
        )

    lines: list[str] = []
    lines.append("# Hotspot × Coverage Priority — Report")
    lines.append("")
    lines.append(f"**Snapshot**: `{data['snapshot_path']}`  ")
    lines.append(f"**Commit SHA**: `{data['snapshot_id']}`  ")
    lines.append(f"**Total nodes scored**: {data['total']}")
    lines.append("")
    cs = data["cov_stats"]
    avg_pct = cs.get("avg_pct")
    avg_pct_str = "—" if avg_pct is None else f"{avg_pct:.1f}%"
    lines.append("## Coverage data presence")
    lines.append("")
    lines.append(f"- **Measured**: {cs['measured']} (have `coverage_pct` from `coverage.py`)")
    lines.append(f"- **Absent**: {cs['absent']} (no coverage data ingested)")
    lines.append(f"- **Average measured coverage**: {avg_pct_str}")
    lines.append("")
    if cs["measured"] == 0:
        lines.append(
            "> ⚠️ **No coverage data was ingested into this snapshot.** Every "
            "row's `coverage_band` is `ABSENT`, so all high-risk modules land in "
            "`P1_URGENT` regardless of actual test coverage. To get meaningful "
            "priority bands, run pytest with `--cov` first, then regenerate ADG."
        )
        lines.append("")

    # Priority distribution
    lines.append("## Priority distribution")
    lines.append("")
    lines.append("| Band | Count | Meaning |")
    lines.append("|---|---:|---|")
    band_meanings = {
        "P1_URGENT": "High risk + ABSENT/MINIMAL coverage — urgent test gap",
        "P2_GAP": "High risk + PARTIAL coverage — add failure/branch tests",
        "P3_OK": "High risk + GOOD/FULL coverage — likely acceptable",
        "P4_LOW": "Medium risk — review during routine refactoring",
        "P5_NOOP": "Low or zero risk — probably acceptable as-is",
    }
    for r in data["priority_dist"]:
        b = r["priority_band"]
        lines.append(f"| `{b}` | {r['n']} | {band_meanings.get(b, '')} |")
    lines.append("")

    # Risk × coverage matrix
    lines.append("## Risk × Coverage matrix")
    lines.append("")
    risk_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    cov_order = ["FULL", "GOOD", "PARTIAL", "MINIMAL", "ABSENT"]
    matrix: dict[tuple[str, str], int] = {}
    for r in data["risk_x_coverage"]:
        matrix[(r["risk_band"], r["coverage_band"])] = r["n"]
    header = "| Risk \\ Coverage | " + " | ".join(cov_order) + " |"
    lines.append(header)
    lines.append("|---|" + "|".join("---:" for _ in cov_order) + "|")
    for risk in risk_order:
        cells = [str(matrix.get((risk, c), 0)) for c in cov_order]
        lines.append(f"| **{risk}** | " + " | ".join(cells) + " |")
    lines.append("")

    # Per-layer breakdown
    lines.append("## Per-layer breakdown")
    lines.append("")
    lines.append("| Layer | P1 | P2 | P3 | P4 | P5 | Total |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for r in data["layer_dist"]:
        lines.append(
            f"| `{r['layer']}` | {r['p1']} | {r['p2']} | {r['p3']} | {r['p4']} | {r['p5']} | {r['total']} |"
        )
    lines.append("")

    # P1_URGENT top list
    lines.append(f"## Top {len(data['p1_top'])} P1_URGENT (high risk, no coverage)")
    lines.append("")
    if not data["p1_top"]:
        lines.append("_None — every high-risk module has at least minimal coverage._")
    else:
        lines.append("| Rank | File | Layer | Crit | Fan-in | Fan-out | Violations | Cov % | Mocks |")
        lines.append("|---:|---|---|---:|---:|---:|---:|---:|---:|")
        for i, r in enumerate(data["p1_top"], 1):
            cov = "—" if r["coverage_pct"] < 0 else f"{r['coverage_pct']:.1f}%"
            lines.append(
                f"| {i} | `{r['file']}` | `{r['layer']}` | "
                f"{r['criticality_score']:.1f} | {r['fan_in']} | "
                f"{r['fan_out']} | {r['violation_count']} | {cov} | "
                f"{r['mock_count']} |"
            )
    lines.append("")

    # P2_GAP top list
    if data["p2_top"]:
        lines.append(f"## Top {len(data['p2_top'])} P2_GAP (high risk, partial coverage)")
        lines.append("")
        lines.append("| Rank | File | Layer | Crit | Cov % | Violations |")
        lines.append("|---:|---|---|---:|---:|---:|")
        for i, r in enumerate(data["p2_top"], 1):
            lines.append(
                f"| {i} | `{r['file']}` | `{r['layer']}` | "
                f"{r['criticality_score']:.1f} | "
                f"{r['coverage_pct']:.1f}% | {r['violation_count']} |"
            )
        lines.append("")

    # Footer / how to read
    lines.append("## How to read")
    lines.append("")
    lines.append("- **Risk** is derived from `mv_path_criticality_rollup.criticality_score`")
    lines.append(
        "  (fan_in × fan_out × violation_count × cross_layer_edges) banded by P50/P75/P95 "
        "percentile within this snapshot."
    )
    lines.append(
        "- **Coverage** is the line-coverage % from `coverage.py` "
        "(intersected with executable-line AST set, capped at 100%)."
    )
    lines.append("- **Priority** is `risk × coverage_weakness` — see top of this report.")
    lines.append(
        "- **Mocks** is the number of `unittest.mock` instantiations in any test "
        "file targeting this module. High mock count means the existing tests "
        "may not exercise the real code path."
    )
    lines.append("")
    lines.append("Source MV: `mv_hotspot_coverage_risk` (Phase F).")
    return "\n".join(lines) + "\n"


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Generate the Hotspot × Coverage priority report. See plan "
            "`docs/archive/windsurf/legacy-tree/plans/hotspot-coverage-pipeline-c4e8d2.md`."
        ),
    )
    p.add_argument(
        "--adg",
        type=Path,
        default=None,
        help="ADG snapshot path (default: latest in artifacts/adg/)",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help=f"Output markdown path (default: {DEFAULT_OUT.relative_to(REPO_ROOT)})",
    )
    p.add_argument(
        "--top",
        type=int,
        default=DEFAULT_TOP,
        help=f"Top-N rows per priority band (default: {DEFAULT_TOP})",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    adg_path = args.adg or _latest_snapshot()
    data = _read(adg_path, top=args.top)
    md = _format(data)
    out_abs = args.out.resolve()
    out_abs.parent.mkdir(parents=True, exist_ok=True)
    out_abs.write_text(md, encoding="utf-8")

    try:
        printable = out_abs.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        printable = str(out_abs)
    print(f"Wrote: {printable}")
    if not data.get("missing_mv"):
        print(f"  total nodes scored: {data['total']}")
        for r in data["priority_dist"]:
            print(f"  {r['priority_band']:<12} {r['n']:>5}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
