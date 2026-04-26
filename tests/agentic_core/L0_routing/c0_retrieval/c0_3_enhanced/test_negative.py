"""Phase 8 — negative tests."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced import (
    AclStatus,
    FreshnessClass,
    GraphTraverseInput,
    HydratedEvidence,
    InMemoryGraphAdapter,
    RejectionReason,
    RetrievalLane,
    SupportTarget,
    run_graph_traverse,
)


def test_unbounded_graph_walk_fails() -> None:
    with pytest.raises(ValueError):
        GraphTraverseInput(
            route_id="r",
            route_replay_key="rrk",
            policy_hash="ph",
            blueprint_hash="bp",
            support_target=SupportTarget.SOURCE_SUMMARY,
            freshness_class=FreshnessClass.STATIC,
            max_hops=1,
            max_nodes=0,  # invalid when traversal enabled
            allowed_relation_types=("references",),
            hydrated_candidates=(
                HydratedEvidence(
                    evidence_id="e",
                    source_id="s",
                    retrieval_lane=RetrievalLane.SPARSE,
                    acl_status=AclStatus.ALLOWED,
                ),
            ),
        )


def test_acl_escape_attempt_fails(make_input, make_basic_graph) -> None:
    pool = run_graph_traverse(make_input(), make_basic_graph())
    rejected_ids = {r.neighbor_id for r in pool.rejected_graph_neighbors}
    assert "doc:denied" in rejected_ids
    accepted_ids = {n.neighbor_id for n in pool.accepted_graph_neighbors}
    assert "doc:denied" not in accepted_ids


def test_relation_type_not_allowed_fails(make_input, make_basic_graph) -> None:
    g = make_basic_graph()
    g.add_node(
        "doc:weird",
        node_type="document",
        source_id="docs/weird.md",
        source_type="docs",
        tenant="tenantA",
        region="us",
        data_class="internal",
    )
    g.add_edge("doc:example", "doc:weird", "weird_relation_not_allowed")
    pool = run_graph_traverse(make_input(), g)
    accepted_ids = {n.neighbor_id for n in pool.accepted_graph_neighbors}
    assert "doc:weird" not in accepted_ids


def test_missing_lineage_neighbor_rejected(make_input, make_basic_graph) -> None:
    g = make_basic_graph()
    g.add_edge("doc:example", "doc:no_lineage", "references")
    pool = run_graph_traverse(make_input(), g)
    rejected_ids = {r.neighbor_id for r in pool.rejected_graph_neighbors}
    assert "doc:no_lineage" in rejected_ids


def test_projection_stale_for_current_claim_downgrades(make_input, make_basic_graph) -> None:
    g = make_basic_graph()
    g.mark_stale("snapshot drift")
    pool = run_graph_traverse(make_input(freshness_class=FreshnessClass.CURRENT), g)
    assert any(r.rejection_reason == RejectionReason.PROJECTION_STALE for r in pool.rejected_graph_neighbors)


def test_contradiction_not_hidden(make_input, make_basic_graph) -> None:
    pool = run_graph_traverse(make_input(), make_basic_graph())
    # The basic graph contains 1 contradicts edge to doc:contradiction.
    accepted_rels = [n.relation_path[-1] for n in pool.accepted_graph_neighbors]
    assert "contradicts" in accepted_rels
    # And it must surface in contradiction_candidates.
    assert pool.contradiction_candidates


def test_duplicate_source_not_counted_as_diversity(make_input, make_basic_graph) -> None:
    g = make_basic_graph()
    # add a duplicate node to the same source — same source_id.
    g.add_node(
        "doc:duplicate",
        node_type="document",
        source_id="docs/example.md",  # same source_id as doc:example
        source_type="docs",
        tenant="tenantA",
        region="us",
        data_class="internal",
        payload_preview="duplicate",
    )
    g.add_edge("doc:example", "doc:duplicate", "duplicates")
    pool = run_graph_traverse(make_input(allowed_relation_types=("duplicates", "references")), g)
    # The duplicates relation isn't in priority_order for SOURCE_SUMMARY ->
    # accepted only as background OR rejected; either way must NOT count as
    # a primary supporting source.
    duplicates_accepted = [n for n in pool.accepted_graph_neighbors if n.relation_path[-1] == "duplicates"]
    if duplicates_accepted:
        for n in duplicates_accepted:
            assert n.support_contribution != "primary"


def test_low_confidence_edge_does_not_become_must_use(make_input, make_basic_graph) -> None:
    pool = run_graph_traverse(make_input(confidence_threshold=0.5), make_basic_graph())
    # doc:low_conf must be rejected; certainly not in accepted/MUST_USE.
    accepted_ids = {n.neighbor_id for n in pool.accepted_graph_neighbors}
    assert "doc:low_conf" not in accepted_ids


def test_raw_unhydrated_candidate_rejected() -> None:
    """A HydratedEvidence with no source_id can't even be constructed."""
    with pytest.raises(ValueError):
        HydratedEvidence(
            evidence_id="x",
            source_id="",
            retrieval_lane=RetrievalLane.SPARSE,
            acl_status=AclStatus.ALLOWED,
        )


def test_empty_pool_is_valid_when_explicit() -> None:
    """Phase 1 §2: hydrated_candidates may be empty only when allow_empty is True."""
    g = InMemoryGraphAdapter()
    inp = GraphTraverseInput(
        route_id="r",
        route_replay_key="rrk",
        policy_hash="ph",
        blueprint_hash="bp",
        support_target=SupportTarget.SOURCE_SUMMARY,
        freshness_class=FreshnessClass.STATIC,
        max_hops=0,
        allowed_relation_types=(),
        hydrated_candidates=(),
        allow_empty_candidates=True,
    )
    pool = run_graph_traverse(inp, g)
    # Empty input -> empty output but manifest still attached.
    assert pool.accepted_graph_neighbors == ()
    assert pool.rejected_graph_neighbors == ()
    assert pool.graph_traversal_manifest.manifest_hash
