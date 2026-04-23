"""Emit ``SymbolCard`` documents from ADG ``nodes`` + ``mv_hotspot_centrality``.

One card per node that has any fan-in or fan-out (nodes with zero degree add
no retrieval signal). The document is a compact prose summary; structural
metadata is carried alongside for reranking.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from pathlib import Path

from tools.ingestion.adg_cards._helpers import (
    adg_conn,
    read_snapshot_id,
    surface_for,
)
from tools.ingestion.adg_cards.types import SymbolCard, coerce_metadata

# SQL keeps all heavy lifting in SQLite — join nodes with mv_hotspot_centrality so
# each row already carries degree metrics; LEFT JOIN so isolated nodes are dropped
# by the WHERE clause rather than silently missing.
_SYMBOL_SQL = """
SELECT
    n.id                AS node_id,
    n.adg_name          AS adg_name,
    n.entity_type       AS entity_type,
    n.layer             AS layer,
    n.resolved_path     AS resolved_path,
    n.precision_type    AS precision_type,
    n.enclosing_symbol  AS enclosing_symbol,
    COALESCE(m.fan_in,  0) AS fan_in,
    COALESCE(m.fan_out, 0) AS fan_out,
    COALESCE(m.degree,  0) AS degree,
    COALESCE(m.degree_centrality,  0.0) AS degree_centrality,
    COALESCE(m.betweenness_approx, 0.0) AS betweenness_approx
FROM nodes n
LEFT JOIN mv_hotspot_centrality m
    ON m.node_id = n.id
WHERE COALESCE(m.degree, 0) > 0
  AND n.adg_name IS NOT NULL
  AND n.adg_name != ''
"""


def _describe(row: sqlite3.Row) -> str:
    """Prose description that reads naturally for embedding."""

    name = row["adg_name"]
    kind = row["entity_type"] or "symbol"
    layer = row["layer"] or "unknown-layer"
    path = row["resolved_path"] or "(no path)"
    fan_in = row["fan_in"]
    fan_out = row["fan_out"]
    parts = [
        f"{kind} {name!r} in layer {layer} at {path}.",
        f"Has {fan_in} incoming and {fan_out} outgoing structural edges.",
    ]
    if row["enclosing_symbol"]:
        parts.append(f"Enclosed by {row['enclosing_symbol']!r}.")
    if row["precision_type"]:
        parts.append(f"Precision type: {row['precision_type']}.")
    return " ".join(parts)


def emit_symbol_cards(
    adg_db_path: str | Path,
    *,
    limit: int | None = None,
) -> Iterator[SymbolCard]:
    """Yield ``SymbolCard`` objects from the given ADG snapshot.

    Args:
        adg_db_path: path to ``artifacts/adg/adg_indexed_<ts>.sqlite``.
        limit: optional cap for smoke tests.
    """

    sql = _SYMBOL_SQL
    if limit is not None:
        sql = f"{sql}\nLIMIT {int(limit)}"

    with adg_conn(adg_db_path) as conn:
        snapshot_id = read_snapshot_id(conn)
        cur = conn.execute(sql)
        for row in cur:
            fan_in = int(row["fan_in"])
            fan_out = int(row["fan_out"])
            metadata = coerce_metadata(
                {
                    "adg_node_id": row["node_id"],
                    "adg_name": row["adg_name"],
                    "entity_type": row["entity_type"],
                    "layer": row["layer"],
                    "resolved_path": row["resolved_path"],
                    "precision_type": row["precision_type"],
                    "enclosing_symbol": row["enclosing_symbol"],
                    "fan_in": fan_in,
                    "fan_out": fan_out,
                    "degree": int(row["degree"]),
                    "degree_centrality": float(row["degree_centrality"]),
                    "betweenness_approx": float(row["betweenness_approx"]),
                    "surface": surface_for(row["layer"]),
                    "snapshot_id": snapshot_id,
                }
            )
            yield SymbolCard(
                card_id=f"n{row['node_id']}",
                document=_describe(row),
                metadata=metadata,
                snapshot_id=snapshot_id,
            )
