"""Tests for lossless, versioned canonical ADG snapshot identity."""

from __future__ import annotations

from types import SimpleNamespace

from agentic_core.adg.analysis.CanonicalSnapshot import CanonicalSnapshot, build_snapshot


def _edge(**overrides):
    values = {
        "from_name": "pkg.a",
        "relation_type": "calls",
        "to_name": "pkg.b",
        "edge_kind": "direct",
        "source_file": "pkg/a.py",
        "line_no": 10,
        "symbol": "run",
        "semantic_type": "invocation",
        "confidence": 0.9,
        "source_span_start": 100,
        "source_span_end": 110,
        "source_span_line": 10,
        "source_span_column": 4,
        "target_span_start": 0,
        "target_span_end": 0,
        "target_span_line": 0,
        "target_span_column": 0,
        "dynamic_resolution": "",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _result(edges, *, modules=None):
    return SimpleNamespace(
        edges=list(edges),
        modules=list(modules or ["pkg.a", "pkg.b"]),
        digest="scanner-digest",
        commit_sha="abc123",
    )


def test_graph_hash_changes_when_occurrence_evidence_changes():
    before = build_snapshot(_result([_edge(line_no=10)]))
    after = build_snapshot(_result([_edge(line_no=11)]))

    assert before.canonical_edge_order == after.canonical_edge_order
    assert before.graph_hash != after.graph_hash
    assert before.graph_hash_version == "edge-occurrence-v2"


def test_graph_hash_preserves_parallel_occurrences():
    single = build_snapshot(_result([_edge(line_no=10)]))
    parallel = build_snapshot(_result([_edge(line_no=10), _edge(line_no=20)]))

    assert single.graph_hash != parallel.graph_hash
    assert parallel.edge_count == 2
    assert len(parallel.canonical_edge_order) == 1
    assert len(parallel.canonical_edge_occurrences) == 2


def test_graph_hash_includes_isolated_declared_modules():
    before = build_snapshot(_result([_edge()], modules=["pkg.a", "pkg.b"]))
    after = build_snapshot(_result([_edge()], modules=["pkg.a", "pkg.b", "pkg.isolated"]))

    assert before.graph_hash != after.graph_hash
    assert after.node_count == 3
    assert "pkg.isolated" in after.canonical_node_order


def test_snapshot_json_round_trip_preserves_hash_contract():
    snapshot = build_snapshot(_result([_edge()]))
    restored = CanonicalSnapshot.from_json(snapshot.to_json())

    assert restored.graph_hash_version == "edge-occurrence-v2"
    assert restored.canonical_edge_occurrences == snapshot.canonical_edge_occurrences
    assert restored.to_dict() == snapshot.to_dict()


def test_legacy_snapshot_defaults_to_legacy_hash_contract():
    legacy = CanonicalSnapshot.from_dict(
        {
            "graph_hash": "legacy",
            "node_count": 2,
            "edge_count": 1,
            "canonical_edge_order": [["pkg.a", "calls", "pkg.b"]],
        }
    )

    assert legacy.graph_hash_version == "triple-set-v1"
    assert legacy.canonical_edge_occurrences == []
