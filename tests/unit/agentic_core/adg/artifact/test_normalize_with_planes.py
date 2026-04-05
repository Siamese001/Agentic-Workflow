"""Regression tests for ArtifactNormalizer.normalize_with_planes (Patch E2).

These tests verify that the fused single-pass normalizer produces bitwise-
identical output to the separate normalize() + split_artifact() path.

Two layers of coverage:
  1. Synthetic minimal fixture — fast, no filesystem I/O, deterministic.
  2. 12-check round-trip parity guard (counts + digests for full + 3 planes).

If either layer fails, the fused normalizer has diverged from the reference
path and must be investigated before proceeding.
"""

from __future__ import annotations

import pytest

from agentic_core.adg.artifact.builder_types import (
    ADGArtifact,
    BlindSpotReport,
    EntityRecord,
    RelationRecord,
    StructuralMetrics,
)
from agentic_core.adg.artifact.normalizer_config import ArtifactNormalizer
from agentic_core.adg.artifact.SplitArtifact import (
    _FILE_GRAPH_RELS,
    _GOVERNANCE_GRAPH_RELS,
    _SYMBOL_GRAPH_RELS,
    split_artifact,
)


# ---------------------------------------------------------------------------
# Minimal synthetic fixture
# ---------------------------------------------------------------------------

def _make_artifact(entities: list[EntityRecord], relations: list[RelationRecord]) -> ADGArtifact:
    return ADGArtifact(
        commit_sha="deadbeef",
        repo_state_hash="abc123",
        scanner_digest="scan-digest-00",
        entities=entities,
        relations=relations,
        structural_metrics=StructuralMetrics(),
        blind_spots=BlindSpotReport(),
        identity_health={},
    )


def _mod(name: str, layer: str = "L2") -> EntityRecord:
    return EntityRecord(
        adg_name=f"ADG::Module::{name}",
        entity_type="module",
        layer=layer,
        identity_kind="",
        confidence="high",
        resolved_path=name,
    )


def _sym(name: str, parent: str) -> EntityRecord:
    return EntityRecord(
        adg_name=f"ADG::Symbol::{parent}::{name}",
        entity_type="symbol",
        layer="",
        identity_kind="",
        confidence="high",
        resolved_path="",
    )


def _rel(
    from_name: str,
    to_name: str,
    rel_type: str,
    src: str = "a.py",
    line: int = 1,
) -> RelationRecord:
    return RelationRecord(
        from_name=from_name,
        to_name=to_name,
        relation_type=rel_type,
        edge_kind=rel_type,
        source_file=src,
        line_no=line,
    )


@pytest.fixture
def minimal_artifact() -> ADGArtifact:
    """Artifact with one edge per plane category."""
    m_a = _mod("a.py")
    m_b = _mod("b.py")
    s_fn = _sym("fn", "a.py")
    entities = [m_a, m_b, s_fn]
    relations = [
        # file plane
        _rel(m_a.adg_name, m_b.adg_name, "imports"),
        # symbol plane
        _rel(s_fn.adg_name, m_b.adg_name, "calls"),
        # governance plane
        _rel(m_a.adg_name, m_b.adg_name, "violates"),
    ]
    return _make_artifact(entities, relations)


@pytest.fixture
def multi_plane_artifact() -> ADGArtifact:
    """Artifact with multiple edges per plane, including dangling references."""
    mods = [_mod(f"m{i}.py", f"L{i % 3}") for i in range(5)]
    syms = [_sym(f"fn{i}", f"m{i % 3}.py") for i in range(4)]
    entities = mods + syms

    relations = [
        # file plane
        _rel(mods[0].adg_name, mods[1].adg_name, "imports"),
        _rel(mods[1].adg_name, mods[2].adg_name, "imports"),
        _rel(mods[2].adg_name, mods[0].adg_name, "in_cycle"),
        _rel(mods[3].adg_name, mods[4].adg_name, "covers"),
        # symbol plane
        _rel(syms[0].adg_name, syms[1].adg_name, "calls"),
        _rel(syms[2].adg_name, mods[0].adg_name, "reads_from"),
        _rel(mods[1].adg_name, syms[3].adg_name, "decorated_by"),
        # governance plane
        _rel(mods[0].adg_name, mods[3].adg_name, "violates"),
        _rel(mods[1].adg_name, mods[4].adg_name, "antipattern"),
        # dangling reference not in entities
        _rel("ADG::Module::ghost.py", mods[0].adg_name, "imports"),
    ]
    return _make_artifact(entities, relations)


# ---------------------------------------------------------------------------
# Core parity helper
# ---------------------------------------------------------------------------

def _assert_parity(artifact: ADGArtifact) -> None:
    """Assert normalize_with_planes() output is bitwise-identical to reference."""
    normalizer = ArtifactNormalizer()

    ng_ref = normalizer.normalize(artifact)
    planes_ref = split_artifact(artifact)

    ng_full, ng_file, ng_sym, ng_gov = normalizer.normalize_with_planes(
        artifact, _FILE_GRAPH_RELS, _SYMBOL_GRAPH_RELS, _GOVERNANCE_GRAPH_RELS
    )

    # Full graph
    assert ng_full.artifact_digest == ng_ref.artifact_digest, (
        "Full graph digest mismatch between normalize() and normalize_with_planes()"
    )
    assert len(ng_full.nodes) == len(ng_ref.nodes), "Full node count mismatch"
    assert len(ng_full.edges) == len(ng_ref.edges), "Full edge count mismatch"

    # File plane
    assert ng_file.artifact_digest == planes_ref.file_graph.artifact_digest, (
        "file_graph digest mismatch"
    )
    assert len(ng_file.nodes) == len(planes_ref.file_graph.nodes), "file_graph node count mismatch"
    assert len(ng_file.edges) == len(planes_ref.file_graph.edges), "file_graph edge count mismatch"

    # Symbol plane
    assert ng_sym.artifact_digest == planes_ref.symbol_graph.artifact_digest, (
        "symbol_graph digest mismatch"
    )
    assert len(ng_sym.nodes) == len(planes_ref.symbol_graph.nodes), "symbol_graph node count mismatch"
    assert len(ng_sym.edges) == len(planes_ref.symbol_graph.edges), "symbol_graph edge count mismatch"

    # Governance plane
    assert ng_gov.artifact_digest == planes_ref.governance_graph.artifact_digest, (
        "governance_graph digest mismatch"
    )
    assert len(ng_gov.nodes) == len(planes_ref.governance_graph.nodes), "governance_graph node count mismatch"
    assert len(ng_gov.edges) == len(planes_ref.governance_graph.edges), "governance_graph edge count mismatch"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestNormalizeWithPlanesParity:
    """Regression guard: normalize_with_planes() must be bitwise-identical to
    separate normalize() + split_artifact() calls."""

    def test_minimal_artifact_parity(self, minimal_artifact: ADGArtifact) -> None:
        """Minimal 3-edge artifact (one per plane) — full parity check."""
        _assert_parity(minimal_artifact)

    def test_multi_plane_artifact_parity(self, multi_plane_artifact: ADGArtifact) -> None:
        """Multi-plane artifact with dangling references — full parity check."""
        _assert_parity(multi_plane_artifact)

    def test_empty_artifact_parity(self) -> None:
        """Empty artifact (no entities, no relations) — must not crash."""
        _assert_parity(_make_artifact([], []))

    def test_single_plane_only_file(self) -> None:
        """Artifact with only file-plane edges — symbol/gov planes must be empty."""
        m_a = _mod("a.py")
        m_b = _mod("b.py")
        artifact = _make_artifact(
            [m_a, m_b],
            [_rel(m_a.adg_name, m_b.adg_name, "imports")],
        )
        normalizer = ArtifactNormalizer()
        _, ng_file, ng_sym, ng_gov = normalizer.normalize_with_planes(
            artifact, _FILE_GRAPH_RELS, _SYMBOL_GRAPH_RELS, _GOVERNANCE_GRAPH_RELS
        )
        assert len(ng_file.edges) == 1
        assert len(ng_sym.edges) == 0
        assert len(ng_gov.edges) == 0

    def test_plane_edge_counts_sum_to_full(self, multi_plane_artifact: ADGArtifact) -> None:
        """Sum of plane edges must equal total artifact relations (every edge assigned)."""
        normalizer = ArtifactNormalizer()
        ng_full, ng_file, ng_sym, ng_gov = normalizer.normalize_with_planes(
            multi_plane_artifact, _FILE_GRAPH_RELS, _SYMBOL_GRAPH_RELS, _GOVERNANCE_GRAPH_RELS
        )
        plane_total = len(ng_file.edges) + len(ng_sym.edges) + len(ng_gov.edges)
        assert plane_total == len(ng_full.edges), (
            f"Plane edges ({plane_total}) != full edges ({len(ng_full.edges)}): "
            "some edges unrouted or double-counted"
        )

    def test_plane_node_ids_are_local_sequential(self, minimal_artifact: ADGArtifact) -> None:
        """Each plane's node IDs must start at 0 and be contiguous (plane-local)."""
        normalizer = ArtifactNormalizer()
        _, ng_file, ng_sym, ng_gov = normalizer.normalize_with_planes(
            minimal_artifact, _FILE_GRAPH_RELS, _SYMBOL_GRAPH_RELS, _GOVERNANCE_GRAPH_RELS
        )
        for plane_name, ng in [("file", ng_file), ("sym", ng_sym), ("gov", ng_gov)]:
            if not ng.nodes:
                continue
            ids = sorted(int(k) for k in ng.nodes)
            assert ids == list(range(len(ids))), (
                f"{plane_name} plane node IDs are not 0-contiguous: {ids[:10]}"
            )

    def test_idempotent_two_calls(self, multi_plane_artifact: ADGArtifact) -> None:
        """Two normalize_with_planes() calls on the same artifact must return identical digests."""
        normalizer = ArtifactNormalizer()
        args = (multi_plane_artifact, _FILE_GRAPH_RELS, _SYMBOL_GRAPH_RELS, _GOVERNANCE_GRAPH_RELS)
        r1 = normalizer.normalize_with_planes(*args)
        r2 = normalizer.normalize_with_planes(*args)
        for i, label in enumerate(["full", "file", "sym", "gov"]):
            assert r1[i].artifact_digest == r2[i].artifact_digest, (
                f"{label} digest not idempotent across two calls"
            )

    def test_plane_rel_sets_are_disjoint(self) -> None:
        """_FILE_GRAPH_RELS, _SYMBOL_GRAPH_RELS, _GOVERNANCE_GRAPH_RELS must not overlap."""
        assert _FILE_GRAPH_RELS.isdisjoint(_SYMBOL_GRAPH_RELS), "file ∩ sym non-empty"
        assert _FILE_GRAPH_RELS.isdisjoint(_GOVERNANCE_GRAPH_RELS), "file ∩ gov non-empty"
        assert _SYMBOL_GRAPH_RELS.isdisjoint(_GOVERNANCE_GRAPH_RELS), "sym ∩ gov non-empty"
