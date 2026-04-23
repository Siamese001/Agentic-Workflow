"""Emit ``ViolationCard`` documents from ``violations`` joined with exemption
proximity (``mv_exemptions_near_critical_paths``).

One card per violation. ``severity`` and ``violation_class`` are carried on
metadata so downstream retrieval can boost safety-critical hits.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from pathlib import Path

from tools.ingestion.adg_cards._helpers import adg_conn, read_snapshot_id
from tools.ingestion.adg_cards.types import ViolationCard, coerce_metadata

_VIOLATION_SQL = """
SELECT
    v.id                    AS violation_id,
    v.edge_id               AS edge_id,
    v.category              AS category,
    v.evidence              AS evidence,
    v.file_path             AS file_path,
    v.line_no               AS line_no,
    v.disposition           AS disposition,
    v.disposition_source    AS disposition_source,
    v.severity              AS severity,
    v.violation_class       AS violation_class,
    COALESCE(e.criticality_score, 0.0) AS criticality_score,
    COALESCE(e.proximity_flag, 0)      AS proximity_flag,
    e.exemption_kind         AS exemption_kind
FROM violations v
LEFT JOIN mv_exemptions_near_critical_paths e
    ON e.edge_id = v.edge_id
"""


def _describe(row: sqlite3.Row) -> str:
    category = row["category"] or "unknown"
    severity = row["severity"] or "unknown"
    vclass = row["violation_class"] or "unspecified"
    path = row["file_path"] or "(no file)"
    line = row["line_no"] or 0
    parts = [
        f"Violation category={category} severity={severity} class={vclass} at {path}:{line}.",
    ]
    if row["evidence"]:
        parts.append(f"Evidence: {row['evidence']}.")
    if row["disposition"]:
        parts.append(f"Disposition: {row['disposition']} (source={row['disposition_source'] or 'n/a'}).")
    if row["exemption_kind"]:
        parts.append(
            f"Exempted via {row['exemption_kind']} near critical path"
            f" (criticality {row['criticality_score']:.2f})."
        )
    return " ".join(parts)


def emit_violation_cards(
    adg_db_path: str | Path,
    *,
    limit: int | None = None,
) -> Iterator[ViolationCard]:
    """Yield ``ViolationCard`` objects, one per row in ``violations``."""

    sql = _VIOLATION_SQL
    if limit is not None:
        sql = f"{sql}\nLIMIT {int(limit)}"

    with adg_conn(adg_db_path) as conn:
        snapshot_id = read_snapshot_id(conn)
        cur = conn.execute(sql)
        for row in cur:
            metadata = coerce_metadata(
                {
                    "violation_id": row["violation_id"],
                    "edge_id": row["edge_id"],
                    "category": row["category"],
                    "severity": row["severity"],
                    "violation_class": row["violation_class"],
                    "file_path": row["file_path"],
                    "line_no": row["line_no"],
                    "disposition": row["disposition"],
                    "disposition_source": row["disposition_source"],
                    "exemption_kind": row["exemption_kind"],
                    "criticality_score": float(row["criticality_score"]),
                    "proximity_flag": int(row["proximity_flag"]),
                    "snapshot_id": snapshot_id,
                }
            )
            yield ViolationCard(
                card_id=f"v{row['violation_id']}",
                document=_describe(row),
                metadata=metadata,
                snapshot_id=snapshot_id,
            )
