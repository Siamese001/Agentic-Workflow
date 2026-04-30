"""Static ↔ Runtime ADG Gap Report — behavioral-coverage fitness function.

Joins the static ADG snapshot (``artifacts/adg/adg_indexed_<ts>.sqlite``)
against the runtime evidence ledger (``artifacts/runtime/req_emission_ledger.sqlite``)
to surface code that EXISTS structurally but was NEVER OBSERVED at runtime.

This single query consolidates three of the original recommendation primitives:

  * **Orphan ingest detection** — L5/L6 functions with zero runtime exemplars.
  * **Hotspot adjustment** — the same query ranks orphans by static fan-in,
    which is exactly what the original "hotspot formula sign-flip" needed.
  * **Behavioral coverage metric** — observed/total ratio per layer.

References
----------
* OneUptime, *Dependency Graph Visualization with OpenTelemetry* — pattern of
  joining structural deps to runtime traces.
* Building Evolutionary Architectures (Ford/Parsons) — Architectural Fitness
  Functions as integrity assessments.
* vFunction, *Exposing Dead Code* — runtime evidence is the only reliable
  signal for "exists but never executed."

Usage
-----
::

    python -m tools.audits.static_runtime_gap [--lookback-days N] [--out PATH]

Exit codes
----------
0 — gap report generated successfully (regardless of gap size).
1 — failed to open one or both SQLite stores.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from contextlib import closing
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ADG_DIR = REPO_ROOT / "artifacts" / "adg"
DEFAULT_LEDGER = REPO_ROOT / "artifacts" / "runtime" / "req_emission_ledger.sqlite"

# Layers we explicitly care about for orphan detection. L5/L6 are highest
# priority (per the canonical-invariants doctrine: layer multipliers L5×2.0,
# L6×0.75 — but L6 orphans are the hidden defect class the RCA surfaced).
_OBSERVABILITY_LAYERS = {"L5_safety", "L6_observability", "L5", "L6"}


def _has_nodes_table(p: Path) -> bool:
    """Return True iff the SQLite file has a `nodes` base table.

    Stub/sentinel snapshots (e.g. adg_indexed_99999999_9999.sqlite or partial
    pipeline outputs) can be present in artifacts/adg/ without the nodes
    table. Picking such a stub by mtime would crash downstream queries.
    Mirrors the fix in ops_scripts/ci/executor_theater_gate.py.
    """
    try:
        import sqlite3 as _sq
        with _sq.connect(str(p)) as conn:
            row = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='nodes'"
            ).fetchone()
            return row is not None
    except Exception:
        return False


def latest_static_snapshot(adg_dir: Path = DEFAULT_ADG_DIR) -> Path | None:
    """Return the newest ``adg_indexed_*.sqlite`` snapshot with a `nodes`
    table, or None. Skips stub/sentinel snapshots so downstream queries
    don't fail on missing schema.
    """
    if not adg_dir.exists():
        return None
    snaps = sorted(adg_dir.glob("adg_indexed_*.sqlite"), reverse=True)
    if not snaps:
        return None
    for s in snaps:
        if _has_nodes_table(s):
            return s
    # All stubs — fall through to the newest one so callers still get a
    # deterministic file rather than None when at least one snapshot exists.
    return snaps[0]


def _load_runtime_observed_paths(
    ledger_path: Path,
    *,
    lookback_seconds: int,
) -> set[str]:
    """Return the set of file paths/modules observed in the ledger window.

    Returns an empty set when the ledger is missing — callers must treat that
    as 'no observations' (a max-gap state), not a query failure.
    """
    if not ledger_path.exists():
        return set()
    cutoff = int(time.time()) - lookback_seconds
    paths: set[str] = set()
    with closing(sqlite3.connect(ledger_path)) as con:
        rows = con.execute(
            """
            SELECT DISTINCT source FROM req_emission
            WHERE observed_at >= ?
            """,
            (cutoff,),
        ).fetchall()
    for (source,) in rows:
        if source:
            paths.add(source)
    return paths


def _load_runtime_observed_layers(
    ledger_path: Path,
    *,
    lookback_seconds: int,
) -> set[str]:
    """Return the set of layers seen in the ledger window."""
    if not ledger_path.exists():
        return set()
    cutoff = int(time.time()) - lookback_seconds
    with closing(sqlite3.connect(ledger_path)) as con:
        rows = con.execute(
            "SELECT DISTINCT layer FROM req_emission WHERE observed_at >= ?",
            (cutoff,),
        ).fetchall()
    return {r[0] for r in rows if r[0]}


def _query_static_observability_nodes(
    static_db: Path, *, limit: int = 200,
) -> list[dict[str, Any]]:
    """Query static ADG for L5/L6 function/method nodes ranked by import fan-in.

    The static ADG schema has columns: id, adg_name, entity_type, layer,
    resolved_path. Layer values are bare 'L5'/'L6'. We restrict to function-
    and method-kind entity types so the orphan list is meaningful (a layer
    has thousands of nodes; we want the executable ones).
    """
    if not static_db.exists():
        return []
    with closing(sqlite3.connect(static_db)) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(
            """
            SELECT n.id,
                   n.adg_name      AS display_name,
                   n.layer         AS layer,
                   n.resolved_path AS file_path,
                   n.entity_type   AS entity_type,
                   (SELECT COUNT(*) FROM edges e
                      WHERE e.dst_id = n.id AND e.relation_type = 'imports'
                   )               AS fan_in
            FROM nodes n
            WHERE n.layer IN ('L5', 'L6')
              AND n.entity_type = 'symbol'
            ORDER BY fan_in DESC, n.adg_name
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def compute_gap(
    *,
    static_db: Path | None = None,
    ledger_path: Path = DEFAULT_LEDGER,
    lookback_days: int = 30,
    limit: int = 200,
) -> dict[str, Any]:
    """Compute the static↔runtime gap report. Pure function — no side effects."""
    static_db = static_db or latest_static_snapshot()
    if static_db is None:
        return {
            "ok": False,
            "error": "no_static_snapshot",
            "snapshot_dir": str(DEFAULT_ADG_DIR),
        }
    lookback_seconds = lookback_days * 24 * 3600
    observed_paths = _load_runtime_observed_paths(
        ledger_path, lookback_seconds=lookback_seconds,
    )
    observed_layers = _load_runtime_observed_layers(
        ledger_path, lookback_seconds=lookback_seconds,
    )
    static_nodes = _query_static_observability_nodes(static_db, limit=limit)

    orphans: list[dict[str, Any]] = []
    for n in static_nodes:
        fp = (n.get("file_path") or "").replace("\\", "/")
        seen = any(fp and fp in source for source in observed_paths)
        if not seen:
            orphans.append({
                "id": n["id"],
                "node_name": n["display_name"],
                "layer": n["layer"],
                "file_path": fp,
                "fan_in": n.get("fan_in", 0),
                "first_seen_runtime": None,
            })

    coverage = (
        1.0 - (len(orphans) / max(1, len(static_nodes)))
        if static_nodes
        else 0.0
    )
    return {
        "ok": True,
        "static_snapshot": str(static_db),
        "ledger_path": str(ledger_path),
        "lookback_days": lookback_days,
        "static_observability_nodes": len(static_nodes),
        "runtime_observed_paths": len(observed_paths),
        "runtime_observed_layers": sorted(observed_layers),
        "orphan_count": len(orphans),
        "observability_coverage": round(coverage, 3),
        "top_orphans": orphans[:25],
    }


def render_markdown(report: dict[str, Any]) -> str:
    """Render a concise markdown report for ``docs/reports/calibration/``."""
    if not report.get("ok"):
        return f"# Static↔Runtime Gap Report — ERROR\n\n```json\n{json.dumps(report, indent=2)}\n```\n"

    lines: list[str] = [
        "# Static↔Runtime ADG Gap Report",
        "",
        f"- **Generated:** {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}",
        f"- **Static snapshot:** `{report['static_snapshot']}`",
        f"- **Lookback:** {report['lookback_days']} days",
        f"- **Static L5/L6 nodes scanned:** {report['static_observability_nodes']}",
        f"- **Runtime observed layers:** {', '.join(report['runtime_observed_layers']) or '_none_'}",
        f"- **Orphan count:** {report['orphan_count']}",
        f"- **Observability coverage:** {report['observability_coverage']:.1%}",
        "",
        "## Top Orphans (static-only, never observed at runtime)",
        "",
        "| Layer | Fan-in | Node | File |",
        "|---|---:|---|---|",
    ]
    for o in report["top_orphans"]:
        lines.append(
            f"| {o['layer']} | {o['fan_in']} | `{o['node_name']}` | `{o['file_path']}` |"
        )
    if not report["top_orphans"]:
        lines.append("| _(none)_ | | | |")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "Orphans are L5/L6 functions present in the static dependency graph "
        "but never linked to a REQ exemplar in the runtime ledger window. "
        "High-fan-in orphans are the highest-priority closure candidates: "
        "many static callers, but no runtime evidence the code path fires."
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lookback-days", type=int, default=30)
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT
        / "docs" / "reports" / "calibration"
        / f"static_runtime_gap_{time.strftime('%Y_W%V')}.md",
    )
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args(argv)

    report = compute_gap(lookback_days=args.lookback_days, limit=args.limit)
    if not report.get("ok"):
        print(json.dumps(report, indent=2), file=sys.stderr)
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render_markdown(report), encoding="utf-8")
    print(f"[static_runtime_gap] wrote {args.out}")
    print(
        f"  orphans={report['orphan_count']}  "
        f"coverage={report['observability_coverage']:.1%}  "
        f"static_nodes={report['static_observability_nodes']}"
    )
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"[static_runtime_gap] wrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
