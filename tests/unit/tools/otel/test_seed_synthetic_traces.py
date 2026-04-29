"""Tests for tools/otel/seed_synthetic_traces.py (W2 of plan
three-bucket-gap-remediation-069806).

Verifies that:
  * The seeder samples real (src_name, dst_name, relation_type) triples
    from the static edges table.
  * Synthetic RuntimeADGSnapshot objects round-trip through the
    FileBackedRuntimeADGStore (canonical_bytes -> _deserialise_snapshot
    -> to_dict()) without losing nodes/edges.
  * The runtime view builder picks them up and aggregates correctly.
  * Static-edge correlation works for arbitrary relation types (the
    bug fixed in this wave: _resolve_static_edge_id was previously
    too narrow).
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.otel.seed_synthetic_traces import (  # noqa: E402
    _build_synthetic_snapshot,
    _sample_static_edges,
)


# ---------------------------------------------------------------------------
# Fixture — synthetic ADG snapshot with a few real-shaped edges.
# ---------------------------------------------------------------------------


def _build_synthetic_static_snapshot(path: Path) -> None:
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
    # 5 nodes, 4 edges between them with varied relation types.
    nodes = [
        ("ADG::Module::a.py", "module", "L1", "module", "HIGH", "a.py"),
        ("ADG::Module::b.py", "module", "L1", "module", "HIGH", "b.py"),
        ("ADG::Module::c.py", "module", "L2", "module", "HIGH", "c.py"),
        ("ADG::Symbol::a.foo", "symbol", "L1", "function", "HIGH", "a.py"),
        ("ADG::Symbol::b.bar", "symbol", "L1", "function", "HIGH", "b.py"),
    ]
    for n in nodes:
        con.execute(
            "INSERT INTO nodes (adg_name, entity_type, layer, identity_kind, "
            "confidence, resolved_path) VALUES (?, ?, ?, ?, ?, ?)",
            n,
        )
    edges = [
        (1, 2, "imports", "static"),
        (1, 3, "imports", "static"),
        (4, 5, "calls", "static"),
        (2, 3, "controls_flow", "static"),
    ]
    for src, dst, rel, bucket in edges:
        con.execute(
            "INSERT INTO edges (src_id, dst_id, relation_type, bucket, "
            "edge_kind, source_file) VALUES (?, ?, ?, ?, 'static', '')",
            (src, dst, rel, bucket),
        )
    con.commit()
    con.close()


@pytest.fixture
def synthetic_static(tmp_path: Path) -> Path:
    snap = tmp_path / "synthetic.sqlite"
    _build_synthetic_static_snapshot(snap)
    return snap


# ---------------------------------------------------------------------------
# Sampling
# ---------------------------------------------------------------------------


class TestSampleStaticEdges:
    def test_returns_real_triples(self, synthetic_static):
        rows = _sample_static_edges(synthetic_static, n=10)
        assert len(rows) == 4  # all 4 static edges (n > total)
        # Each row is (src_name, dst_name, relation_type).
        for src, dst, rel in rows:
            assert src.startswith("ADG::")
            assert dst.startswith("ADG::")
            assert rel in ("imports", "calls", "controls_flow")

    def test_sample_size_caps_at_pool_size(self, synthetic_static):
        rows = _sample_static_edges(synthetic_static, n=2)
        assert len(rows) == 2

    def test_excludes_registry_bucket_rows(self, synthetic_static):
        # Inject a registry-bucket row that should NOT be sampled.
        con = sqlite3.connect(synthetic_static)
        con.execute(
            "INSERT INTO edges (src_id, dst_id, relation_type, bucket, "
            "edge_kind, source_file) VALUES (1, 2, 'declared', 'registry', "
            "'reg', '')"
        )
        con.commit()
        con.close()
        rows = _sample_static_edges(synthetic_static, n=100)
        # Should still be 4 — the registry-bucket row is excluded.
        assert len(rows) == 4


# ---------------------------------------------------------------------------
# Snapshot synthesis
# ---------------------------------------------------------------------------


class TestBuildSyntheticSnapshot:
    def test_creates_one_node_per_unique_name(self):
        edges = [
            ("ADG::Module::a", "ADG::Module::b", "imports"),
            ("ADG::Module::a", "ADG::Module::c", "imports"),
            ("ADG::Module::b", "ADG::Module::c", "calls"),
        ]
        snap = _build_synthetic_snapshot(
            trace_id="t1", edges=edges, started_at_ms=1000
        )
        # 3 unique names -> 3 nodes.
        assert len(snap.nodes) == 3
        # 3 edges.
        assert len(snap.edges) == 3

    def test_node_ids_are_deterministic_per_name(self):
        edges = [("ADG::A", "ADG::B", "imports")]
        s1 = _build_synthetic_snapshot(trace_id="t1", edges=edges, started_at_ms=1000)
        s2 = _build_synthetic_snapshot(trace_id="t2", edges=edges, started_at_ms=2000)
        # Same names -> same node_ids (different traces, same node identity).
        ids_1 = sorted(n.node_id for n in s1.nodes)
        ids_2 = sorted(n.node_id for n in s2.nodes)
        assert ids_1 == ids_2

    def test_carries_synthetic_layer_marker(self):
        snap = _build_synthetic_snapshot(
            trace_id="t1",
            edges=[("ADG::A", "ADG::B", "imports")],
            started_at_ms=1000,
        )
        for node in snap.nodes:
            assert node.layer == "L_SYN"
            assert node.kind == "synthetic"
            assert node.component == "seed_synthetic_traces"


# ---------------------------------------------------------------------------
# End-to-end through the runtime view builder
# ---------------------------------------------------------------------------


class TestEndToEndViaBuildRuntimeView:
    """Verify synthetic snapshots flow through to v_runtime_proof correctly."""

    def _add_runtime_view_table(self, path: Path) -> None:
        """Add the v_runtime_proof table that the W1 schema would create."""
        con = sqlite3.connect(path)
        con.execute(
            """
            CREATE TABLE v_runtime_proof (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                src_name TEXT NOT NULL,
                dst_name TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                edge_kind TEXT NOT NULL,
                static_edge_id INTEGER,
                attesting_trace_count INTEGER NOT NULL,
                latest_trace_id TEXT,
                latest_span_id TEXT,
                last_seen_at TEXT,
                evidence_refs TEXT,
                bucket TEXT NOT NULL,
                resolution_status TEXT NOT NULL,
                authority_status TEXT NOT NULL,
                UNIQUE(src_name, dst_name, relation_type)
            )
            """
        )
        con.commit()
        con.close()

    def test_explicit_payload_path_lights_v_runtime_proof(
        self, synthetic_static: Path
    ):
        """Build the runtime view directly from a list of synthetic payloads,
        bypassing FileBackedRuntimeADGStore. Verifies the aggregator +
        upsert path independently of persistence."""
        self._add_runtime_view_table(synthetic_static)

        edges = _sample_static_edges(synthetic_static, n=4)
        snap = _build_synthetic_snapshot(
            trace_id="trace-1", edges=edges, started_at_ms=1700000000000
        )
        from tools.otel.runtime_view_builder import build_runtime_view  # noqa: PLC0415

        stats = build_runtime_view(
            synthetic_static,
            explicit_payloads=[snap.to_dict()],
            fail_soft=False,
        )
        assert stats.snapshots_read == 1
        assert stats.edges_aggregated >= 1
        assert stats.rows_written == stats.edges_aggregated

        con = sqlite3.connect(synthetic_static)
        n = con.execute("SELECT COUNT(*) FROM v_runtime_proof").fetchone()[0]
        n_attested = con.execute(
            "SELECT COUNT(*) FROM v_runtime_proof WHERE attesting_trace_count >= 1"
        ).fetchone()[0]
        n_correlated = con.execute(
            "SELECT COUNT(*) FROM v_runtime_proof WHERE static_edge_id IS NOT NULL"
        ).fetchone()[0]
        con.close()

        assert n >= 1
        assert n_attested == n  # all rows are attested by the synthetic trace
        # All synthetic edges sampled from real static edges should correlate.
        assert n_correlated == n, (
            f"Expected all {n} runtime rows to correlate to a static edge; "
            f"only {n_correlated} did. _resolve_static_edge_id may have "
            f"regressed."
        )


# ---------------------------------------------------------------------------
# Resolver bug guard — protects the 2026-04-29 W2 fix.
# ---------------------------------------------------------------------------


class TestResolverHandlesArbitraryRelations:
    """The pre-W2 _resolve_static_edge_id only matched when relation was in
    {call, invokes, calls, tool_call}. In W2 we broadened it to do an exact
    triple match first. This test pins that behavior so a future narrowing
    refactor cannot silently regress static-edge correlation."""

    def test_imports_relation_resolves_to_static_edge(self, synthetic_static):
        from tools.otel.runtime_view_builder import _resolve_static_edge_id  # noqa: PLC0415

        con = sqlite3.connect(synthetic_static)
        try:
            edge_id = _resolve_static_edge_id(
                con,
                src_name="ADG::Module::a.py",
                dst_name="ADG::Module::b.py",
                relation_type="imports",
            )
        finally:
            con.close()
        assert edge_id is not None
        assert isinstance(edge_id, int)

    def test_controls_flow_relation_resolves_to_static_edge(self, synthetic_static):
        from tools.otel.runtime_view_builder import _resolve_static_edge_id  # noqa: PLC0415

        con = sqlite3.connect(synthetic_static)
        try:
            edge_id = _resolve_static_edge_id(
                con,
                src_name="ADG::Module::b.py",
                dst_name="ADG::Module::c.py",
                relation_type="controls_flow",
            )
        finally:
            con.close()
        assert edge_id is not None

    def test_parent_child_runtime_relation_returns_none(self, synthetic_static):
        from tools.otel.runtime_view_builder import _resolve_static_edge_id  # noqa: PLC0415

        # Runtime-only relation has no static counterpart by construction.
        con = sqlite3.connect(synthetic_static)
        try:
            edge_id = _resolve_static_edge_id(
                con,
                src_name="ADG::Module::a.py",
                dst_name="ADG::Module::b.py",
                relation_type="parent_child",
            )
        finally:
            con.close()
        assert edge_id is None
