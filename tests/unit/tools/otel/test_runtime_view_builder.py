"""Tests for tools/otel/runtime_view_builder.py — three-bucket runtime view.

Tier: unit
Plan: docs/archive/windsurf/legacy-tree/plans/three-bucket-otel-view-5db409.md (W1.P1.4)
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Consumer mode declaration — the test suite reads v_runtime_proof for
# verification, classified as proof-mode against the canonical view.
__adg_consumer_mode__ = "proof"

from agentic_core.adg.artifact.edge_authority import (
    SQL_CREATE_V_RUNTIME_PROOF,
    SQL_PROOF_VIEW_ALL,
    runtime_authority_for,
)
from tools.otel.runtime_view_builder import (
    RuntimeViewBuildStats,
    build_runtime_view,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_static_snapshot(path: Path) -> sqlite3.Connection:
    """Create a minimal static ADG snapshot with the schema we need.

    We don't need the full ArtifactPaths schema — just nodes + edges +
    v_runtime_proof so the builder can resolve static_edge_id and write rows.
    """
    con = sqlite3.connect(str(path))
    con.executescript(
        """
        CREATE TABLE nodes (
            id            INTEGER PRIMARY KEY,
            adg_name      TEXT NOT NULL,
            entity_type   TEXT NOT NULL,
            layer         TEXT NOT NULL,
            identity_kind TEXT NOT NULL DEFAULT '',
            confidence    TEXT NOT NULL DEFAULT '',
            resolved_path TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE edges (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            src_id        INTEGER NOT NULL,
            dst_id        INTEGER NOT NULL,
            relation_type TEXT NOT NULL,
            edge_kind     TEXT NOT NULL,
            source_file   TEXT NOT NULL DEFAULT '',
            line_no       INTEGER NOT NULL DEFAULT 0,
            symbol        TEXT NOT NULL DEFAULT '',
            authority     TEXT,
            bucket        TEXT,
            resolution_status TEXT,
            authority_status  TEXT,
            evidence_refs    TEXT
        );
        """
    )
    con.executescript(SQL_CREATE_V_RUNTIME_PROOF)
    con.executescript(SQL_PROOF_VIEW_ALL)
    return con


def _runtime_payload(
    *,
    trace_id: str,
    edges: list[tuple[str, str, str]],  # (src_name, dst_name, relation)
    started_at_utc: int = 1_730_000_000_000,
) -> dict:
    """Build a minimal RuntimeADGSnapshot-shaped payload for tests."""
    # Build deterministic node_ids from names so the builder's lookup works.
    node_ids: dict[str, str] = {}
    for src_name, dst_name, _ in edges:
        node_ids.setdefault(src_name, f"span_{len(node_ids)}")
        node_ids.setdefault(dst_name, f"span_{len(node_ids)}")
    nodes = [
        {
            "node_id": nid,
            "name": nm,
            "kind": "tool",
            "layer": "L2",
            "component": "test",
            "started_at_utc": started_at_utc,
            "duration_ms": 1.0,
            "status": "ok",
            "attributes_json": "{}",
        }
        for nm, nid in node_ids.items()
    ]
    return {
        "snapshot_id": f"snap_{trace_id}",
        "trace_id": trace_id,
        "mission": "test_mission",
        "nodes": nodes,
        "edges": [
            {
                "src_id": node_ids[src_name],
                "dst_id": node_ids[dst_name],
                "relation": rel,
            }
            for src_name, dst_name, rel in edges
        ],
        "metadata": {"run_id": f"run_{trace_id}"},
    }


# ---------------------------------------------------------------------------
# runtime_authority_for — closed enum classifier
# ---------------------------------------------------------------------------


class TestRuntimeAuthorityClassifier:
    """Maps OTel evidence count -> (resolution_status, authority_status)."""

    def test_one_full_trace_is_authoritative(self) -> None:
        assert runtime_authority_for(attesting_trace_count=1) == (
            "VERIFIED_RUNTIME",
            "AUTHORITATIVE_RUNTIME",
        )

    def test_many_full_traces_remain_authoritative(self) -> None:
        assert runtime_authority_for(attesting_trace_count=42) == (
            "VERIFIED_RUNTIME",
            "AUTHORITATIVE_RUNTIME",
        )

    def test_full_trace_with_partials_stays_authoritative(self) -> None:
        # Any full trace dominates; partials don't downgrade.
        assert runtime_authority_for(
            attesting_trace_count=1, partial_trace_count=10
        ) == ("VERIFIED_RUNTIME", "AUTHORITATIVE_RUNTIME")

    def test_only_partials_yields_partial(self) -> None:
        assert runtime_authority_for(
            attesting_trace_count=0, partial_trace_count=1
        ) == ("PARTIAL_TRACE", "PARTIAL")

    def test_no_evidence_is_unknown_not_proof(self) -> None:
        assert runtime_authority_for(attesting_trace_count=0) == (
            "MISSING_TRACE",
            "UNKNOWN_NOT_PROOF",
        )


# ---------------------------------------------------------------------------
# build_runtime_view — empty / fail-soft cases
# ---------------------------------------------------------------------------


class TestBuildRuntimeViewEmptyCases:
    """The builder must be fail-soft for missing OTel data."""

    def test_missing_snapshot_returns_error(self, tmp_path: Path) -> None:
        bad_path = tmp_path / "does_not_exist.sqlite"
        stats = build_runtime_view(bad_path, explicit_payloads=[], fail_soft=True)
        assert stats.error is not None
        assert "not found" in stats.error.lower()
        assert stats.rows_written == 0

    def test_missing_snapshot_strict_raises(self, tmp_path: Path) -> None:
        bad_path = tmp_path / "does_not_exist.sqlite"
        with pytest.raises(FileNotFoundError):
            build_runtime_view(bad_path, explicit_payloads=[], fail_soft=False)

    def test_empty_payloads_writes_zero_rows(self, tmp_path: Path) -> None:
        snap = tmp_path / "snap.sqlite"
        con = _make_static_snapshot(snap)
        con.close()
        stats = build_runtime_view(snap, explicit_payloads=[])
        assert stats.snapshots_read == 0
        assert stats.edges_aggregated == 0
        assert stats.rows_written == 0
        assert stats.error is None

    def test_invalid_payload_shape_skipped(self, tmp_path: Path) -> None:
        snap = tmp_path / "snap.sqlite"
        con = _make_static_snapshot(snap)
        con.close()
        stats = build_runtime_view(
            snap,
            explicit_payloads=[
                "not a dict",  # type: ignore[list-item]
                {"trace_id": "x", "nodes": "wrong shape"},
                None,  # type: ignore[list-item]
            ],
        )
        assert stats.snapshots_read == 3
        assert stats.edges_aggregated == 0


# ---------------------------------------------------------------------------
# build_runtime_view — single-payload happy path
# ---------------------------------------------------------------------------


class TestBuildRuntimeViewSinglePayload:
    """Exercises the aggregator and the v_runtime_proof writer."""

    def test_single_payload_writes_one_row_per_triple(
        self, tmp_path: Path
    ) -> None:
        snap = tmp_path / "snap.sqlite"
        con = _make_static_snapshot(snap)
        con.close()

        payload = _runtime_payload(
            trace_id="trace_A",
            edges=[
                ("agent.research", "tool.search", "parent_child"),
                ("agent.research", "tool.fetch", "parent_child"),
            ],
        )
        stats = build_runtime_view(snap, explicit_payloads=[payload])

        assert stats.snapshots_read == 1
        assert stats.edges_aggregated == 2
        assert stats.rows_written == 2
        assert stats.error is None

        # Verify rows landed correctly with AUTHORITATIVE_RUNTIME.
        con = sqlite3.connect(str(snap))
        rows = con.execute(
            "SELECT src_name, dst_name, relation_type, attesting_trace_count, "
            "authority_status, latest_trace_id FROM v_runtime_proof "
            "ORDER BY src_name, dst_name"
        ).fetchall()
        con.close()

        assert len(rows) == 2
        for row in rows:
            assert row[3] == 1  # attesting_trace_count
            assert row[4] == "AUTHORITATIVE_RUNTIME"
            assert row[5] == "trace_A"

    def test_root_sentinel_src_is_skipped(self, tmp_path: Path) -> None:
        snap = tmp_path / "snap.sqlite"
        con = _make_static_snapshot(snap)
        con.close()

        # Hand-build a payload where one edge has src_id == "__root__".
        payload = {
            "snapshot_id": "snap_x",
            "trace_id": "trace_root_test",
            "nodes": [
                {
                    "node_id": "n1",
                    "name": "agent.x",
                    "kind": "agent",
                    "layer": "L2",
                    "component": "x",
                    "started_at_utc": 1_730_000_000_000,
                    "duration_ms": 1.0,
                    "status": "ok",
                    "attributes_json": "{}",
                },
            ],
            "edges": [
                {"src_id": "__root__", "dst_id": "n1", "relation": "parent_child"},
            ],
        }
        stats = build_runtime_view(snap, explicit_payloads=[payload])
        assert stats.edges_aggregated == 0
        assert stats.rows_written == 0


# ---------------------------------------------------------------------------
# build_runtime_view — multi-payload aggregation
# ---------------------------------------------------------------------------


class TestBuildRuntimeViewMultiPayload:
    """Multiple traces attesting the same edge increment the count."""

    def test_two_traces_same_edge_count_two(self, tmp_path: Path) -> None:
        snap = tmp_path / "snap.sqlite"
        con = _make_static_snapshot(snap)
        con.close()

        edges = [("agent.x", "tool.y", "parent_child")]
        payloads = [
            _runtime_payload(trace_id="trace_1", edges=edges),
            _runtime_payload(trace_id="trace_2", edges=edges),
        ]
        stats = build_runtime_view(snap, explicit_payloads=payloads)
        assert stats.snapshots_read == 2
        assert stats.edges_aggregated == 1
        # rows_written counts INSERT + UPSERT; the row exists either way.

        con = sqlite3.connect(str(snap))
        row = con.execute(
            "SELECT attesting_trace_count, authority_status, evidence_refs "
            "FROM v_runtime_proof"
        ).fetchone()
        con.close()

        assert row[0] == 2
        assert row[1] == "AUTHORITATIVE_RUNTIME"
        evidence = json.loads(row[2])
        assert set(evidence["trace_ids"]) == {"trace_1", "trace_2"}

    def test_same_trace_same_edge_count_once(self, tmp_path: Path) -> None:
        # If two payloads have the same trace_id (shouldn't happen, but
        # robustness), we still count 1 attesting trace.
        snap = tmp_path / "snap.sqlite"
        con = _make_static_snapshot(snap)
        con.close()

        edges = [("agent.x", "tool.y", "parent_child")]
        dup = _runtime_payload(trace_id="trace_1", edges=edges)
        stats = build_runtime_view(snap, explicit_payloads=[dup, dup])

        con = sqlite3.connect(str(snap))
        row = con.execute(
            "SELECT attesting_trace_count FROM v_runtime_proof"
        ).fetchone()
        con.close()
        assert row[0] == 1

    def test_idempotent_rebuild(self, tmp_path: Path) -> None:
        # Running the builder twice with the same payloads must not duplicate
        # rows. The UNIQUE(src_name, dst_name, relation_type) constraint plus
        # the UPSERT clause guarantees this.
        snap = tmp_path / "snap.sqlite"
        con = _make_static_snapshot(snap)
        con.close()

        payloads = [
            _runtime_payload(
                trace_id="trace_1",
                edges=[("a", "b", "parent_child")],
            )
        ]
        build_runtime_view(snap, explicit_payloads=payloads)
        build_runtime_view(snap, explicit_payloads=payloads)

        con = sqlite3.connect(str(snap))
        count = con.execute("SELECT COUNT(*) FROM v_runtime_proof").fetchone()[0]
        con.close()
        assert count == 1


# ---------------------------------------------------------------------------
# proof_view_all — UNION of edges-proof and runtime-proof
# ---------------------------------------------------------------------------


class TestProofViewAll:
    """proof_view_all surfaces both static/registry and runtime proof rows."""

    def test_runtime_rows_appear_in_proof_view_all(self, tmp_path: Path) -> None:
        snap = tmp_path / "snap.sqlite"
        con = _make_static_snapshot(snap)
        # Insert one static edge so we can prove the UNION works.
        con.execute(
            "INSERT INTO nodes(id, adg_name, entity_type, layer) "
            "VALUES (1, 'mod_a', 'module', 'L2')"
        )
        con.execute(
            "INSERT INTO nodes(id, adg_name, entity_type, layer) "
            "VALUES (2, 'mod_b', 'module', 'L2')"
        )
        con.execute(
            "INSERT INTO edges(src_id, dst_id, relation_type, edge_kind, "
            "bucket, authority_status) "
            "VALUES (1, 2, 'imports', 'STATIC_IMPORT', 'static', 'AUTHORITATIVE')"
        )
        con.commit()
        con.close()

        # Add a runtime row.
        payloads = [
            _runtime_payload(
                trace_id="trace_x",
                edges=[("agent.x", "tool.y", "parent_child")],
            )
        ]
        build_runtime_view(snap, explicit_payloads=payloads)

        con = sqlite3.connect(str(snap))
        rows = con.execute(
            "SELECT source_table, src_name, dst_name, authority_status "
            "FROM proof_view_all ORDER BY source_table"
        ).fetchall()
        con.close()

        assert len(rows) == 2
        edges_row = next(r for r in rows if r[0] == "edges")
        runtime_row = next(r for r in rows if r[0] == "v_runtime_proof")
        assert edges_row[1] == "mod_a" and edges_row[2] == "mod_b"
        assert edges_row[3] == "AUTHORITATIVE"
        assert runtime_row[1] == "agent.x" and runtime_row[2] == "tool.y"
        assert runtime_row[3] == "AUTHORITATIVE_RUNTIME"


# ---------------------------------------------------------------------------
# Stats dataclass
# ---------------------------------------------------------------------------


class TestRuntimeViewBuildStats:
    def test_default_stats_are_zero(self) -> None:
        stats = RuntimeViewBuildStats()
        assert stats.snapshots_read == 0
        assert stats.edges_aggregated == 0
        assert stats.rows_written == 0
        assert stats.rows_updated == 0
        assert stats.triples_skipped_invalid == 0
        assert stats.error is None
