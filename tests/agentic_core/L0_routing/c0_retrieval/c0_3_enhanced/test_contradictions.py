"""Phase 8 — contradiction + gap tests."""

from __future__ import annotations

from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced import (
    ContradictionType,
    GapType,
    SupportTarget,
    run_graph_traverse,
)


def test_contradiction_neighbor_preserved(make_input, make_basic_graph) -> None:
    pool = run_graph_traverse(make_input(), make_basic_graph())
    accepted_rels = {n.relation_path[-1] for n in pool.accepted_graph_neighbors}
    assert "contradicts" in accepted_rels
    assert pool.contradiction_candidates


def test_supersession_neighbor_preserved(make_input, make_basic_graph) -> None:
    pool = run_graph_traverse(make_input(), make_basic_graph())
    assert pool.supersession_candidates
    sup = pool.supersession_candidates[0]
    assert sup.superseding_source_id


def test_docs_vs_code_conflict_marked(make_input, make_basic_graph) -> None:
    g = make_basic_graph()
    g.add_node(
        "code:fn",
        node_type="function",
        source_id="code/fn.py:1",
        source_type="code",
        tenant="tenantA",
        region="us",
        data_class="internal",
        payload_preview="code body says X",
    )
    g.add_edge("doc:example", "code:fn", "contradicts")
    pool = run_graph_traverse(make_input(), g)
    types = {c.conflict_type for c in pool.contradiction_candidates}
    assert ContradictionType.DOCS_VS_CODE in types


def test_runtime_vs_design_conflict_marked(make_input, make_basic_graph) -> None:
    g = make_basic_graph()
    g.add_node(
        "trace:runtime_conflict",
        node_type="trace",
        source_id="trace/conflict",
        source_type="trace",
        tenant="tenantA",
        region="us",
        data_class="internal",
        payload_preview="runtime claim conflicts with design",
    )
    g.add_edge("doc:example", "trace:runtime_conflict", "contradicts")
    pool = run_graph_traverse(make_input(), g)
    types = {c.conflict_type for c in pool.contradiction_candidates}
    assert ContradictionType.RUNTIME_VS_DESIGN in types


def test_policy_vs_implementation_conflict_marked(make_input, make_basic_graph) -> None:
    g = make_basic_graph()
    g.add_node(
        "policy:p1",
        node_type="policy",
        source_id="policy/p1",
        source_type="policy",
        tenant="tenantA",
        region="us",
        data_class="internal",
        payload_preview="policy says X but impl says Y",
    )
    g.add_edge("doc:example", "policy:p1", "contradicts")
    pool = run_graph_traverse(make_input(support_target=SupportTarget.POLICY_CLAUSE), g)
    types = {c.conflict_type for c in pool.contradiction_candidates}
    assert ContradictionType.POLICY_VS_IMPLEMENTATION in types


def test_missing_runtime_evidence_gap_emitted(make_input, make_evidence) -> None:
    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced import InMemoryGraphAdapter

    g = InMemoryGraphAdapter()
    g.add_node(
        "doc:incident",
        node_type="document",
        source_id="docs/incident.md",
        source_type="docs",
        tenant="tenantA",
        region="us",
        data_class="internal",
    )
    ev = make_evidence(
        evidence_id="e-incident",
        source_id="docs/incident.md",
        file_path_or_doc_id="doc:incident",
        extracted_ids=("doc:incident",),
    )
    pool = run_graph_traverse(
        make_input(
            candidates=(ev,),
            support_target=SupportTarget.INCIDENT_EVIDENCE,
        ),
        g,
    )
    assert any(g.gap_type == GapType.MISSING_RUNTIME_EVIDENCE for g in pool.gap_findings)


def test_missing_implementation_link_gap_emitted(make_input, make_evidence) -> None:
    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced import InMemoryGraphAdapter

    g = InMemoryGraphAdapter()
    g.add_node(
        "code:func",
        node_type="function",
        source_id="code/func.py",
        source_type="code",
        tenant="tenantA",
        region="us",
        data_class="internal",
    )
    ev = make_evidence(
        evidence_id="e-code",
        source_id="code/func.py",
        file_path_or_doc_id="code:func",
        extracted_ids=("code:func",),
    )
    pool = run_graph_traverse(
        make_input(
            candidates=(ev,),
            support_target=SupportTarget.CODE_LOCATION,
        ),
        g,
    )
    assert any(g.gap_type == GapType.MISSING_IMPLEMENTATION_LINK for g in pool.gap_findings)


def test_contradictions_not_dropped_silently(make_input, make_basic_graph) -> None:
    pool = run_graph_traverse(make_input(), make_basic_graph())
    # The basic graph has 1 'contradicts' edge -> at least 1 contradiction.
    assert len(pool.contradiction_candidates) >= 1
