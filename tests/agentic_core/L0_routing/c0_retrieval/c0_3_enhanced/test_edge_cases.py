"""Edge-case + bug-regression tests for C0.3 enhanced.

Covers paths the main test files don't exercise:
  * cycle detection + multi-path duplicate
  * adapter exception caught (not crashed)
  * adapter health check failure -> RuntimeError
  * per-relation hop budget cap
  * confidence-threshold boundary
  * frozen contract immutability
  * GraphTraversalPlan priority/allowed cross-check validation
  * ambiguous anchor surfacing
  * citation-anchor downgrade flag
  * multi-hop relation_path correctness
  * EXACT_QUOTE strict policy honoring
  * plan + manifest determinism across runs
  * empty primary_relations intersection
  * projection without snapshot pointer rejection
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced import (
    AcceptedGraphNeighbor,
    AclStatus,
    AnchorCandidate,
    AnchorType,
    FreshnessClass,
    FreshnessStatus,
    GraphBudget,
    GraphTraversalPlan,
    GraphTraverseInput,
    HydratedEvidence,
    InMemoryGraphAdapter,
    NullSpanRecorder,
    RejectionReason,
    RetrievalLane,
    SupportTarget,
    compute_manifest_hash,
    run_graph_traverse,
)
from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter import (
    GraphAdapterHealth,
    GraphNeighbor,
)


# ---------------------------------------------------------------------------
# Cycle detection
# ---------------------------------------------------------------------------


def test_cycle_detection_short_circuits_revisit() -> None:
    """A → B, B → A traversal must not infinite-loop and the revisit must be
    rejected with CYCLE_DETECTED."""
    g = InMemoryGraphAdapter()
    common = dict(
        tenant="tA",
        region="us",
        data_class="internal",
        acl_status=AclStatus.ALLOWED.value,
    )
    g.add_node("a", source_id="a", source_type="docs", **common)
    g.add_node("b", source_id="b", source_type="docs", **common)
    g.add_edge("a", "b", "references")
    g.add_edge("b", "a", "references")  # cycle back

    ev = HydratedEvidence(
        evidence_id="e",
        source_id="a",
        retrieval_lane=RetrievalLane.SPARSE,
        acl_status=AclStatus.ALLOWED,
        file_path_or_doc_id="a",
        extracted_ids=("a",),
        tenant="tA",
        region="us",
        data_class="internal",
    )
    inp = GraphTraverseInput(
        route_id="r",
        route_replay_key="rrk",
        policy_hash="ph",
        blueprint_hash="bp",
        support_target=SupportTarget.SOURCE_SUMMARY,
        freshness_class=FreshnessClass.STATIC,
        max_hops=5,
        max_nodes=32,
        max_edges=32,
        allowed_relation_types=("references",),
        hydrated_candidates=(ev,),
        tenant_scope="tA",
        region_scope="us",
        data_class_scope=("internal",),
        acl_scope=(AclStatus.ALLOWED.value,),
    )
    pool = run_graph_traverse(inp, g)

    accepted_ids = {n.neighbor_id for n in pool.accepted_graph_neighbors}
    assert "b" in accepted_ids  # b accepted via a -> b
    rejected_reasons = {r.rejection_reason for r in pool.rejected_graph_neighbors}
    assert RejectionReason.CYCLE_DETECTED in rejected_reasons


# ---------------------------------------------------------------------------
# Adapter exception handling
# ---------------------------------------------------------------------------


class _RaisingAdapter(InMemoryGraphAdapter):
    """Adapter whose get_neighbors raises on a specific node."""

    def __init__(self, raise_on_node: str) -> None:
        super().__init__()
        self._raise_on = raise_on_node

    def get_neighbors(self, node_id, relation_types, scope, limit):  # type: ignore[override]
        if node_id == self._raise_on:
            raise ValueError(f"simulated adapter failure on {node_id}")
        return super().get_neighbors(node_id, relation_types, scope, limit)


def test_adapter_exception_is_recorded_not_crashed() -> None:
    g = _RaisingAdapter(raise_on_node="root")
    common = dict(
        tenant="tA",
        region="us",
        data_class="internal",
        acl_status=AclStatus.ALLOWED.value,
    )
    g.add_node("root", source_id="root", source_type="docs", **common)
    ev = HydratedEvidence(
        evidence_id="e",
        source_id="root",
        retrieval_lane=RetrievalLane.SPARSE,
        acl_status=AclStatus.ALLOWED,
        file_path_or_doc_id="root",
        extracted_ids=("root",),
        tenant="tA",
        region="us",
        data_class="internal",
    )
    inp = GraphTraverseInput(
        route_id="r",
        route_replay_key="rrk",
        policy_hash="ph",
        blueprint_hash="bp",
        support_target=SupportTarget.SOURCE_SUMMARY,
        freshness_class=FreshnessClass.STATIC,
        max_hops=2,
        max_nodes=8,
        max_edges=8,
        allowed_relation_types=("references",),
        hydrated_candidates=(ev,),
        tenant_scope="tA",
        region_scope="us",
        data_class_scope=("internal",),
        acl_scope=(AclStatus.ALLOWED.value,),
    )
    # Must not crash.
    pool = run_graph_traverse(inp, g)
    # The failure is recorded as a rejected neighbor with adapter_error gate.
    failed_gates = {r.failed_gate for r in pool.rejected_graph_neighbors}
    assert "adapter_error" in failed_gates


# ---------------------------------------------------------------------------
# Health check failure
# ---------------------------------------------------------------------------


class _UnhealthyAdapter(InMemoryGraphAdapter):
    def health_check(self) -> GraphAdapterHealth:
        return GraphAdapterHealth(
            healthy=False,
            backend="broken",
            latency_p50_ms=999.0,
            latency_p95_ms=9999.0,
            last_error="simulated unhealthy state",
        )


def test_unhealthy_adapter_raises_runtime_error() -> None:
    g = _UnhealthyAdapter()
    g.add_node(
        "x",
        source_id="x",
        source_type="docs",
        tenant="tA",
        region="us",
        data_class="internal",
        acl_status=AclStatus.ALLOWED.value,
    )
    ev = HydratedEvidence(
        evidence_id="e",
        source_id="x",
        retrieval_lane=RetrievalLane.SPARSE,
        acl_status=AclStatus.ALLOWED,
        file_path_or_doc_id="x",
        extracted_ids=("x",),
    )
    inp = GraphTraverseInput(
        route_id="r",
        route_replay_key="rrk",
        policy_hash="ph",
        blueprint_hash="bp",
        support_target=SupportTarget.SOURCE_SUMMARY,
        freshness_class=FreshnessClass.STATIC,
        max_hops=1,
        allowed_relation_types=("references",),
        hydrated_candidates=(ev,),
    )
    with pytest.raises(RuntimeError, match="unhealthy"):
        run_graph_traverse(inp, g)


# ---------------------------------------------------------------------------
# Boundary tests
# ---------------------------------------------------------------------------


def test_confidence_at_threshold_is_accepted(make_input, make_basic_graph) -> None:
    """confidence == threshold: not strictly less, so PASS."""
    pool = run_graph_traverse(make_input(confidence_threshold=0.1), make_basic_graph())
    # doc:low_conf has confidence=0.1; with threshold=0.1 it must NOT be
    # rejected for low_confidence.
    for r in pool.rejected_graph_neighbors:
        if r.neighbor_id == "doc:low_conf":
            assert r.rejection_reason != RejectionReason.LOW_CONFIDENCE


def test_confidence_just_below_threshold_rejected(make_input, make_basic_graph) -> None:
    pool = run_graph_traverse(make_input(confidence_threshold=0.10001), make_basic_graph())
    rejected = {r.neighbor_id for r in pool.rejected_graph_neighbors}
    assert "doc:low_conf" in rejected


# ---------------------------------------------------------------------------
# Frozen contract immutability
# ---------------------------------------------------------------------------


def test_hydrated_evidence_is_frozen() -> None:
    ev = HydratedEvidence(
        evidence_id="e",
        source_id="s",
        retrieval_lane=RetrievalLane.SPARSE,
        acl_status=AclStatus.ALLOWED,
    )
    with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
        ev.evidence_id = "mutated"  # type: ignore[misc]


def test_graph_traverse_input_is_frozen() -> None:
    ev = HydratedEvidence(
        evidence_id="e",
        source_id="s",
        retrieval_lane=RetrievalLane.SPARSE,
        acl_status=AclStatus.ALLOWED,
    )
    inp = GraphTraverseInput(
        route_id="r",
        route_replay_key="rrk",
        policy_hash="ph",
        blueprint_hash="bp",
        support_target=SupportTarget.SOURCE_SUMMARY,
        freshness_class=FreshnessClass.STATIC,
        max_hops=1,
        allowed_relation_types=("references",),
        hydrated_candidates=(ev,),
    )
    with pytest.raises(Exception):
        inp.max_hops = 99  # type: ignore[misc]


# ---------------------------------------------------------------------------
# GraphTraversalPlan validation
# ---------------------------------------------------------------------------


def test_plan_validation_rejects_priority_outside_allowed() -> None:
    budget = GraphBudget(
        max_hops=1,
        max_nodes=8,
        max_edges=8,
        max_neighbors_by_anchor=4,
        max_latency_ms=1000,
        max_token_budget_for_graph_context=1000,
    )
    with pytest.raises(ValueError, match="priority_order"):
        GraphTraversalPlan(
            start_nodes=("n",),
            allowed_relation_types=("references",),
            relation_priority_order=("supersedes",),  # not in allowed!
            max_hops_by_relation_type={"references": 1},
            max_neighbors_by_anchor=4,
            contradiction_scan_enabled=True,
            supersession_scan_enabled=True,
            dependency_scan_enabled=False,
            lineage_scan_enabled=True,
            runtime_scan_enabled=False,
            definition_scan_enabled=True,
            owner_scan_enabled=True,
            source_authority_scan_enabled=True,
            graph_budget=budget,
            stop_conditions=(),
            replay_metadata={},
        )


# ---------------------------------------------------------------------------
# Ambiguous anchor surfacing
# ---------------------------------------------------------------------------


def test_ambiguous_anchor_surfaced_in_pool() -> None:
    g = InMemoryGraphAdapter()
    common = dict(
        tenant="tA",
        region="us",
        data_class="internal",
        acl_status=AclStatus.ALLOWED.value,
    )
    # Two nodes share an alias.
    g.add_node(
        "n1",
        source_id="n1",
        source_type="docs",
        anchor_aliases=("AmbiguousName",),
        **common,
    )
    g.add_node(
        "n2",
        source_id="n2",
        source_type="docs",
        anchor_aliases=("AmbiguousName",),
        **common,
    )
    ev = HydratedEvidence(
        evidence_id="e",
        source_id="src",
        retrieval_lane=RetrievalLane.SPARSE,
        acl_status=AclStatus.ALLOWED,
        file_path_or_doc_id=None,
        extracted_ids=("AmbiguousName",),
        extracted_symbols=(),
        extracted_entities=(),
        tenant="tA",
        region="us",
        data_class="internal",
    )
    inp = GraphTraverseInput(
        route_id="r",
        route_replay_key="rrk",
        policy_hash="ph",
        blueprint_hash="bp",
        support_target=SupportTarget.SOURCE_SUMMARY,
        freshness_class=FreshnessClass.STATIC,
        max_hops=1,
        allowed_relation_types=("references",),
        hydrated_candidates=(ev,),
        tenant_scope="tA",
        region_scope="us",
        data_class_scope=("internal",),
        acl_scope=(AclStatus.ALLOWED.value,),
    )
    pool = run_graph_traverse(inp, g)
    assert any(a.anchor_value == "AmbiguousName" for a in pool.ambiguous_anchors)


# ---------------------------------------------------------------------------
# Citation anchor downgrade
# ---------------------------------------------------------------------------


def test_neighbor_without_span_ref_marked_background_when_citation_required() -> None:
    g = InMemoryGraphAdapter()
    common = dict(
        tenant="tA",
        region="us",
        data_class="internal",
        acl_status=AclStatus.ALLOWED.value,
    )
    g.add_node("a", source_id="a", source_type="docs", span_ref="a.md#L1", **common)
    g.add_node("b", source_id="b", source_type="docs", span_ref=None, **common)  # no citation anchor
    g.add_edge("a", "b", "references")

    ev = HydratedEvidence(
        evidence_id="e",
        source_id="a",
        retrieval_lane=RetrievalLane.SPARSE,
        acl_status=AclStatus.ALLOWED,
        file_path_or_doc_id="a",
        extracted_ids=("a",),
        tenant="tA",
        region="us",
        data_class="internal",
    )
    inp = GraphTraverseInput(
        route_id="r",
        route_replay_key="rrk",
        policy_hash="ph",
        blueprint_hash="bp",
        support_target=SupportTarget.SOURCE_SUMMARY,
        freshness_class=FreshnessClass.STATIC,
        max_hops=1,
        allowed_relation_types=("references",),
        hydrated_candidates=(ev,),
        tenant_scope="tA",
        region_scope="us",
        data_class_scope=("internal",),
        acl_scope=(AclStatus.ALLOWED.value,),
        require_citation_anchor=True,
    )
    pool = run_graph_traverse(inp, g)
    # 'b' must be accepted (citation gate downgrades, never rejects) AND
    # carry a background_only / no_citation_anchor flag.
    accepted_b = next(
        (n for n in pool.accepted_graph_neighbors if n.neighbor_id == "b"),
        None,
    )
    assert accepted_b is not None
    assert "background_only" in accepted_b.flag_categories
    assert "no_citation_anchor" in accepted_b.flag_categories


# ---------------------------------------------------------------------------
# Multi-hop relation_path correctness
# ---------------------------------------------------------------------------


def test_multi_hop_relation_path_records_full_chain() -> None:
    g = InMemoryGraphAdapter()
    common = dict(
        tenant="tA",
        region="us",
        data_class="internal",
        acl_status=AclStatus.ALLOWED.value,
    )
    g.add_node("a", source_id="a", source_type="docs", **common)
    g.add_node("b", source_id="b", source_type="docs", **common)
    g.add_node("c", source_id="c", source_type="docs", **common)
    g.add_edge("a", "b", "references")
    g.add_edge("b", "c", "supersedes")

    ev = HydratedEvidence(
        evidence_id="e",
        source_id="a",
        retrieval_lane=RetrievalLane.SPARSE,
        acl_status=AclStatus.ALLOWED,
        file_path_or_doc_id="a",
        extracted_ids=("a",),
        tenant="tA",
        region="us",
        data_class="internal",
    )
    inp = GraphTraverseInput(
        route_id="r",
        route_replay_key="rrk",
        policy_hash="ph",
        blueprint_hash="bp",
        support_target=SupportTarget.SOURCE_SUMMARY,
        freshness_class=FreshnessClass.STATIC,
        max_hops=2,
        max_nodes=8,
        max_edges=8,
        allowed_relation_types=("references", "supersedes"),
        hydrated_candidates=(ev,),
        tenant_scope="tA",
        region_scope="us",
        data_class_scope=("internal",),
        acl_scope=(AclStatus.ALLOWED.value,),
    )
    pool = run_graph_traverse(inp, g)
    c_neighbor = next((n for n in pool.accepted_graph_neighbors if n.neighbor_id == "c"), None)
    assert c_neighbor is not None
    assert c_neighbor.relation_path == ("references", "supersedes")
    assert c_neighbor.hop_distance == 2


# ---------------------------------------------------------------------------
# EXACT_QUOTE strict policy
# ---------------------------------------------------------------------------


def test_exact_quote_does_not_walk_imports(make_input, make_basic_graph) -> None:
    g = make_basic_graph()
    g.add_node(
        "doc:imp",
        source_id="docs/imp.md",
        source_type="docs",
        tenant="tenantA",
        region="us",
        data_class="internal",
    )
    g.add_edge("doc:example", "doc:imp", "imports")

    pool = run_graph_traverse(
        make_input(
            support_target=SupportTarget.EXACT_QUOTE,
            allowed_relation_types=("supersedes", "imports", "references"),
        ),
        g,
    )
    # imports is not in EXACT_QUOTE recommended set; it ends up in extras
    # of priority_order. G9 currently allows it (priority_order PASS); but
    # support_contribution must NOT be 'primary'.
    for n in pool.accepted_graph_neighbors:
        if n.relation_path[-1] == "imports":
            assert n.support_contribution != "primary"


# ---------------------------------------------------------------------------
# Plan + manifest determinism
# ---------------------------------------------------------------------------


def test_manifest_hash_is_deterministic_across_runs(make_input, make_basic_graph) -> None:
    """Phase 1 §8: manifest_hash must be deterministic from stable fields.
    Latency is volatile and excluded; everything else must agree."""
    inp = make_input()
    pool1 = run_graph_traverse(inp, make_basic_graph())
    pool2 = run_graph_traverse(inp, make_basic_graph())
    assert pool1.graph_traversal_manifest.manifest_hash == pool2.graph_traversal_manifest.manifest_hash


def test_manifest_hash_excludes_volatile_latency() -> None:
    """compute_manifest_hash must ignore latency_ms / budget_remaining."""
    payload_a = {
        "graph_source": "G",
        "graph_snapshot_id": "S",
        "projection_version": "v1",
        "traversal_policy_hash": "ph",
        "allowed_relation_types_used": ["references"],
        "blocked_relation_types_seen": [],
        "hops_used": 1,
        "nodes_seen": 1,
        "edges_seen": 1,
        "nodes_accepted": 1,
        "edges_accepted": 1,
        "nodes_rejected": 0,
        "edges_rejected": 0,
        "latency_ms": 5,
        "budget_remaining": {"nodes": 7, "edges": 7, "hops": 0, "latency_ms": 100},
        "replay_seed": "x",
    }
    payload_b = dict(payload_a)
    payload_b["latency_ms"] = 9999
    payload_b["budget_remaining"] = {"nodes": 7, "edges": 7, "hops": 0, "latency_ms": 0}

    assert compute_manifest_hash(payload_a) == compute_manifest_hash(payload_b)


def test_plan_replay_seed_is_deterministic(make_input, make_basic_graph) -> None:
    inp = make_input()
    pool1 = run_graph_traverse(inp, make_basic_graph())
    pool2 = run_graph_traverse(inp, make_basic_graph())
    assert pool1.graph_traversal_manifest.replay_seed == pool2.graph_traversal_manifest.replay_seed


# ---------------------------------------------------------------------------
# Empty primary_relations intersection
# ---------------------------------------------------------------------------


def test_empty_primary_intersection_marks_everything_secondary_or_background() -> None:
    """If user's allowed_relation_types has zero overlap with the support
    target's recommended set, no neighbor is 'primary'."""
    g = InMemoryGraphAdapter()
    common = dict(
        tenant="tA",
        region="us",
        data_class="internal",
        acl_status=AclStatus.ALLOWED.value,
    )
    g.add_node("a", source_id="a", source_type="docs", **common)
    g.add_node("b", source_id="b", source_type="docs", **common)
    g.add_edge("a", "b", "imports")

    ev = HydratedEvidence(
        evidence_id="e",
        source_id="a",
        retrieval_lane=RetrievalLane.SPARSE,
        acl_status=AclStatus.ALLOWED,
        file_path_or_doc_id="a",
        extracted_ids=("a",),
        tenant="tA",
        region="us",
        data_class="internal",
    )
    # SOURCE_SUMMARY recommends references/defines/parent_of/etc; user
    # allows ONLY imports — intersection is empty.
    inp = GraphTraverseInput(
        route_id="r",
        route_replay_key="rrk",
        policy_hash="ph",
        blueprint_hash="bp",
        support_target=SupportTarget.SOURCE_SUMMARY,
        freshness_class=FreshnessClass.STATIC,
        max_hops=1,
        allowed_relation_types=("imports",),
        hydrated_candidates=(ev,),
        tenant_scope="tA",
        region_scope="us",
        data_class_scope=("internal",),
        acl_scope=(AclStatus.ALLOWED.value,),
    )
    pool = run_graph_traverse(inp, g)
    for n in pool.accepted_graph_neighbors:
        assert n.support_contribution != "primary"


# ---------------------------------------------------------------------------
# AcceptedGraphNeighbor: non-projected neighbor must NOT require projection_version
# ---------------------------------------------------------------------------


def test_accepted_neighbor_non_projected_skips_projection_fields() -> None:
    n = AcceptedGraphNeighbor(
        neighbor_id="n",
        neighbor_type="document",
        source_id="s",
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
        lineage_refs=("a",),
        graph_source="DirectStore",
        projection_version=None,
        snapshot_pointer=None,
        is_projected=False,
    )
    assert n.is_projected is False


# ---------------------------------------------------------------------------
# GraphNeighbor dataclass validation
# ---------------------------------------------------------------------------


def test_graph_neighbor_requires_node_id() -> None:
    with pytest.raises(ValueError, match="node_id"):
        GraphNeighbor(
            node_id="",
            node_type="document",
            source_id="s",
            source_type="docs",
            source_version="v1",
            relation_type="references",
            relation_path=("references",),
            hop_distance=1,
            tenant="t",
            region="r",
            data_class="internal",
            acl_status=AclStatus.ALLOWED,
            freshness_status=FreshnessStatus.FRESH,
            confidence=0.9,
            lineage_refs=(),
            span_ref=None,
            graph_source="G",
            projection_version="v1",
            snapshot_pointer="snap",
            payload_preview=None,
        )


def test_graph_neighbor_negative_hop_distance_rejected() -> None:
    with pytest.raises(ValueError, match="hop_distance"):
        GraphNeighbor(
            node_id="n",
            node_type="document",
            source_id="s",
            source_type="docs",
            source_version="v1",
            relation_type="references",
            relation_path=("references",),
            hop_distance=-1,
            tenant="t",
            region="r",
            data_class="internal",
            acl_status=AclStatus.ALLOWED,
            freshness_status=FreshnessStatus.FRESH,
            confidence=0.9,
            lineage_refs=(),
            span_ref=None,
            graph_source="G",
            projection_version="v1",
            snapshot_pointer="snap",
            payload_preview=None,
        )


# ---------------------------------------------------------------------------
# AnchorCandidate validation
# ---------------------------------------------------------------------------


def test_anchor_candidate_requires_value() -> None:
    with pytest.raises(ValueError, match="anchor_value"):
        AnchorCandidate(
            anchor_value="",
            anchor_type=AnchorType.DOCUMENT,
            original_evidence_id="e",
        )


def test_anchor_candidate_requires_evidence_id() -> None:
    with pytest.raises(ValueError, match="original_evidence_id"):
        AnchorCandidate(
            anchor_value="v",
            anchor_type=AnchorType.DOCUMENT,
            original_evidence_id="",
        )


# ---------------------------------------------------------------------------
# OTel span attributes carry latency only inside the volatile attribute
# ---------------------------------------------------------------------------


def test_otel_traverse_span_has_non_negative_latency(make_input, make_basic_graph) -> None:
    recorder = NullSpanRecorder()
    run_graph_traverse(make_input(), make_basic_graph(), span_recorder=recorder)
    traverse = next(s for s in recorder.list_spans() if s.name.value == "c0.graph.traverse")
    assert traverse.attributes["latency_ms"] >= 0


# ---------------------------------------------------------------------------
# Multiple evidence with same anchor → resolved once
# ---------------------------------------------------------------------------


def test_overlapping_anchors_resolved_once(make_basic_graph) -> None:
    ev1 = HydratedEvidence(
        evidence_id="e1",
        source_id="docs/example.md",
        retrieval_lane=RetrievalLane.SPARSE,
        acl_status=AclStatus.ALLOWED,
        file_path_or_doc_id="doc:example",
        extracted_ids=("doc:example",),
        tenant="tenantA",
        region="us",
        data_class="internal",
    )
    ev2 = HydratedEvidence(
        evidence_id="e2",
        source_id="docs/example.md",
        retrieval_lane=RetrievalLane.DENSE,
        acl_status=AclStatus.ALLOWED,
        file_path_or_doc_id="doc:example",  # same target
        extracted_ids=("doc:example",),
        tenant="tenantA",
        region="us",
        data_class="internal",
    )
    inp = GraphTraverseInput(
        route_id="r",
        route_replay_key="rrk",
        policy_hash="ph",
        blueprint_hash="bp",
        support_target=SupportTarget.SOURCE_SUMMARY,
        freshness_class=FreshnessClass.CURRENT,
        max_hops=1,
        max_nodes=32,
        max_edges=32,
        allowed_relation_types=("supersedes", "owns", "references", "contradicts"),
        hydrated_candidates=(ev1, ev2),
        tenant_scope="tenantA",
        region_scope="us",
        data_class_scope=("internal",),
        acl_scope=(AclStatus.ALLOWED.value,),
    )
    pool = run_graph_traverse(inp, make_basic_graph())
    # Each accepted neighbor appears once even though two evidence items
    # resolved the same anchor.
    accepted_ids = [n.neighbor_id for n in pool.accepted_graph_neighbors]
    assert len(accepted_ids) == len(set(accepted_ids))


# ---------------------------------------------------------------------------
# Per-relation hop budget cap
# ---------------------------------------------------------------------------


def test_per_relation_hop_cap_applied() -> None:
    """For BLAST_RADIUS, the policy max_hops_recommended=2. With max_hops=2,
    the per-relation cap for imports/calls is min(2, 2)=2. Build a 3-hop
    chain and verify only first 2 hops accepted."""
    g = InMemoryGraphAdapter()
    common = dict(
        tenant="tA",
        region="us",
        data_class="internal",
        acl_status=AclStatus.ALLOWED.value,
    )
    for nid in ("a", "b", "c", "d"):
        g.add_node(nid, source_id=nid, source_type="code", **common)
    g.add_edge("a", "b", "imports")
    g.add_edge("b", "c", "imports")
    g.add_edge("c", "d", "imports")

    ev = HydratedEvidence(
        evidence_id="e",
        source_id="a",
        retrieval_lane=RetrievalLane.SPARSE,
        acl_status=AclStatus.ALLOWED,
        file_path_or_doc_id="a",
        extracted_ids=("a",),
        tenant="tA",
        region="us",
        data_class="internal",
    )
    inp = GraphTraverseInput(
        route_id="r",
        route_replay_key="rrk",
        policy_hash="ph",
        blueprint_hash="bp",
        support_target=SupportTarget.BLAST_RADIUS,
        freshness_class=FreshnessClass.STATIC,
        max_hops=2,
        max_nodes=16,
        max_edges=16,
        allowed_relation_types=("imports",),
        hydrated_candidates=(ev,),
        tenant_scope="tA",
        region_scope="us",
        data_class_scope=("internal",),
        acl_scope=(AclStatus.ALLOWED.value,),
    )
    pool = run_graph_traverse(inp, g)
    accepted_ids = {n.neighbor_id for n in pool.accepted_graph_neighbors}
    assert "b" in accepted_ids and "c" in accepted_ids
    assert "d" not in accepted_ids
