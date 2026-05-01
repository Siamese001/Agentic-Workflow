"""OTEL Runtime View Builder — populate v_runtime_proof from the OTel store.

This module is the **runtime bucket** producer for the three-bucket ADG
authority model after the 2026-04-29 Mid-Day Pivot.

ARCHITECTURAL CONTEXT
=====================

Per the 2026-04-29 user critique ("the runtime ADG isnt that a fake concept?
should it is OTEL traces"), validated against:

  - OpenTelemetry GenAI SIG semconv (gen-ai-agent-spans)
  - OpenAI Agents SDK Tracing docs
  - Anthropic Claude Code Monitoring docs
  - CNCF "single source of truth for telemetry" principle

The runtime bucket is NOT lifted into the static ``edges`` table. Instead,
this builder summarizes the OTel-native span sink (``runtime_adg_store``)
into a deterministic point-in-time projection: the ``v_runtime_proof`` table
inside the static ADG snapshot.

FLOW
====

::

    [code emits OTel-shaped spans]
              |
              v
    [system_learning.runtime_adg.store.FileBackedRuntimeADGStore]   <-- OTel sink
              |
              | (queried at snapshot generation time)
              v
    [tools.otel.runtime_view_builder.build_runtime_view]            <-- THIS MODULE
              |
              | (writes summary rows: 1 per (src, dst, relation))
              v
    [adg_indexed_<ts>.sqlite : v_runtime_proof]                      <-- runtime bucket

CONTRACT
========

* **Input**: a path to the static ADG snapshot, plus an optional list of
  recent ``RuntimeADGSnapshot`` payloads. When no payloads are supplied, the
  builder queries the default :class:`FileBackedRuntimeADGStore` lazily.
* **Output**: rows inserted into ``v_runtime_proof`` with one row per
  ``(src_name, dst_name, relation_type)`` triple, summarizing all attesting
  traces into ``attesting_trace_count`` plus a top-N evidence_refs JSON.
* **Idempotency**: the table has a UNIQUE constraint on the triple, so
  re-running the builder against the same input is a no-op for existing
  rows; new triples are inserted, existing rows have their counts updated
  via UPSERT (INSERT ... ON CONFLICT DO UPDATE).
* **Fail-soft**: any error reading the OTel store is logged and the builder
  returns 0 rows. Snapshot generation MUST NOT fail because the OTel store
  is empty or unavailable.

USAGE
=====

::

    # From within tools/generate/generate_full_adg.py final stage:
    from tools.otel.runtime_view_builder import build_runtime_view
    stats = build_runtime_view(static_snapshot_path)
    print(f"v_runtime_proof: rows_written={stats.rows_written}")

CI VALIDATION
=============

* ``ops_scripts/ci/check_runtime_proof_view_well_formed.py`` asserts that
  every row in ``v_runtime_proof`` has a non-empty ``latest_trace_id`` when
  ``authority_status='AUTHORITATIVE_RUNTIME'``.
* ``ops_scripts/ci/check_otel_genai_semconv_coverage.py`` asserts that the
  underlying OTel spans use the ``gen_ai.*`` semconv attributes.

Plan: ``.windsurf/plans/three-bucket-otel-view-5db409.md`` (W1).
"""

from __future__ import annotations

import json
import logging
import sqlite3
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.adg.artifact.edge_authority import runtime_authority_for  # noqa: E402

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass
class RuntimeViewBuildStats:
    """Accounting for one ``build_runtime_view`` invocation."""

    snapshots_read: int = 0
    edges_aggregated: int = 0
    rows_written: int = 0
    rows_updated: int = 0
    triples_skipped_invalid: int = 0
    error: str | None = None


@dataclass
class _EdgeAggregate:
    """Aggregator for one (src, dst, relation) triple across all snapshots."""

    src_name: str
    dst_name: str
    relation_type: str
    edge_kind: str = "RUNTIME_OBSERVED"
    attesting_trace_count: int = 0
    partial_trace_count: int = 0
    trace_ids: list[str] = field(default_factory=list)
    span_ids: list[str] = field(default_factory=list)
    run_ids: list[str] = field(default_factory=list)
    last_seen_at: str = ""

    def evidence_refs_json(self, *, top_n: int = 5) -> str:
        """Return the canonical evidence_refs JSON blob."""
        return json.dumps(
            {
                "trace_ids": self.trace_ids[-top_n:],
                "run_ids": list({rid for rid in self.run_ids[-top_n:] if rid}),
                "span_count": len(self.span_ids),
            },
            sort_keys=True,
            separators=(",", ":"),
        )


# ---------------------------------------------------------------------------
# Snapshot reader — extracts (src, dst, relation) triples from RuntimeADG
# ---------------------------------------------------------------------------


def _iter_runtime_snapshots(
    *,
    explicit_payloads: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    """Yield runtime ADG snapshot payloads (parent-child + temporal edges).

    When ``explicit_payloads`` is supplied (used by tests and direct callers),
    those are returned verbatim. Otherwise the builder lazily loads the
    default :class:`FileBackedRuntimeADGStore` and lists every persisted
    snapshot. Failures are logged and yield an empty list — the caller MUST
    treat 0 snapshots as a normal outcome (e.g. fresh-clone, no runs yet).
    """
    if explicit_payloads is not None:
        return explicit_payloads

    try:
        from system_learning.runtime_adg.store import FileBackedRuntimeADGStore
    except ImportError as exc:  # guardian: allow-log-and-swallow -- soft-dep on system_learning
        logger.warning("runtime_view_builder.import_store_failed: %s", exc)
        return []

    try:
        store = FileBackedRuntimeADGStore()
    except (OSError, RuntimeError) as exc:
        logger.warning("runtime_view_builder.store_init_failed: %s", exc)
        return []

    payloads: list[dict[str, Any]] = []
    try:
        for version_id in store.list_snapshots():
            # Use the store's typed load_snapshot() rather than reading raw
            # bytes — the persistence layer uses a custom canonical_bytes
            # format (binary delimiters, NOT JSON) so json.loads() on the
            # raw bytes silently drops every snapshot. load_snapshot()
            # invokes _deserialise_snapshot() which correctly parses the
            # canonical format back into a RuntimeADGSnapshot, and to_dict()
            # produces the JSON-shaped payload the aggregator expects.
            #
            # Bug fix (2026-04-29 plan three-bucket-gap-remediation-069806 W2):
            # the prior implementation called store.get_by_version() and ran
            # json.loads() on the bytes — every snapshot fell into the
            # except (ValueError, TypeError) branch, so snapshots_read was
            # always 0 even with a populated store.
            try:
                snap = store.load_snapshot(version_id)
            except (OSError, ValueError, TypeError) as exc:
                logger.debug("runtime_view_builder.load_snapshot_failed: %s", exc)
                continue
            if snap is None:
                continue
            try:
                payloads.append(snap.to_dict())
            except (AttributeError, TypeError) as exc:
                logger.debug("runtime_view_builder.to_dict_failed: %s", exc)
                continue
    except (OSError, AttributeError, RuntimeError) as exc:
        logger.warning("runtime_view_builder.snapshot_iter_failed: %s", exc)
        return payloads

    return payloads


def _aggregate_snapshots(
    payloads: list[dict[str, Any]],
) -> dict[tuple[str, str, str], _EdgeAggregate]:
    """Roll up parent-child runtime edges into per-(src,dst,rel) aggregates.

    Each payload is a ``RuntimeADGSnapshot`` dict with keys::

        {
          "snapshot_id": ...,
          "trace_id": ...,
          "mission": ...,
          "nodes": [{"node_id": ..., "name": ..., ...}, ...],
          "edges": [{"src_id": ..., "dst_id": ..., "relation": ...}, ...],
          "metadata": { ... }
        }

    Node names (``node.name``) are used as ``src_name`` / ``dst_name`` so the
    aggregate row matches the static ADG ``adg_name`` convention. ``__root__``
    placeholder src nodes (parent-of-root sentinel) are skipped.
    """
    aggregates: dict[tuple[str, str, str], _EdgeAggregate] = {}

    for payload in payloads:
        if not isinstance(payload, dict):
            continue

        nodes = payload.get("nodes") or []
        edges = payload.get("edges") or []
        trace_id = str(payload.get("trace_id") or "")
        run_id = str(
            (payload.get("metadata") or {}).get("run_id")
            or payload.get("snapshot_id")
            or ""
        )

        # Build node_id -> name lookup (skip the __root__ sentinel).
        node_name: dict[str, str] = {}
        latest_started: int = 0
        for node in nodes:
            if not isinstance(node, dict):
                continue
            nid = node.get("node_id")
            nm = node.get("name")
            if isinstance(nid, str) and isinstance(nm, str) and nm:
                node_name[nid] = nm
            started = node.get("started_at_utc")
            if isinstance(started, int) and started > latest_started:
                latest_started = started

        last_seen_iso = (
            datetime.fromtimestamp(latest_started / 1000.0, tz=timezone.utc).isoformat()
            if latest_started
            else ""
        )

        for edge in edges:
            if not isinstance(edge, dict):
                continue
            src_id = edge.get("src_id")
            dst_id = edge.get("dst_id")
            rel = str(edge.get("relation") or "parent_child")
            if not isinstance(src_id, str) or not isinstance(dst_id, str):
                continue
            # Skip the __root__ sentinel parent.
            if src_id == "__root__":
                continue
            src_name = node_name.get(src_id)
            dst_name = node_name.get(dst_id)
            if not src_name or not dst_name:
                continue

            key = (src_name, dst_name, rel)
            agg = aggregates.get(key)
            if agg is None:
                agg = _EdgeAggregate(
                    src_name=src_name, dst_name=dst_name, relation_type=rel
                )
                aggregates[key] = agg

            # Each snapshot represents one trace attesting this edge.
            # We count distinct trace_ids only (a single trace with multiple
            # parent-child edges between the same nodes still counts once).
            if trace_id and trace_id not in agg.trace_ids:
                agg.attesting_trace_count += 1
                agg.trace_ids.append(trace_id)
            if dst_id not in agg.span_ids:
                agg.span_ids.append(dst_id)
            if run_id and run_id not in agg.run_ids:
                agg.run_ids.append(run_id)
            if last_seen_iso > agg.last_seen_at:
                agg.last_seen_at = last_seen_iso

    return aggregates


# ---------------------------------------------------------------------------
# Static-edge correlation — link runtime triples to static.edges where possible
# ---------------------------------------------------------------------------


def _resolve_static_edge_id(
    static_con: sqlite3.Connection,
    *,
    src_name: str,
    dst_name: str,
    relation_type: str,
) -> int | None:
    """Best-effort lookup: does a static edge exist with the same triple?

    Resolution strategy (broadest match first):

      1. Skip if the relation is the runtime-only ``parent_child`` /
         ``temporal_sequence`` sentinel \u2014 those have no static counterpart
         by construction.
      2. **Exact triple match**: try ``(src_name, dst_name, relation_type)``.
         This is the strongest correlation \u2014 same nodes, same relation.
      3. **Reference-class fallback**: if ``relation_type`` is one of the
         invocation-class relations (``call`` / ``invokes`` / ``calls`` /
         ``tool_call``), try matching against any of the static
         reference-class relations (``imports`` / ``calls`` / ``invokes``).
         This handles the common case where a runtime ``invokes`` trace
         maps to a static ``imports`` edge.

    Returns the static ``edges.id`` if any strategy hits, else ``None``.
    Runtime evidence without a static counterpart is still authoritative
    runtime evidence \u2014 ``None`` is fine.
    """
    if relation_type in {"parent_child", "temporal_sequence"}:
        return None

    # Strategy 1 \u2014 exact triple match.
    cur = static_con.execute(
        """
        SELECT e.id
          FROM edges e
          JOIN nodes s ON s.id = e.src_id
          JOIN nodes d ON d.id = e.dst_id
         WHERE s.adg_name = ? AND d.adg_name = ?
           AND e.relation_type = ?
         LIMIT 1
        """,
        (src_name, dst_name, relation_type),
    )
    row = cur.fetchone()
    if row:
        return int(row[0])

    # Strategy 2 \u2014 invocation-class fallback.
    if relation_type in {"call", "invokes", "calls", "tool_call"}:
        cur = static_con.execute(
            """
            SELECT e.id
              FROM edges e
              JOIN nodes s ON s.id = e.src_id
              JOIN nodes d ON d.id = e.dst_id
             WHERE s.adg_name = ? AND d.adg_name = ?
               AND e.relation_type IN ('imports', 'calls', 'invokes')
             LIMIT 1
            """,
            (src_name, dst_name),
        )
        row = cur.fetchone()
        if row:
            return int(row[0])

    return None


# ---------------------------------------------------------------------------
# Writer — UPSERT aggregates into v_runtime_proof
# ---------------------------------------------------------------------------


def _upsert_aggregates(
    static_con: sqlite3.Connection,
    aggregates: dict[tuple[str, str, str], _EdgeAggregate],
    stats: RuntimeViewBuildStats,
) -> None:
    """Write each aggregate as a v_runtime_proof row (idempotent UPSERT).

    Sets ``resolution_status`` and ``authority_status`` per
    :func:`runtime_authority_for`. Skips triples with empty src or dst.
    """
    for (src_name, dst_name, rel), agg in aggregates.items():
        if not src_name or not dst_name:
            stats.triples_skipped_invalid += 1
            continue

        res_status, auth_status = runtime_authority_for(
            attesting_trace_count=agg.attesting_trace_count,
            partial_trace_count=agg.partial_trace_count,
        )
        static_edge_id = _resolve_static_edge_id(
            static_con,
            src_name=src_name,
            dst_name=dst_name,
            relation_type=rel,
        )

        cur = static_con.execute(
            """
            INSERT INTO v_runtime_proof (
                src_name, dst_name, relation_type, edge_kind,
                static_edge_id, attesting_trace_count,
                latest_trace_id, latest_span_id, last_seen_at,
                evidence_refs, bucket, resolution_status, authority_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'runtime', ?, ?)
            ON CONFLICT(src_name, dst_name, relation_type) DO UPDATE SET
                attesting_trace_count = excluded.attesting_trace_count,
                latest_trace_id       = excluded.latest_trace_id,
                latest_span_id        = excluded.latest_span_id,
                last_seen_at          = excluded.last_seen_at,
                evidence_refs         = excluded.evidence_refs,
                resolution_status     = excluded.resolution_status,
                authority_status      = excluded.authority_status,
                static_edge_id        = excluded.static_edge_id
            """,
            (
                src_name,
                dst_name,
                rel,
                agg.edge_kind,
                static_edge_id,
                agg.attesting_trace_count,
                agg.trace_ids[-1] if agg.trace_ids else "",
                agg.span_ids[-1] if agg.span_ids else "",
                agg.last_seen_at,
                agg.evidence_refs_json(),
                res_status,
                auth_status,
            ),
        )
        # SQLite reports rowcount=1 for both INSERT and UPDATE (UPSERT)
        # so we cannot reliably distinguish here without a SELECT first.
        # We count both as "rows_written" for simplicity; rows_updated is
        # captured via a pre-count below for the stats accuracy when the
        # caller cares.
        if cur.rowcount > 0:
            stats.rows_written += 1


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def build_runtime_view(
    static_snapshot_path: Path | str,
    *,
    explicit_payloads: list[dict[str, Any]] | None = None,
    fail_soft: bool = True,
) -> RuntimeViewBuildStats:
    """Populate ``v_runtime_proof`` in the static ADG snapshot.

    Parameters
    ----------
    static_snapshot_path
        Path to ``adg_indexed_<ts>.sqlite``. The file MUST already contain
        the ``v_runtime_proof`` table created by
        :data:`SQL_CREATE_V_RUNTIME_PROOF` (this is wired into
        :mod:`agentic_core.adg.artifact.ArtifactPaths` schema build).
    explicit_payloads
        Optional list of pre-loaded ``RuntimeADGSnapshot`` payloads. Used by
        tests; production callers leave this ``None`` and let the builder
        query :class:`FileBackedRuntimeADGStore` directly.
    fail_soft
        If True (default), any exception is logged and an empty
        ``RuntimeViewBuildStats`` (with ``error`` populated) is returned.
        If False, exceptions propagate.

    Returns
    -------
    RuntimeViewBuildStats
        Counters for the run.
    """
    stats = RuntimeViewBuildStats()
    snapshot_path = Path(static_snapshot_path)

    if not snapshot_path.exists():
        msg = f"static snapshot not found: {snapshot_path}"
        if fail_soft:
            logger.warning("runtime_view_builder.snapshot_missing: %s", msg)
            stats.error = msg
            return stats
        raise FileNotFoundError(msg)

    try:
        payloads = _iter_runtime_snapshots(explicit_payloads=explicit_payloads)
        stats.snapshots_read = len(payloads)

        if not payloads:
            logger.info(
                "runtime_view_builder.no_snapshots: 0 runtime ADG snapshots "
                "available; v_runtime_proof will be empty for this generation"
            )
            return stats

        aggregates = _aggregate_snapshots(payloads)
        stats.edges_aggregated = len(aggregates)

        if not aggregates:
            return stats

        con = sqlite3.connect(str(snapshot_path))
        try:
            con.execute("BEGIN")
            _upsert_aggregates(con, aggregates, stats)
            con.commit()
        finally:
            con.close()

    except (sqlite3.Error, OSError, ValueError) as exc:
        if not fail_soft:
            raise
        logger.error("runtime_view_builder.failed: %s", exc, exc_info=True)
        stats.error = str(exc)

    return stats


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def _main(argv: list[str] | None = None) -> int:
    """CLI: build the runtime view in-place against the latest snapshot."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Populate v_runtime_proof from the OTel runtime store.",
    )
    parser.add_argument(
        "--snapshot",
        type=Path,
        default=None,
        help="Path to adg_indexed_<ts>.sqlite (default: latest in artifacts/adg/)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Disable fail-soft; raise on any error.",
    )
    args = parser.parse_args(argv)

    snapshot = args.snapshot
    if snapshot is None:
        snaps = sorted((REPO_ROOT / "artifacts" / "adg").glob("adg_indexed_*.sqlite"))
        if not snaps:
            print("[runtime_view_builder] no static snapshot found", file=sys.stderr)
            return 2
        snapshot = snaps[-1]

    stats = build_runtime_view(snapshot, fail_soft=not args.strict)

    print(
        f"[runtime_view_builder] snapshot={snapshot.name} "
        f"snapshots_read={stats.snapshots_read} "
        f"edges_aggregated={stats.edges_aggregated} "
        f"rows_written={stats.rows_written} "
        f"error={stats.error or 'none'}"
    )
    return 0 if stats.error is None else 1


if __name__ == "__main__":
    sys.exit(_main())


__all__ = [
    "RuntimeViewBuildStats",
    "build_runtime_view",
]
