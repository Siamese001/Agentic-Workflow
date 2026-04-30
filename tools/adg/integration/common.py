"""Shared helpers for ADG integration ingesters.

Provides:
  - latest_snapshot()  : resolve the canonical (non-sentinel) ADG SQLite snapshot
  - ensure_node()      : get-or-create a node for a given resolved_path
  - insert_edge_idempotent(): dedup-safe edge insertion
  - bulk_insert_edges(): batch-friendly insertion with progress display
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from pathlib import Path
from typing import Any


def latest_snapshot(adg_dir: Path | None = None) -> Path:
    """Return the most recent canonical ADG snapshot (excluding 99999999 sentinel)."""
    base = adg_dir or Path("artifacts/adg")
    candidates = sorted(
        p for p in base.glob("adg_indexed_*.sqlite") if "99999999" not in p.name
    )
    if not candidates:
        raise FileNotFoundError(f"No ADG snapshot found in {base}")
    return candidates[-1]


def ensure_node(
    cur: sqlite3.Cursor,
    resolved_path: str,
    *,
    layer: str = "L_UNKNOWN",
    entity_type: str = "module",
) -> int:
    """Return node id for resolved_path, creating a stub if needed.

    Stub nodes carry adg_name=resolved_path, kind='module'. This is intentional
    for runtime-only artifacts (OTel spans, profiler pairs) whose call sites
    may not have been parsed by the static scanner.
    """
    row = cur.execute(
        "SELECT id FROM nodes WHERE resolved_path = ? LIMIT 1", (resolved_path,)
    ).fetchone()
    if row:
        return int(row[0])
    cur.execute(
        """
        INSERT INTO nodes (adg_name, entity_type, layer, identity_kind, confidence, resolved_path)
        VALUES (?, ?, ?, 'integration_stub', 0.5, ?)
        """,
        (resolved_path, entity_type, layer, resolved_path),
    )
    return int(cur.lastrowid)


def insert_edge_idempotent(
    cur: sqlite3.Cursor,
    *,
    src_id: int,
    dst_id: int,
    relation_type: str,
    source_file: str = "",
    line_no: int = 0,
    symbol: str = "",
    semantic_type: str = "runtime",
    authority: str = "runtime",
    bucket: str = "integration",
    resolution_status: str = "resolved",
    authority_status: str = "asserted",
) -> bool:
    """Insert edge if (src,dst,relation_type,line_no) tuple absent. Returns True if inserted."""
    existing = cur.execute(
        """
        SELECT id FROM edges
        WHERE src_id = ? AND dst_id = ? AND relation_type = ? AND line_no = ?
        LIMIT 1
        """,
        (src_id, dst_id, relation_type, line_no),
    ).fetchone()
    if existing:
        return False
    cur.execute(
        """
        INSERT INTO edges (
            src_id, dst_id, relation_type, edge_kind,
            source_file, line_no, symbol, semantic_type,
            confidence_score, authority, bucket,
            resolution_status, authority_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            src_id,
            dst_id,
            relation_type,
            "runtime",
            source_file,
            line_no,
            symbol,
            semantic_type,
            1.0,
            authority,
            bucket,
            resolution_status,
            authority_status,
        ),
    )
    return True


def bulk_insert_edges(
    sqlite_path: Path,
    edges: Iterable[dict[str, Any]],
    *,
    relation_type: str,
    label: str = "ingest",
) -> int:
    """Insert many edges idempotently. Returns number actually inserted."""
    inserted = 0
    with sqlite3.connect(sqlite_path) as con:
        cur = con.cursor()
        for edge in edges:
            src = edge["src_path"]
            dst = edge["dst_path"]
            src_id = ensure_node(cur, src)
            dst_id = ensure_node(cur, dst)
            ok = insert_edge_idempotent(
                cur,
                src_id=src_id,
                dst_id=dst_id,
                relation_type=relation_type,
                source_file=edge.get("source_file", src),
                line_no=int(edge.get("line_no", 0)),
                symbol=edge.get("symbol", ""),
                semantic_type=edge.get("semantic_type", "runtime"),
                authority=edge.get("authority", "runtime"),
                bucket=edge.get("bucket", label),
            )
            if ok:
                inserted += 1
        con.commit()
    return inserted
