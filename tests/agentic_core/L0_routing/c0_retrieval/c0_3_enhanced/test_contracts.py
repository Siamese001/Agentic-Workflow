"""Phase 8 — contract tests."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced import (
    AcceptedGraphNeighbor,
    AclStatus,
    AnchorType,
    FreshnessClass,
    FreshnessStatus,
    GraphTraverseInput,
    HydratedEvidence,
    RejectedGraphNeighbor,
    RejectionReason,
    RetrievalLane,
    SupportTarget,
    compute_manifest_hash,
)


# ---- HydratedEvidence -----------------------------------------------------


def test_hydrated_evidence_requires_source_id() -> None:
    with pytest.raises(ValueError, match="source_id"):
        HydratedEvidence(
            evidence_id="e1",
            source_id="",
            retrieval_lane=RetrievalLane.SPARSE,
            acl_status=AclStatus.ALLOWED,
        )


def test_hydrated_evidence_requires_evidence_id() -> None:
    with pytest.raises(ValueError, match="evidence_id"):
        HydratedEvidence(
            evidence_id="",
            source_id="s1",
            retrieval_lane=RetrievalLane.SPARSE,
            acl_status=AclStatus.ALLOWED,
        )


def test_hydrated_evidence_requires_acl_status() -> None:
    with pytest.raises(ValueError, match="acl_status"):
        HydratedEvidence(
            evidence_id="e1",
            source_id="s1",
            retrieval_lane=RetrievalLane.SPARSE,
            acl_status="",
        )


def test_hydrated_evidence_marks_no_citation_anchor() -> None:
    ev = HydratedEvidence(
        evidence_id="e1",
        source_id="s1",
        retrieval_lane=RetrievalLane.SPARSE,
        acl_status=AclStatus.ALLOWED,
    )
    assert ev.has_citation_anchor is False


# ---- GraphTraverseInput ---------------------------------------------------


def _ev() -> HydratedEvidence:
    return HydratedEvidence(
        evidence_id="e",
        source_id="s",
        retrieval_lane=RetrievalLane.SPARSE,
        acl_status=AclStatus.ALLOWED,
    )


def test_graph_traverse_input_requires_route_replay_key() -> None:
    with pytest.raises(ValueError, match="route_replay_key"):
        GraphTraverseInput(
            route_id="r",
            route_replay_key="",
            policy_hash="ph",
            blueprint_hash="bp",
            support_target=SupportTarget.SOURCE_SUMMARY,
            freshness_class=FreshnessClass.STATIC,
            allowed_relation_types=("references",),
            hydrated_candidates=(_ev(),),
        )


def test_graph_traverse_input_requires_policy_hash() -> None:
    with pytest.raises(ValueError, match="policy_hash"):
        GraphTraverseInput(
            route_id="r",
            route_replay_key="rrk",
            policy_hash="",
            blueprint_hash="bp",
            support_target=SupportTarget.SOURCE_SUMMARY,
            freshness_class=FreshnessClass.STATIC,
            allowed_relation_types=("references",),
            hydrated_candidates=(_ev(),),
        )


def test_graph_traverse_input_requires_support_target() -> None:
    with pytest.raises(ValueError, match="support_target"):
        GraphTraverseInput(
            route_id="r",
            route_replay_key="rrk",
            policy_hash="ph",
            blueprint_hash="bp",
            support_target="",
            freshness_class=FreshnessClass.STATIC,
            allowed_relation_types=("references",),
            hydrated_candidates=(_ev(),),
        )


def test_graph_traverse_input_requires_hydrated_candidates() -> None:
    with pytest.raises(ValueError, match="hydrated_candidates"):
        GraphTraverseInput(
            route_id="r",
            route_replay_key="rrk",
            policy_hash="ph",
            blueprint_hash="bp",
            support_target=SupportTarget.SOURCE_SUMMARY,
            freshness_class=FreshnessClass.STATIC,
            allowed_relation_types=("references",),
            hydrated_candidates=(),
        )


def test_graph_traverse_input_allows_empty_when_explicit() -> None:
    inp = GraphTraverseInput(
        route_id="r",
        route_replay_key="rrk",
        policy_hash="ph",
        blueprint_hash="bp",
        support_target=SupportTarget.SOURCE_SUMMARY,
        freshness_class=FreshnessClass.STATIC,
        allowed_relation_types=("references",),
        hydrated_candidates=(),
        allow_empty_candidates=True,
    )
    assert inp.hydrated_candidates == ()


def test_graph_traverse_input_negative_max_hops_rejected() -> None:
    with pytest.raises(ValueError, match="max_hops"):
        GraphTraverseInput(
            route_id="r",
            route_replay_key="rrk",
            policy_hash="ph",
            blueprint_hash="bp",
            support_target=SupportTarget.SOURCE_SUMMARY,
            freshness_class=FreshnessClass.STATIC,
            max_hops=-1,
            allowed_relation_types=("references",),
            hydrated_candidates=(_ev(),),
        )


def test_graph_traverse_input_empty_relation_types_rejected_when_traversing() -> None:
    with pytest.raises(ValueError, match="allowed_relation_types"):
        GraphTraverseInput(
            route_id="r",
            route_replay_key="rrk",
            policy_hash="ph",
            blueprint_hash="bp",
            support_target=SupportTarget.SOURCE_SUMMARY,
            freshness_class=FreshnessClass.STATIC,
            max_hops=1,
            allowed_relation_types=(),
            hydrated_candidates=(_ev(),),
        )


# ---- AcceptedGraphNeighbor ------------------------------------------------


def _ok_accepted_kwargs() -> dict:
    return dict(
        neighbor_id="n1",
        neighbor_type="document",
        source_id="s1",
        source_type="docs",
        source_version="v1",
        relation_path=("references",),
        relation_types=("references",),
        hop_distance=1,
        inclusion_reason="reason",
        support_contribution="primary",
        authority_contribution="default",
        freshness_status=FreshnessStatus.FRESH,
        acl_status=AclStatus.ALLOWED,
        confidence=0.9,
        lineage_refs=("lineage1",),
        graph_source="GraphDB",
        projection_version="v1",
        snapshot_pointer="snap://1",
    )


def test_accepted_neighbor_requires_relation_path() -> None:
    kw = _ok_accepted_kwargs()
    kw["relation_path"] = ()
    with pytest.raises(ValueError, match="relation_path"):
        AcceptedGraphNeighbor(**kw)


def test_accepted_neighbor_requires_inclusion_reason() -> None:
    kw = _ok_accepted_kwargs()
    kw["inclusion_reason"] = ""
    with pytest.raises(ValueError, match="inclusion_reason"):
        AcceptedGraphNeighbor(**kw)


def test_accepted_neighbor_projected_requires_projection_version() -> None:
    kw = _ok_accepted_kwargs()
    kw["projection_version"] = None
    with pytest.raises(ValueError, match="projection_version"):
        AcceptedGraphNeighbor(**kw)


def test_accepted_neighbor_projected_requires_snapshot_pointer() -> None:
    kw = _ok_accepted_kwargs()
    kw["snapshot_pointer"] = None
    with pytest.raises(ValueError, match="snapshot_pointer"):
        AcceptedGraphNeighbor(**kw)


def test_accepted_neighbor_acl_must_be_allowed_or_cleared() -> None:
    kw = _ok_accepted_kwargs()
    kw["acl_status"] = AclStatus.DENIED
    with pytest.raises(ValueError, match="allowed/cleared"):
        AcceptedGraphNeighbor(**kw)


# ---- RejectedGraphNeighbor ------------------------------------------------


def test_rejected_neighbor_requires_failed_gate() -> None:
    with pytest.raises(ValueError, match="failed_gate"):
        RejectedGraphNeighbor(
            neighbor_id="n",
            relation_path=("r",),
            rejection_reason=RejectionReason.ACL_FAILED,
            failed_gate="",
            hop_distance=1,
            source_id="s",
            acl_status=AclStatus.DENIED,
            freshness_status=FreshnessStatus.FRESH,
        )


def test_rejected_neighbor_requires_rejection_reason() -> None:
    with pytest.raises(ValueError, match="rejection_reason"):
        RejectedGraphNeighbor(
            neighbor_id="n",
            relation_path=("r",),
            rejection_reason="",
            failed_gate="C0.3.G1_ACL",
            hop_distance=1,
            source_id="s",
            acl_status=AclStatus.DENIED,
            freshness_status=FreshnessStatus.FRESH,
        )


# ---- manifest hash --------------------------------------------------------


def test_manifest_hash_is_deterministic() -> None:
    payload = {
        "graph_source": "GraphDB",
        "graph_snapshot_id": "snap://1",
        "projection_version": "v1",
        "traversal_policy_hash": "ph",
        "allowed_relation_types_used": ["references", "supersedes"],
        "blocked_relation_types_seen": [],
        "hops_used": 1,
        "nodes_seen": 2,
        "edges_seen": 2,
        "nodes_accepted": 2,
        "edges_accepted": 2,
        "nodes_rejected": 0,
        "edges_rejected": 0,
        "latency_ms": 5,
        "budget_remaining": {"nodes": 30, "edges": 30, "hops": 0, "latency_ms": 0},
        "replay_seed": "deadbeef",
    }
    h1 = compute_manifest_hash(payload)
    # Same payload, different key insertion order — must produce same hash.
    payload2 = dict(reversed(list(payload.items())))
    h2 = compute_manifest_hash(payload2)
    assert h1 == h2
    # Different replay seed -> different hash.
    payload3 = dict(payload)
    payload3["replay_seed"] = "feedface"
    h3 = compute_manifest_hash(payload3)
    assert h1 != h3
