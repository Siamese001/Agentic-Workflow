"""Emit ``HotspotCard`` documents from hotspot + debt + cone-risk MVs.

One card per hotspot row, joining ``mv_hotspot_centrality`` with
``mv_dependency_cone_risk`` and ``mv_debt_concentration_hotspots`` so each
card carries centrality, cone-risk, and debt in a single document.

Every card carries an archetype classification (CENTRAL_DEPENDENCY |
ORCHESTRATOR | STATE_NODE | SAFETY_GATEKEEPER) per the canonical ADG
invariants.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from pathlib import Path

from tools.ingestion.adg_cards._helpers import (
    adg_conn,
    archetype_for,
    impact_score,
    layer_multiplier,
    read_snapshot_id,
    surface_for,
)
from tools.ingestion.adg_cards.types import HotspotCard, coerce_metadata

_HOTSPOT_SQL = """
SELECT
    h.node_id                                    AS node_id,
    h.adg_name                                   AS adg_name,
    h.layer                                      AS layer,
    h.resolved_path                              AS resolved_path,
    h.fan_in                                     AS fan_in,
    h.fan_out                                    AS fan_out,
    h.degree                                     AS degree,
    h.degree_centrality                          AS degree_centrality,
    h.betweenness_approx                         AS betweenness_approx,
    COALESCE(c.cone_risk_score, 0.0)             AS cone_risk_score,
    COALESCE(c.transitive_depth_approx, 0)       AS transitive_depth_approx,
    COALESCE(d.total_violations, 0)              AS total_violations,
    COALESCE(d.total_debt_score, 0.0)            AS total_debt_score,
    COALESCE(d.p0_count, 0)                      AS p0_count,
    COALESCE(d.p1_count, 0)                      AS p1_count
FROM mv_hotspot_centrality h
LEFT JOIN mv_dependency_cone_risk c
    ON c.node_id = h.node_id
LEFT JOIN mv_debt_concentration_hotspots d
    ON d.file = h.resolved_path
WHERE h.degree >= 5
ORDER BY h.degree DESC
"""


def _describe(row: sqlite3.Row, archetype: str, impact: float) -> str:
    name = row["adg_name"] or f"node-{row['node_id']}"
    layer = row["layer"] or "unknown-layer"
    path = row["resolved_path"] or "(no path)"
    parts = [
        f"Hotspot {name!r} ({archetype}) in layer {layer} at {path}.",
        f"Fan-in {row['fan_in']}, fan-out {row['fan_out']}, degree {row['degree']}.",
        f"Cone risk {row['cone_risk_score']:.2f}, transitive depth approx {row['transitive_depth_approx']}.",
        f"Debt score {row['total_debt_score']:.2f} across {row['total_violations']} violations"
        f" (P0={row['p0_count']}, P1={row['p1_count']}).",
        f"Constitutional impact score {impact:.2f}.",
    ]
    return " ".join(parts)


def emit_hotspot_cards(
    adg_db_path: str | Path,
    *,
    limit: int | None = None,
) -> Iterator[HotspotCard]:
    """Yield ``HotspotCard`` objects ordered by structural degree."""

    sql = _HOTSPOT_SQL
    if limit is not None:
        sql = f"{sql}\nLIMIT {int(limit)}"

    with adg_conn(adg_db_path) as conn:
        snapshot_id = read_snapshot_id(conn)
        cur = conn.execute(sql)
        for row in cur:
            fan_in = int(row["fan_in"])
            fan_out = int(row["fan_out"])
            layer = row["layer"]
            archetype = archetype_for(layer, fan_in, fan_out)
            impact = impact_score(
                int(row["total_violations"]) or 1,  # baseline weight even when no violations
                fan_in,
                layer,
            )
            metadata = coerce_metadata(
                {
                    "adg_node_id": row["node_id"],
                    "adg_name": row["adg_name"],
                    "layer": layer,
                    "resolved_path": row["resolved_path"],
                    "fan_in": fan_in,
                    "fan_out": fan_out,
                    "degree": int(row["degree"]),
                    "degree_centrality": float(row["degree_centrality"]),
                    "betweenness_approx": float(row["betweenness_approx"]),
                    "cone_risk_score": float(row["cone_risk_score"]),
                    "transitive_depth_approx": int(row["transitive_depth_approx"]),
                    "total_violations": int(row["total_violations"]),
                    "total_debt_score": float(row["total_debt_score"]),
                    "p0_count": int(row["p0_count"]),
                    "p1_count": int(row["p1_count"]),
                    "archetype": archetype,
                    "surface": surface_for(layer),
                    "layer_multiplier": layer_multiplier(layer),
                    "impact_score": impact,
                    "snapshot_id": snapshot_id,
                }
            )
            yield HotspotCard(
                card_id=f"n{row['node_id']}",
                document=_describe(row, archetype, impact),
                metadata=metadata,
                snapshot_id=snapshot_id,
            )
