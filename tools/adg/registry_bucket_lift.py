"""Registry bucket lift — port registry-resolver edges into the unified ADG.

Per the 2026-04-29 three-bucket authority model (W3): registry evidence
(MCP server configs, agent spec catalogs, route-contract YAMLs) is owned
by per-source resolvers in
``agentic_core.adg.registry.registry_resolvers``.

This script invokes those resolvers and INSERTs their edges into the
canonical static ADG snapshot's ``edges`` table with:

    bucket            = 'registry'
    resolution_status = STABLE_REGISTRY / DISABLED_REGISTRY / ...
    authority_status  = AUTHORITATIVE_REGISTRY / RISK_SIGNAL_ONLY / ...
    authority         = 'registry_declared' (registry-bucket back-compat)
    evidence_refs     = JSON {registry_path, registry_digest, declaration_key, ...}

Idempotency: dedup is keyed by (src_id, dst_id, relation_type,
source_file, authority='registry_declared') so repeated runs do not
duplicate rows.

Usage:

    python tools/adg/registry_bucket_lift.py
        [--static-snapshot artifacts/adg/adg_indexed_<ts>.sqlite]
        [--dry-run]
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.adg.registry.registry_resolvers import (  # noqa: E402
    RegistryEdge,
    resolve_all_registries,
)
from agentic_core.adg.registry.registry_consumer_resolver import (  # noqa: E402
    consumer_edge_to_registry_edges,
    resolve_all_consumer_edges,
)


@dataclass
class LiftStats:
    edges_resolved: int = 0
    nodes_stubbed: int = 0
    edges_inserted: int = 0
    edges_skipped_duplicate: int = 0
    consumer_edges_inserted: int = 0
    by_resolution_status: dict[str, int] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.by_resolution_status is None:
            self.by_resolution_status = {}


def _latest_static_snapshot() -> Path | None:
    candidates = sorted((REPO_ROOT / "artifacts" / "adg").glob("adg_indexed_*.sqlite"))
    return candidates[-1] if candidates else None


def _ensure_static_node(con: sqlite3.Connection, *, adg_name: str) -> int:
    """Ensure a node row exists for ``adg_name``; return its id.

    Populates the 5 NOT NULL columns required by the canonical ``nodes``
    schema (``adg_name``, ``entity_type``, ``layer``, ``identity_kind``,
    ``confidence``, ``resolved_path``) with sensible defaults for
    registry-virtual nodes:

        entity_type='registry_node'  — synthetic, not a Python construct
        layer='L_REGISTRY'           — registry surface (declarative)
        identity_kind='virtual'      — synthetic root, not a real symbol
        confidence='HIGH'            — declarative source = authoritative
        resolved_path=''             — virtual nodes have no file path
    """
    row = con.execute("SELECT id FROM nodes WHERE adg_name = ?", (adg_name,)).fetchone()
    if row is not None:
        return int(row[0])
    cur = con.execute(
        """
        INSERT INTO nodes (
            adg_name, entity_type, layer, identity_kind, confidence, resolved_path
        ) VALUES (?, 'registry_node', 'L_REGISTRY', 'virtual', 'HIGH', '')
        """,
        (adg_name,),
    )
    return int(cur.lastrowid or 0)


def _registry_edge_exists(
    con: sqlite3.Connection,
    *,
    src_id: int,
    dst_id: int,
    relation_type: str,
    source_file: str,
) -> bool:
    row = con.execute(
        """
        SELECT 1 FROM edges
        WHERE src_id = ?
          AND dst_id = ?
          AND relation_type = ?
          AND source_file = ?
          AND authority = 'registry_declared'
        LIMIT 1
        """,
        (src_id, dst_id, relation_type, source_file),
    ).fetchone()
    return row is not None


def _consumer_edge_exists(
    con: sqlite3.Connection,
    *,
    src_id: int,
    dst_id: int,
    relation_type: str,
    bucket: str,
    authority: str,
) -> bool:
    """Dedup check for consumer-edge pairs (static + registry twins)."""
    row = con.execute(
        """
        SELECT 1 FROM edges
        WHERE src_id = ?
          AND dst_id = ?
          AND relation_type = ?
          AND bucket = ?
          AND authority = ?
        LIMIT 1
        """,
        (src_id, dst_id, relation_type, bucket, authority),
    ).fetchone()
    return row is not None


def lift(
    *,
    static_snapshot: Path,
    dry_run: bool = False,
    edges: list[RegistryEdge] | None = None,
    include_consumer_edges: bool = True,
) -> LiftStats:
    """Lift registry edges into the static snapshot.

    Args:
        static_snapshot: path to the canonical static ADG SQLite.
        dry_run:         if True, transaction is rolled back.
        edges:           optional pre-resolved edge list (used by tests).
                         When None, ``resolve_all_registries()`` is called.
        include_consumer_edges:
                         when True (default), also call
                         ``resolve_all_consumer_edges()`` and emit
                         (consumer, registry_anchor) twin edges
                         (bucket='static' + bucket='registry') so the
                         gap classifier can score them as TRIPLET_ATTESTED
                         once the runtime bucket also attests.
    """
    if not static_snapshot.exists():
        raise FileNotFoundError(f"static snapshot not found: {static_snapshot}")

    if edges is None:
        edges = resolve_all_registries()

    stats = LiftStats(edges_resolved=len(edges), by_resolution_status={})

    con = sqlite3.connect(static_snapshot)
    try:
        for edge in edges:
            stats.by_resolution_status[edge.resolution_status] = (
                stats.by_resolution_status.get(edge.resolution_status, 0) + 1
            )

            src_before = con.execute(
                "SELECT id FROM nodes WHERE adg_name = ?", (edge.src_name,)
            ).fetchone()
            dst_before = con.execute(
                "SELECT id FROM nodes WHERE adg_name = ?", (edge.dst_name,)
            ).fetchone()

            src_id = _ensure_static_node(con, adg_name=edge.src_name)
            dst_id = _ensure_static_node(con, adg_name=edge.dst_name)
            if src_before is None:
                stats.nodes_stubbed += 1
            if dst_before is None:
                stats.nodes_stubbed += 1

            if _registry_edge_exists(
                con,
                src_id=src_id,
                dst_id=dst_id,
                relation_type=edge.relation_type,
                source_file=edge.source_file,
            ):
                stats.edges_skipped_duplicate += 1
                continue

            con.execute(
                """
                INSERT INTO edges (
                    src_id, dst_id, relation_type, edge_kind,
                    source_file, line_no, symbol,
                    authority, bucket, resolution_status, authority_status, evidence_refs
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'registry_declared', 'registry', ?, ?, ?)
                """,
                (
                    src_id,
                    dst_id,
                    edge.relation_type,
                    edge.edge_kind,
                    edge.source_file,
                    edge.line_no,
                    edge.symbol,
                    edge.resolution_status,
                    edge.authority_status,
                    edge.evidence_refs_json(),
                ),
            )
            stats.edges_inserted += 1

        # Consumer edges — bucket-aware INSERT for the (static, registry)
        # twin pairs. Each ConsumerEdge produces 2 RegistryEdges with
        # different `bucket` values; we route to authority='static_canonical'
        # for bucket='static' twins and authority='registry_declared' for
        # bucket='registry' twins.
        if include_consumer_edges:
            consumer_edges_raw = resolve_all_consumer_edges()
            for consumer in consumer_edges_raw:
                twins = consumer_edge_to_registry_edges(consumer)
                for twin in twins:
                    src_id = _ensure_static_node(con, adg_name=twin.src_name)
                    dst_id = _ensure_static_node(con, adg_name=twin.dst_name)
                    authority = (
                        "static_canonical" if twin.bucket == "static"
                        else "registry_declared"
                    )
                    if _consumer_edge_exists(
                        con,
                        src_id=src_id,
                        dst_id=dst_id,
                        relation_type=twin.relation_type,
                        bucket=twin.bucket,
                        authority=authority,
                    ):
                        stats.edges_skipped_duplicate += 1
                        continue
                    con.execute(
                        """
                        INSERT INTO edges (
                            src_id, dst_id, relation_type, edge_kind,
                            source_file, line_no, symbol,
                            authority, bucket, resolution_status, authority_status, evidence_refs
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            src_id,
                            dst_id,
                            twin.relation_type,
                            twin.edge_kind,
                            twin.source_file,
                            twin.line_no,
                            twin.symbol,
                            authority,
                            twin.bucket,
                            twin.resolution_status,
                            twin.authority_status,
                            twin.evidence_refs_json(),
                        ),
                    )
                    stats.consumer_edges_inserted += 1

        if dry_run:
            con.rollback()
        else:
            con.commit()
    finally:
        con.close()

    return stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--static-snapshot",
        type=Path,
        default=None,
        help="Path to static ADG SQLite (default: latest under artifacts/adg/)",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    static_snap = args.static_snapshot or _latest_static_snapshot()
    if static_snap is None:
        print("[FATAL] no static ADG snapshot found", file=sys.stderr)
        return 2

    print(f"[INFO] static snapshot: {static_snap}")
    print(f"[INFO] dry_run={args.dry_run}")

    stats = lift(static_snapshot=static_snap, dry_run=args.dry_run)

    print(f"[OK] edges_resolved          = {stats.edges_resolved}")
    print(f"[OK] nodes_stubbed           = {stats.nodes_stubbed}")
    print(f"[OK] edges_inserted          = {stats.edges_inserted}")
    print(f"[OK] consumer_edges_inserted = {stats.consumer_edges_inserted}")
    print(f"[OK] edges_skipped_duplicate = {stats.edges_skipped_duplicate}")
    print("[OK] by_resolution_status:")
    for k in sorted(stats.by_resolution_status):
        print(f"       {k:30s} = {stats.by_resolution_status[k]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
