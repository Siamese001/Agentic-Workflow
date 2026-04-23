"""Emit ``PathCard`` documents from structural path MVs.

Two path kinds are surfaced:

- ``gateway_bypass`` — rows from ``mv_gateway_bypass_paths`` (authority-escape paths).
- ``chokepoint_bridge`` — rows from ``mv_graph_chokepoint_bridges`` (structural bridges
  whose removal partitions the graph).

Both are rare by design; emitting them as first-class semantic cards keeps
safety-critical topology retrievable by natural-language query.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from pathlib import Path

from tools.ingestion.adg_cards._helpers import adg_conn, read_snapshot_id, surface_for
from tools.ingestion.adg_cards.types import PathCard, coerce_metadata

_BYPASS_SQL = """
SELECT
    snapshot_id,
    edge_id,
    src_file,
    src_layer,
    provider_symbol,
    source_file,
    line_no,
    bypass_type
FROM mv_gateway_bypass_paths
"""

_BRIDGE_SQL = """
SELECT
    snapshot_id,
    node_id,
    file_path,
    layer,
    fan_in,
    fan_out,
    bridge_score,
    imbalance_ratio,
    bridge_type
FROM mv_graph_chokepoint_bridges
"""


def _describe_bypass(row: sqlite3.Row) -> str:
    return (
        f"Gateway bypass path ({row['bypass_type'] or 'unspecified'}) from layer"
        f" {row['src_layer'] or 'unknown'} at {row['src_file'] or '(no file)'}"
        f" via provider {row['provider_symbol'] or '(none)'}; observed in"
        f" {row['source_file'] or '(no file)'}:{row['line_no'] or 0}."
    )


def _describe_bridge(row: sqlite3.Row) -> str:
    return (
        f"Chokepoint bridge ({row['bridge_type'] or 'structural'}) in layer"
        f" {row['layer'] or 'unknown'} at {row['file_path'] or '(no file)'}."
        f" Fan-in {row['fan_in']}, fan-out {row['fan_out']},"
        f" bridge score {row['bridge_score']:.2f}, imbalance {row['imbalance_ratio']:.2f}."
    )


def _emit_bypasses(conn: sqlite3.Connection, snapshot_id: str, limit: int | None) -> Iterator[PathCard]:
    sql = _BYPASS_SQL if limit is None else f"{_BYPASS_SQL}\nLIMIT {int(limit)}"
    for row in conn.execute(sql):
        metadata = coerce_metadata(
            {
                "path_kind": "gateway_bypass",
                "edge_id": row["edge_id"],
                "bypass_type": row["bypass_type"],
                "src_file": row["src_file"],
                "src_layer": row["src_layer"],
                "provider_symbol": row["provider_symbol"],
                "source_file": row["source_file"],
                "line_no": row["line_no"],
                "surface": surface_for(row["src_layer"]),
                "snapshot_id": snapshot_id,
            }
        )
        yield PathCard(
            card_id=f"bypass-{row['edge_id']}",
            document=_describe_bypass(row),
            metadata=metadata,
            snapshot_id=snapshot_id,
        )


def _emit_bridges(conn: sqlite3.Connection, snapshot_id: str, limit: int | None) -> Iterator[PathCard]:
    sql = _BRIDGE_SQL if limit is None else f"{_BRIDGE_SQL}\nLIMIT {int(limit)}"
    for row in conn.execute(sql):
        metadata = coerce_metadata(
            {
                "path_kind": "chokepoint_bridge",
                "adg_node_id": row["node_id"],
                "bridge_type": row["bridge_type"],
                "file_path": row["file_path"],
                "layer": row["layer"],
                "fan_in": int(row["fan_in"]),
                "fan_out": int(row["fan_out"]),
                "bridge_score": float(row["bridge_score"]),
                "imbalance_ratio": float(row["imbalance_ratio"]),
                "surface": surface_for(row["layer"]),
                "snapshot_id": snapshot_id,
            }
        )
        yield PathCard(
            card_id=f"bridge-n{row['node_id']}",
            document=_describe_bridge(row),
            metadata=metadata,
            snapshot_id=snapshot_id,
        )


def emit_path_cards(
    adg_db_path: str | Path,
    *,
    limit: int | None = None,
) -> Iterator[PathCard]:
    """Yield ``PathCard`` objects for bypasses and chokepoint bridges.

    ``limit`` is applied per source table (so ``limit=5`` yields up to 5 bypasses
    plus up to 5 bridges).
    """

    with adg_conn(adg_db_path) as conn:
        snapshot_id = read_snapshot_id(conn)
        yield from _emit_bypasses(conn, snapshot_id, limit)
        yield from _emit_bridges(conn, snapshot_id, limit)
