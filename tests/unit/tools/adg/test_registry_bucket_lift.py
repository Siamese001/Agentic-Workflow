"""Tests for the registry-bucket lift (P1.3 of plan three-bucket-gap-remediation-069806).

Verifies that ``tools.adg.registry_bucket_lift.lift()`` correctly persists
``RegistryEdge`` records into a snapshot's ``edges`` table with the
constitutional triplet (``bucket``, ``resolution_status``,
``authority_status``) populated, and that the operation is idempotent
across repeated calls.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.adg.registry.registry_resolvers import (  # noqa: E402
    AUTHORITY_AUTHORITATIVE_REGISTRY,
    AUTHORITY_RISK_SIGNAL_ONLY,
    MCP_REGISTRY_ROOT,
    RESOLUTION_DISABLED,
    RESOLUTION_STABLE,
    RegistryEdge,
)
from tools.adg.registry_bucket_lift import lift  # noqa: E402


# ---------------------------------------------------------------------------
# Schema fixture — minimal subset of the canonical ADG SQLite that the lift
# touches. The lift writes to `nodes` and `edges`; nothing else is queried.
# ---------------------------------------------------------------------------


def _create_synthetic_snapshot(path: Path) -> None:
    """Create a snapshot with the canonical NOT NULL constraints on `nodes`.

    Mirrors the real schema's NOT NULL columns so the lift's
    ``_ensure_static_node`` is exercised against the same constraints it
    will hit in production. The 2026-04-29 W1 regen failure (missing
    ``entity_type``/``layer``/``identity_kind``/``confidence``) was caught
    only after schema drift; this fixture prevents recurrence.
    """
    con = sqlite3.connect(path)
    con.executescript(
        """
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            adg_name TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            layer TEXT NOT NULL,
            identity_kind TEXT NOT NULL,
            confidence TEXT NOT NULL,
            resolved_path TEXT NOT NULL
        );
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            src_id INTEGER,
            dst_id INTEGER,
            relation_type TEXT,
            edge_kind TEXT,
            source_file TEXT,
            line_no INTEGER,
            symbol TEXT,
            authority TEXT,
            bucket TEXT,
            resolution_status TEXT,
            authority_status TEXT,
            evidence_refs TEXT
        );
        """
    )
    con.commit()
    con.close()


@pytest.fixture
def synthetic_snapshot(tmp_path: Path) -> Path:
    snap = tmp_path / "synthetic.sqlite"
    _create_synthetic_snapshot(snap)
    return snap


@pytest.fixture
def two_edges() -> list[RegistryEdge]:
    """One STABLE_REGISTRY + one DISABLED_REGISTRY — the canonical pair."""
    return [
        RegistryEdge(
            src_name=MCP_REGISTRY_ROOT,
            dst_name="Registry::MCP::adg_sqlite",
            relation_type="MCP_SERVER_DECLARED",
            edge_kind="REGISTRY_DECLARATION",
            source_file=".windsurf/mcp_config.json",
            symbol="adg_sqlite",
            resolution_status=RESOLUTION_STABLE,
            authority_status=AUTHORITY_AUTHORITATIVE_REGISTRY,
            evidence_refs={
                "registry_path": ".windsurf/mcp_config.json",
                "registry_digest": "abc123",
                "declaration_key": "mcpServers.adg_sqlite",
            },
        ),
        RegistryEdge(
            src_name=MCP_REGISTRY_ROOT,
            dst_name="Registry::MCP::disabled_server",
            relation_type="MCP_SERVER_DECLARED",
            edge_kind="REGISTRY_DECLARATION",
            source_file=".windsurf/mcp_config.json",
            symbol="disabled_server",
            resolution_status=RESOLUTION_DISABLED,
            authority_status=AUTHORITY_RISK_SIGNAL_ONLY,
            evidence_refs={
                "registry_path": ".windsurf/mcp_config.json",
                "registry_digest": "def456",
                "declaration_key": "mcpServers.disabled_server",
            },
        ),
    ]


# ---------------------------------------------------------------------------
# Behavior tests
# ---------------------------------------------------------------------------


class TestLiftBasicPersistence:
    def test_inserts_one_row_per_edge(self, synthetic_snapshot, two_edges):
        stats = lift(static_snapshot=synthetic_snapshot, edges=two_edges)

        assert stats.edges_resolved == 2
        assert stats.edges_inserted == 2
        assert stats.edges_skipped_duplicate == 0

        con = sqlite3.connect(synthetic_snapshot)
        n = con.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        con.close()
        assert n == 2

    def test_writes_constitutional_triplet(self, synthetic_snapshot, two_edges):
        lift(static_snapshot=synthetic_snapshot, edges=two_edges)

        con = sqlite3.connect(synthetic_snapshot)
        rows = con.execute(
            "SELECT bucket, resolution_status, authority_status, authority "
            "FROM edges ORDER BY symbol"
        ).fetchall()
        con.close()

        # Both edges must satisfy the closed-enum invariant.
        for bucket, res, auth_status, auth in rows:
            assert bucket == "registry"
            assert auth == "registry_declared"
            assert res in (RESOLUTION_STABLE, RESOLUTION_DISABLED)
            assert auth_status in (
                AUTHORITY_AUTHORITATIVE_REGISTRY,
                AUTHORITY_RISK_SIGNAL_ONLY,
            )

    def test_disabled_server_carries_risk_signal_authority(
        self, synthetic_snapshot, two_edges
    ):
        lift(static_snapshot=synthetic_snapshot, edges=two_edges)

        con = sqlite3.connect(synthetic_snapshot)
        row = con.execute(
            "SELECT resolution_status, authority_status FROM edges "
            "WHERE symbol = 'disabled_server'"
        ).fetchone()
        con.close()

        assert row == (RESOLUTION_DISABLED, AUTHORITY_RISK_SIGNAL_ONLY)


class TestLiftIdempotency:
    def test_repeated_calls_do_not_duplicate(self, synthetic_snapshot, two_edges):
        first = lift(static_snapshot=synthetic_snapshot, edges=two_edges)
        second = lift(static_snapshot=synthetic_snapshot, edges=two_edges)

        assert first.edges_inserted == 2
        assert second.edges_inserted == 0
        assert second.edges_skipped_duplicate == 2

        con = sqlite3.connect(synthetic_snapshot)
        n = con.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        con.close()
        assert n == 2  # still 2, not 4

    def test_dedup_key_is_src_dst_relation_source(self, synthetic_snapshot):
        # Two edges with same src/dst/relation/source_file — second is dup.
        edge_a = RegistryEdge(
            src_name="Registry::X::root",
            dst_name="Registry::X::a",
            relation_type="DECLARED",
            edge_kind="REGISTRY_DECLARATION",
            source_file="config.json",
            evidence_refs={"registry_digest": "1"},
        )
        edge_b = RegistryEdge(
            src_name="Registry::X::root",
            dst_name="Registry::X::a",
            relation_type="DECLARED",
            edge_kind="REGISTRY_DECLARATION",
            source_file="config.json",
            # Different evidence — but dedup ignores it.
            evidence_refs={"registry_digest": "2"},
        )
        stats = lift(static_snapshot=synthetic_snapshot, edges=[edge_a, edge_b])

        assert stats.edges_inserted == 1
        assert stats.edges_skipped_duplicate == 1


class TestLiftDryRun:
    def test_dry_run_rolls_back(self, synthetic_snapshot, two_edges):
        stats = lift(static_snapshot=synthetic_snapshot, edges=two_edges, dry_run=True)

        # Stats reflect what WOULD have been inserted.
        assert stats.edges_inserted == 2

        # But the snapshot is untouched.
        con = sqlite3.connect(synthetic_snapshot)
        n = con.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        con.close()
        assert n == 0


class TestLiftNodeStubbing:
    def test_creates_nodes_for_unknown_names(self, synthetic_snapshot, two_edges):
        # Initially no nodes.
        con = sqlite3.connect(synthetic_snapshot)
        n_nodes_before = con.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        con.close()
        assert n_nodes_before == 0

        stats = lift(static_snapshot=synthetic_snapshot, edges=two_edges)

        # 1 unique src + 2 unique dsts = 3 stubbed nodes.
        assert stats.nodes_stubbed == 3

        con = sqlite3.connect(synthetic_snapshot)
        n_nodes_after = con.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        con.close()
        assert n_nodes_after == 3

    def test_reuses_existing_node_ids(self, synthetic_snapshot, two_edges):
        # Pre-create the src node — lift should reuse it.
        con = sqlite3.connect(synthetic_snapshot)
        con.execute(
            """
            INSERT INTO nodes (
                adg_name, entity_type, layer, identity_kind, confidence, resolved_path
            ) VALUES (?, 'pre_existing', 'L_REGISTRY', 'virtual', 'HIGH', '')
            """,
            (MCP_REGISTRY_ROOT,),
        )
        con.commit()
        con.close()

        stats = lift(static_snapshot=synthetic_snapshot, edges=two_edges)

        # Only 2 dst nodes need stubbing; the src already existed.
        assert stats.nodes_stubbed == 2


class TestLiftMissingSnapshot:
    def test_raises_filenotfounderror(self, tmp_path):
        nonexistent = tmp_path / "does_not_exist.sqlite"
        with pytest.raises(FileNotFoundError, match="static snapshot not found"):
            lift(static_snapshot=nonexistent, edges=[])

    def test_pipeline_swallows_via_fail_soft(self, tmp_path):
        """Mirrors the generate_full_adg.py except clause — FileNotFoundError
        is in the documented exception set so the pipeline should treat a
        missing snapshot as a SKIPPED stage, not a fatal."""
        nonexistent = tmp_path / "does_not_exist.sqlite"
        try:
            lift(static_snapshot=nonexistent, edges=[])
        except (ImportError, OSError, FileNotFoundError):
            pass  # this is what the pipeline does
        else:
            pytest.fail(
                "expected the lift to raise an exception in the documented set"
            )


class TestLiftStatsByResolutionStatus:
    def test_groups_by_resolution_status(self, synthetic_snapshot, two_edges):
        stats = lift(static_snapshot=synthetic_snapshot, edges=two_edges)

        assert stats.by_resolution_status[RESOLUTION_STABLE] == 1
        assert stats.by_resolution_status[RESOLUTION_DISABLED] == 1


class TestLiftEmptyEdges:
    def test_no_edges_no_writes(self, synthetic_snapshot):
        stats = lift(static_snapshot=synthetic_snapshot, edges=[])

        assert stats.edges_resolved == 0
        assert stats.edges_inserted == 0
        assert stats.nodes_stubbed == 0

        con = sqlite3.connect(synthetic_snapshot)
        n = con.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        con.close()
        assert n == 0
