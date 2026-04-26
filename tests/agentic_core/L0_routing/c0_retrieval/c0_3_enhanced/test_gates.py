"""Phase 8 — gate tests."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced import (
    FreshnessClass,
    RejectionReason,
    SupportTarget,
    run_graph_traverse,
)


def _rejection_reasons(pool) -> set[str]:
    return {
        (r.rejection_reason.value if hasattr(r.rejection_reason, "value") else str(r.rejection_reason))
        for r in pool.rejected_graph_neighbors
    }


def test_max_hops_enforced(make_input, make_basic_graph) -> None:
    g = make_basic_graph()
    g.add_node(
        "doc:far",
        node_type="document",
        source_id="docs/far.md",
        source_type="docs",
        tenant="tenantA",
        region="us",
        data_class="internal",
        payload_preview="far doc",
    )
    g.add_edge("doc:example_v2", "doc:far", "references")
    pool = run_graph_traverse(make_input(max_hops=1), g)
    accepted = {n.neighbor_id for n in pool.accepted_graph_neighbors}
    assert "doc:far" not in accepted


def test_max_nodes_enforced(make_input, make_basic_graph) -> None:
    pool = run_graph_traverse(make_input(max_nodes=1), make_basic_graph())
    assert pool.graph_traversal_manifest.nodes_seen <= 1


def test_max_edges_enforced(make_input, make_basic_graph) -> None:
    pool = run_graph_traverse(make_input(max_edges=1), make_basic_graph())
    assert pool.graph_traversal_manifest.edges_seen <= 1


def test_relation_allowlist_enforced(make_input, make_basic_graph) -> None:
    pool = run_graph_traverse(make_input(allowed_relation_types=("supersedes",)), make_basic_graph())
    accepted_rels = {n.relation_path[-1] for n in pool.accepted_graph_neighbors}
    assert accepted_rels.issubset({"supersedes"})


def test_disallowed_relation_rejected(make_input, make_basic_graph) -> None:
    pool = run_graph_traverse(
        make_input(
            allowed_relation_types=("supersedes", "owns", "references"),
            disallowed_relation_types=("references",),
        ),
        make_basic_graph(),
    )
    accepted_rels = {n.relation_path[-1] for n in pool.accepted_graph_neighbors}
    assert "references" not in accepted_rels


def test_acl_failed_neighbor_rejected(make_input, make_basic_graph) -> None:
    pool = run_graph_traverse(make_input(), make_basic_graph())
    rejected_ids = {r.neighbor_id for r in pool.rejected_graph_neighbors}
    assert "doc:denied" in rejected_ids
    assert RejectionReason.ACL_FAILED.value in _rejection_reasons(pool)


def test_wrong_tenant_neighbor_rejected(make_input, make_basic_graph) -> None:
    pool = run_graph_traverse(make_input(), make_basic_graph())
    rejected_ids = {r.neighbor_id for r in pool.rejected_graph_neighbors}
    assert "doc:wrong_tenant" in rejected_ids
    assert RejectionReason.WRONG_TENANT.value in _rejection_reasons(pool)


def test_wrong_region_neighbor_rejected(make_input, make_basic_graph) -> None:
    pool = run_graph_traverse(make_input(), make_basic_graph())
    rejected_ids = {r.neighbor_id for r in pool.rejected_graph_neighbors}
    assert "doc:wrong_region" in rejected_ids
    assert RejectionReason.WRONG_REGION.value in _rejection_reasons(pool)


def test_blocked_data_class_neighbor_rejected(make_input, make_basic_graph) -> None:
    pool = run_graph_traverse(make_input(data_class_scope=("public", "internal")), make_basic_graph())
    rejected_ids = {r.neighbor_id for r in pool.rejected_graph_neighbors}
    assert "doc:secret" in rejected_ids
    assert RejectionReason.BLOCKED_DATA_CLASS.value in _rejection_reasons(pool)


def test_stale_neighbor_rejected_for_latest_freshness(make_input, make_basic_graph) -> None:
    pool = run_graph_traverse(make_input(freshness_class=FreshnessClass.CURRENT), make_basic_graph())
    rejected_ids = {r.neighbor_id for r in pool.rejected_graph_neighbors}
    assert "doc:stale" in rejected_ids
    assert RejectionReason.STALE.value in _rejection_reasons(pool)


def test_stale_neighbor_allowed_for_historical_support_with_flag(make_input, make_basic_graph) -> None:
    pool = run_graph_traverse(make_input(freshness_class=FreshnessClass.STATIC), make_basic_graph())
    for r in pool.rejected_graph_neighbors:
        if r.neighbor_id == "doc:stale":
            assert r.rejection_reason != RejectionReason.STALE


def test_low_confidence_edge_rejected_or_downgraded(make_input, make_basic_graph) -> None:
    pool = run_graph_traverse(make_input(confidence_threshold=0.5), make_basic_graph())
    rejected_ids = {r.neighbor_id for r in pool.rejected_graph_neighbors}
    assert "doc:low_conf" in rejected_ids
    assert RejectionReason.LOW_CONFIDENCE.value in _rejection_reasons(pool)


def test_missing_lineage_rejected_or_downgraded(make_input, make_basic_graph) -> None:
    g = make_basic_graph()
    g.add_edge("doc:example", "doc:no_lineage", "references")
    pool = run_graph_traverse(make_input(), g)
    rejected_ids = {r.neighbor_id for r in pool.rejected_graph_neighbors}
    assert "doc:no_lineage" in rejected_ids


def test_interesting_not_relevant_rejected(make_input, make_basic_graph) -> None:
    g = make_basic_graph()
    g.add_node(
        "doc:imports_target",
        node_type="document",
        source_id="docs/imports.md",
        source_type="docs",
        tenant="tenantA",
        region="us",
        data_class="internal",
        payload_preview="imports target",
    )
    g.add_edge("doc:example", "doc:imports_target", "imports")
    pool = run_graph_traverse(
        make_input(
            support_target=SupportTarget.EXACT_QUOTE,
            allowed_relation_types=("supersedes",),
        ),
        g,
    )
    accepted_rels = {n.relation_path[-1] for n in pool.accepted_graph_neighbors}
    assert "imports" not in accepted_rels


def test_projection_stale_blocks_for_current_freshness(make_input, make_basic_graph) -> None:
    g = make_basic_graph()
    g.mark_stale("snapshot drift")
    pool = run_graph_traverse(make_input(freshness_class=FreshnessClass.CURRENT), g)
    assert RejectionReason.PROJECTION_STALE.value in _rejection_reasons(pool)


def test_unbounded_walk_via_negative_max_hops_fails(make_input) -> None:
    with pytest.raises(ValueError):
        make_input(max_hops=-1)
