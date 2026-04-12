"""ADG Graph Query CLI — analyst interface to adg_graph_<ts>.sqlite.

Reads from the derived graph projection artifact via GraphProjectionBackend.
Never writes. Never touches the canonical adg_indexed_<ts>.sqlite directly.

Exit codes
----------
    0  success (result found and printed)
    1  projection unavailable (no adg_graph_*.sqlite exists or could not be opened)
    2  projection stale (source_artifact_digest does not match current canonical)

Subcommands
-----------
    status
        Show projection availability, staleness, path, source digest, and node count.

    blast-radius <adg_name> [--hops N]
        Print direct and k-hop blast radius for a node.

    scc <adg_name>
        Print SCC membership if the node is in a non-trivial SCC.

    violations [--layer L] [--severity S] [--limit N]
        Print violations sorted by blast-radius impact descending.

    diff [--metric M]
        Print cross-run metric deltas from proj_diff.

Usage examples
--------------
    python tools/adg/adg_graph_query.py status
    python tools/adg/adg_graph_query.py blast-radius "ADG::Module::agentic_core/__init__" --hops 2
    python tools/adg/adg_graph_query.py scc "ADG::Module::tools/adg/core/sqlite_backend"
    python tools/adg/adg_graph_query.py violations --severity HIGH --limit 20
    python tools/adg/adg_graph_query.py diff --metric blast_radius_direct
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path
from typing import Any

from tqdm import tqdm

from tools.adg.core.graph_projection_backend import GraphProjectionBackend

_DIFF_ALL_METRICS = ("fan_in", "fan_out", "blast_radius_direct", "blast_radius_2hop")


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------


def _cmd_status(backend: GraphProjectionBackend) -> int:
    status = backend.get_status()
    print("=== ADG Graph Projection Status ===")
    print(f"  available             : {status['available']}")
    print(f"  stale                 : {status['stale']}")
    print(f"  projection_path       : {status['projection_path'] or '(none)'}")
    print(f"  source_artifact_digest: {status['source_artifact_digest'] or '(none)'}")
    print(f"  proj_schema_version   : {status['proj_schema_version'] or '(none)'}")
    print(f"  node_count            : {status['node_count']}")

    if not status["available"]:
        print("\nNo projection available. Run `python tools/generate/graph_projection.py` to build.")
        return 1
    if status["stale"]:
        print("\nProjection is stale — regenerate with the full ADG pipeline or standalone rebuild.")
        return 2
    return 0


def _cmd_blast_radius(backend: GraphProjectionBackend, adg_name: str, hops: int) -> int:
    if not backend.is_available():
        print(f"ERROR: projection unavailable — cannot query blast-radius for {adg_name!r}")
        return 1

    result = backend.get_blast_radius(adg_name, hops=hops)

    print(f"=== Blast Radius: {adg_name} ===")
    print(f"  available             : {result['available']}")
    print(f"  stale                 : {result['stale']}")
    print(f"  blast_radius_direct   : {result['blast_radius_direct']}")
    print(f"  blast_radius_2hop     : {result['blast_radius_2hop']}")
    print(f"  reachability_rows     : {result['reachability_rows']}")
    print(f"  hops_requested        : {result['hops_requested']}")
    print(f"  derived_from          : {result['derived_from']}")

    if result["blast_radius_direct"] == 0 and result["blast_radius_2hop"] == 0:
        print("\n(Node not found in projection or has zero inbound edges.)")

    if result["stale"]:
        return 2
    return 0


def _cmd_scc(backend: GraphProjectionBackend, adg_name: str) -> int:
    if not backend.is_available():
        print(f"ERROR: projection unavailable — cannot query SCC for {adg_name!r}")
        return 1

    result = backend.get_scc(adg_name)

    print(f"=== SCC Membership: {adg_name} ===")
    if result is None:
        print("  (not in any non-trivial SCC — architecturally clean)")
        if backend.is_stale():
            return 2
        return 0

    print(f"  scc_id                : {result['scc_id']}")
    print(f"  scc_size              : {result['scc_size']}")
    print(f"  scc_type              : {result['scc_type']}")
    print(f"  scc_risk_score        : {result['scc_risk_score']:.4f}")
    print(f"  stale                 : {result['stale']}")
    print(f"  derived_from          : {result['derived_from']}")
    print(f"  members ({len(result['members'])}):")
    for member in result["members"]:
        marker = " <-- queried node" if member == adg_name else ""
        print(f"    {member}{marker}")

    if result["stale"]:
        return 2
    return 0


def _cmd_violations(
    backend: GraphProjectionBackend,
    layer: str | None,
    severity: str | None,
    limit: int,
) -> int:
    if not backend.is_available():
        print("ERROR: projection unavailable — cannot query violations")
        return 1

    rows = backend.get_violations_with_impact(layer=layer, severity=severity, limit=limit)

    filters = []
    if layer:
        filters.append(f"layer={layer}")
    if severity:
        filters.append(f"severity={severity}")
    filter_str = f" [{', '.join(filters)}]" if filters else ""

    print(f"=== Violations with Impact{filter_str} (limit={limit}) ===")
    if not rows:
        print("  (no violations found matching filters)")
        if backend.is_stale():
            return 2
        return 0

    col_w = 45
    print(
        f"  {'SEVERITY':<8}  {'BLAST':>5}  {'FROM':<{col_w}}  {'TO':<{col_w}}  {'DISPOSITION':<12}  FILE:LINE"
    )
    print("  " + "-" * (8 + 5 + col_w * 2 + 12 + 20 + 10))
    for row in tqdm(rows, desc="violations", leave=False, disable=True):
        from_short = (
            row["adg_name_from"][-col_w:] if len(row["adg_name_from"]) > col_w else row["adg_name_from"]
        )
        to_short = row["adg_name_to"][-col_w:] if len(row["adg_name_to"]) > col_w else row["adg_name_to"]
        file_short = row["source_file"][-35:] if len(row["source_file"]) > 35 else row["source_file"]
        print(
            f"  {row['severity']:<8}  {row['blast_radius_direct']:>5}  "
            f"{from_short:<{col_w}}  {to_short:<{col_w}}  "
            f"{row['disposition']:<12}  {file_short}:{row['line_no']}"
        )

    if backend.is_stale():
        print("\nWARNING: projection is stale — results may not reflect current canonical state.")
        return 2
    return 0


def _cmd_diff(
    backend: GraphProjectionBackend,
    metric: str | None,
) -> int:
    """Read proj_diff directly from the projection sqlite.

    GraphProjectionBackend does not expose a get_diff() method (deferred to a later
    increment), so this command performs a minimal local sqlite read using the
    projection_path reported by get_status(). All reads are read-only.
    """
    if not backend.is_available():
        print("ERROR: projection unavailable — cannot query diff")
        return 1

    status = backend.get_status()
    proj_path_str = status.get("projection_path")
    if not proj_path_str:
        print("ERROR: projection path not available from status")
        return 1

    proj_path = Path(proj_path_str)
    if not proj_path.exists():
        print(f"ERROR: projection file not found: {proj_path}")
        return 1

    try:
        conn = sqlite3.connect(str(proj_path), timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only = ON")

        if metric:
            rows = conn.execute(
                "SELECT adg_name, metric, prev_value, curr_value, delta, delta_pct, direction, layer "
                "FROM proj_diff WHERE metric = ? AND direction != 'unchanged' "
                "ORDER BY ABS(delta) DESC",
                (metric,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT adg_name, metric, prev_value, curr_value, delta, delta_pct, direction, layer "
                "FROM proj_diff WHERE direction != 'unchanged' "
                "ORDER BY ABS(delta) DESC "
                "LIMIT 100",
            ).fetchall()

        total_rows = conn.execute("SELECT COUNT(*) FROM proj_diff").fetchone()[0]
        conn.close()
    except sqlite3.Error as exc:
        print(f"ERROR: could not read proj_diff: {exc}")
        return 1

    metric_str = f" [metric={metric}]" if metric else ""
    print(f"=== Cross-run Metric Diff{metric_str} ===")
    print(f"  Total proj_diff rows  : {total_rows}")

    if not rows:
        print("  (no changed metrics found)")
        if backend.is_stale():
            return 2
        return 0

    print(f"\n  {'METRIC':<25}  {'DIRECTION':<10}  {'PREV':>8}  {'CURR':>8}  {'DELTA':>8}  {'PCT':>7}  NODE")
    print("  " + "-" * 100)
    for row in rows:
        node_short = row["adg_name"][-55:] if len(row["adg_name"]) > 55 else row["adg_name"]
        print(
            f"  {row['metric']:<25}  {row['direction']:<10}  "
            f"{row['prev_value']:>8.1f}  {row['curr_value']:>8.1f}  "
            f"{row['delta']:>+8.1f}  {row['delta_pct']:>6.1f}%  {node_short}"
        )

    if backend.is_stale():
        print("\nWARNING: projection is stale — diff may not reflect current canonical state.")
        return 2
    return 0


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="adg_graph_query",
        description="Query the ADG derived graph projection (adg_graph_<ts>.sqlite).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exit codes: 0=success  1=unavailable  2=stale\n\n"
            "Examples:\n"
            "  python tools/adg/adg_graph_query.py status\n"
            "  python tools/adg/adg_graph_query.py blast-radius "
            '"ADG::Module::agentic_core/__init__" --hops 2\n'
            "  python tools/adg/adg_graph_query.py scc "
            '"ADG::Module::tools/adg/core/sqlite_backend"\n'
            "  python tools/adg/adg_graph_query.py violations --severity HIGH --limit 20\n"
            "  python tools/adg/adg_graph_query.py diff --metric blast_radius_direct\n"
        ),
    )

    sub = parser.add_subparsers(dest="command", metavar="SUBCOMMAND")
    sub.required = True

    sub.add_parser("status", help="Show projection availability and metadata")

    p_blast = sub.add_parser(
        "blast-radius",
        help="Print blast-radius counts for a node",
    )
    p_blast.add_argument("adg_name", help="Stable ADG node name (e.g. ADG::Module::path/to/module)")
    p_blast.add_argument("--hops", type=int, default=2, help="Hop depth (default: 2)")

    p_scc = sub.add_parser(
        "scc",
        help="Print SCC membership for a node",
    )
    p_scc.add_argument("adg_name", help="Stable ADG node name")

    p_viol = sub.add_parser(
        "violations",
        help="List violations sorted by blast-radius impact",
    )
    p_viol.add_argument("--layer", default=None, help="Filter by layer prefix (e.g. L0, L3)")
    p_viol.add_argument("--severity", default=None, help="Filter by severity (HIGH, MEDIUM, LOW)")
    p_viol.add_argument("--limit", type=int, default=100, help="Max rows to print (default: 100)")

    p_diff = sub.add_parser(
        "diff",
        help="Show cross-run metric deltas from proj_diff",
    )
    p_diff.add_argument(
        "--metric",
        default=None,
        choices=list(_DIFF_ALL_METRICS),
        help="Filter to a single metric (default: all changed metrics)",
    )

    return parser


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    backend = GraphProjectionBackend()

    try:
        if args.command == "status":
            return _cmd_status(backend)

        if args.command == "blast-radius":
            return _cmd_blast_radius(backend, args.adg_name, args.hops)

        if args.command == "scc":
            return _cmd_scc(backend, args.adg_name)

        if args.command == "violations":
            return _cmd_violations(backend, args.layer, args.severity, args.limit)

        if args.command == "diff":
            return _cmd_diff(backend, args.metric)

        parser.print_help()
        return 1

    finally:
        backend.close()


if __name__ == "__main__":
    sys.exit(main())
