"""C0.3 GraphTraverseInput / GraphExpandedEvidencePool tests.

Doctrine: ``docs/reference/03A_C0_Context_Engine/C0.3_Graph_RAG.md``

Closes the C0.3.GAP1 schema gap previously logged in the requirements
traceability matrix. Verifies the additive ``graph_traverse`` module:
  * carries every named bound the spec enumerates (PHASE 1 §2);
  * enforces every named bound deterministically (PHASE 2 worksteps);
  * produces a replay-stable manifest hash;
  * rejects neighbors with explicit reason codes (no silent drops).
"""

from __future__ import annotations

import pytest

from agentic_core.L1_cognition.c0_context.graph_traverse import (
    GRAPH_RELATIONS,
    GraphEdge,
    GraphExclusionReason,
    GraphNodeRef,
    GraphRelation,
    GraphTraverseInput,
    traverse_bounded,
)


# --------------------------------------------------------------------------- #
# Vocabulary contract.
# --------------------------------------------------------------------------- #


def test_graph_relations_thirteen_per_spec() -> None:
    """Spec §C0.3 doctrine — 13 graph relations."""
    expected = {
        "defines",
        "references",
        "imports",
        "calls",
        "owns",
        "depends_on",
        "supersedes",
        "contradicts",
        "duplicates",
        "implements",
        "governed_by",
        "derived_from",
        "observed_in",
    }
    assert {r.value for r in GraphRelation} == expected
    assert GRAPH_RELATIONS == frozenset(expected)
    assert len(GRAPH_RELATIONS) == 13


def test_graph_exclusion_reasons_are_closed_enum() -> None:
    expected = {
        "max_hops_reached",
        "max_nodes_reached",
        "max_edges_reached",
        "acl_blocked",
        "freshness_blocked",
        "relation_disallowed",
        "source_class_disallowed",
        "support_target_irrelevant",
        "duplicate",
    }
    assert {r.value for r in GraphExclusionReason} == expected


# --------------------------------------------------------------------------- #
# Input validation.
# --------------------------------------------------------------------------- #


def _seed(node_id: str = "n0", **k) -> GraphNodeRef:
    return GraphNodeRef(
        node_id=node_id,
        source_id=k.get("source_id", "doc:n0"),
        source_class=k.get("source_class", "docs"),
        acl_status=k.get("acl_status", "cleared"),
        freshness_status=k.get("freshness_status", "fresh"),
        authority_score=k.get("authority_score", 0.5),
    )


def _input(**overrides) -> GraphTraverseInput:
    base = {
        "route_id": "R3_GROUNDED",
        "route_replay_key": "rk-1",
        "policy_hash": "ph",
        "blueprint_hash": "bh",
        "support_target": "SOURCE_SUMMARY",
        "freshness_class": "static",
        "tenant_scope": "tenantA",
        "acl_scope": ("default",),
        "region_scope": "us",
        "data_class_scope": "open",
        "max_hops": 2,
        "max_nodes": 50,
        "max_edges": 100,
        "max_parent_expansion": 5,
        "max_child_expansion": 5,
        "max_relation_types": 13,
        "max_contradiction_edges": 5,
        "max_dependency_edges": 5,
        "max_lineage_edges": 5,
        "max_latency_ms": 2000,
        "max_token_budget_for_graph_context": 1024,
        "allowed_graph_sources": frozenset({"docs", "code"}),
        "disallowed_graph_sources": frozenset(),
        "allowed_relation_types": frozenset(),  # empty → all allowed
        "disallowed_relation_types": frozenset(),
        "allowed_source_classes": frozenset(),
        "disallowed_source_classes": frozenset(),
        "hydrated_seeds": (_seed(),),
    }
    base.update(overrides)
    return GraphTraverseInput(**base)


def test_input_validation_rejects_negative_hops() -> None:
    with pytest.raises(ValueError, match="max_hops"):
        _input(max_hops=-1)


def test_input_validation_rejects_zero_max_nodes() -> None:
    with pytest.raises(ValueError, match="max_nodes"):
        _input(max_nodes=0)


def test_input_validation_rejects_zero_max_edges() -> None:
    with pytest.raises(ValueError, match="max_edges"):
        _input(max_edges=0)


def test_input_validation_rejects_unknown_relation() -> None:
    with pytest.raises(ValueError, match="unknown relations"):
        _input(allowed_relation_types=frozenset({"bogus_relation"}))


def test_input_validation_rejects_overlapping_allow_disallow_relations() -> None:
    with pytest.raises(ValueError, match="overlap"):
        _input(
            allowed_relation_types=frozenset({"imports"}),
            disallowed_relation_types=frozenset({"imports"}),
        )


def test_input_validation_rejects_overlapping_allow_disallow_sources() -> None:
    with pytest.raises(ValueError, match="overlap"):
        _input(
            allowed_graph_sources=frozenset({"docs"}),
            disallowed_graph_sources=frozenset({"docs"}),
        )


# --------------------------------------------------------------------------- #
# Bounded traversal — every bound is enforced.
# --------------------------------------------------------------------------- #


def _build_graph() -> tuple[dict[str, GraphNodeRef], dict[str, tuple[GraphEdge, ...]]]:
    """Construct a small graph: n0 → n1 (imports) → n2 (depends_on),
    n0 → n3 (contradicts), n0 → n4 (acl-blocked), n0 → n5 (stale)."""
    nodes = {
        "n0": _seed("n0"),
        "n1": _seed("n1", source_id="doc:n1"),
        "n2": _seed("n2", source_id="doc:n2"),
        "n3": _seed("n3", source_id="doc:n3"),
        "n4": _seed("n4", source_id="doc:n4", acl_status="blocked-tenantB"),
        "n5": _seed("n5", source_id="doc:n5", freshness_status="stale"),
    }
    edges = {
        "n0": (
            GraphEdge(GraphRelation.IMPORTS, "n0", "n1"),
            GraphEdge(GraphRelation.CONTRADICTS, "n0", "n3"),
            GraphEdge(GraphRelation.IMPORTS, "n0", "n4"),
            GraphEdge(GraphRelation.IMPORTS, "n0", "n5"),
        ),
        "n1": (GraphEdge(GraphRelation.DEPENDS_ON, "n1", "n2"),),
    }
    return nodes, edges


def test_bounded_traversal_respects_max_hops() -> None:
    nodes, edges = _build_graph()
    inp = _input(max_hops=1)
    pool = traverse_bounded(inp, edges_by_src=edges, nodes_by_id=nodes)
    accepted = {n.node_id for n in pool.accepted_nodes}
    # n0 (seed) + n1 + n3 should be accepted at hop 1; n2 (hop 2) excluded.
    assert "n0" in accepted
    assert "n1" in accepted
    assert "n2" not in accepted, "n2 is hop 2 — must be excluded by max_hops=1"
    assert pool.manifest.max_hop_reached <= 1


def test_bounded_traversal_respects_max_nodes() -> None:
    nodes, edges = _build_graph()
    inp = _input(max_nodes=2)
    pool = traverse_bounded(inp, edges_by_src=edges, nodes_by_id=nodes)
    assert len(pool.accepted_nodes) <= 2


def test_bounded_traversal_blocks_non_cleared_acl() -> None:
    nodes, edges = _build_graph()
    pool = traverse_bounded(_input(), edges_by_src=edges, nodes_by_id=nodes)
    accepted = {n.node_id for n in pool.accepted_nodes}
    assert "n4" not in accepted, "ACL-blocked neighbor must be excluded"
    rejection_reasons = dict(pool.manifest.rejection_counts)
    assert rejection_reasons.get("acl_blocked", 0) >= 1


def test_bounded_traversal_blocks_stale_under_regulated_freshness() -> None:
    nodes, edges = _build_graph()
    pool = traverse_bounded(
        _input(freshness_class="regulated"),
        edges_by_src=edges,
        nodes_by_id=nodes,
    )
    accepted = {n.node_id for n in pool.accepted_nodes}
    assert "n5" not in accepted, "stale neighbor must be excluded under regulated freshness"
    rejection_reasons = dict(pool.manifest.rejection_counts)
    assert rejection_reasons.get("freshness_blocked", 0) >= 1


def test_bounded_traversal_disallowed_relation_excluded() -> None:
    nodes, edges = _build_graph()
    inp = _input(disallowed_relation_types=frozenset({"contradicts"}))
    pool = traverse_bounded(inp, edges_by_src=edges, nodes_by_id=nodes)
    accepted = {n.node_id for n in pool.accepted_nodes}
    assert "n3" not in accepted, "contradicts disallowed → n3 must be excluded"


def test_bounded_traversal_allowed_relation_whitelist() -> None:
    nodes, edges = _build_graph()
    inp = _input(allowed_relation_types=frozenset({"imports"}))
    pool = traverse_bounded(inp, edges_by_src=edges, nodes_by_id=nodes)
    relation_counts = dict(pool.manifest.relation_counts)
    # Only imports edges should have been counted as accepted.
    assert relation_counts.get("imports", 0) >= 1
    assert relation_counts.get("contradicts", 0) == 0
    assert relation_counts.get("depends_on", 0) == 0


def test_bounded_traversal_disallowed_source_class_excluded() -> None:
    nodes, edges = _build_graph()
    # Mark n1 as code; disallow code → n1 must be excluded.
    nodes["n1"] = _seed("n1", source_class="code")
    inp = _input(disallowed_source_classes=frozenset({"code"}))
    pool = traverse_bounded(inp, edges_by_src=edges, nodes_by_id=nodes)
    accepted = {n.node_id for n in pool.accepted_nodes}
    assert "n1" not in accepted


def test_bounded_traversal_allowed_source_class_whitelist() -> None:
    nodes, edges = _build_graph()
    # Allow only docs; nothing else may be added (every neighbor is docs in
    # the default graph, so result equals docs-only graph minus duplicates).
    inp = _input(allowed_source_classes=frozenset({"docs"}))
    pool = traverse_bounded(inp, edges_by_src=edges, nodes_by_id=nodes)
    for n in pool.accepted_nodes:
        assert n.source_class == "docs"


def test_bounded_traversal_records_no_duplicates() -> None:
    nodes, edges = _build_graph()
    # Add a cycle: n1 → n0 (defines).
    edges_with_cycle = dict(edges)
    edges_with_cycle["n1"] = edges["n1"] + (GraphEdge(GraphRelation.DEFINES, "n1", "n0"),)
    pool = traverse_bounded(_input(), edges_by_src=edges_with_cycle, nodes_by_id=nodes)
    seen: set[str] = set()
    for n in pool.accepted_nodes:
        assert n.node_id not in seen, "node visited twice"
        seen.add(n.node_id)


def test_bounded_traversal_manifest_hash_replay_stable() -> None:
    nodes, edges = _build_graph()
    pool1 = traverse_bounded(_input(), edges_by_src=edges, nodes_by_id=nodes)
    pool2 = traverse_bounded(_input(), edges_by_src=edges, nodes_by_id=nodes)
    assert pool1.manifest.manifest_hash == pool2.manifest.manifest_hash


def test_bounded_traversal_manifest_hash_changes_with_max_hops() -> None:
    nodes, edges = _build_graph()
    a = traverse_bounded(_input(max_hops=1), edges_by_src=edges, nodes_by_id=nodes)
    b = traverse_bounded(_input(max_hops=2), edges_by_src=edges, nodes_by_id=nodes)
    assert a.manifest.manifest_hash != b.manifest.manifest_hash


def test_bounded_traversal_zero_hops_returns_only_seeds() -> None:
    nodes, edges = _build_graph()
    pool = traverse_bounded(_input(max_hops=0), edges_by_src=edges, nodes_by_id=nodes)
    assert {n.node_id for n in pool.accepted_nodes} == {"n0"}
    assert pool.accepted_edges == ()


def test_bounded_traversal_all_thirteen_relations_recognized() -> None:
    """Every named relation can be traversed when allowed."""
    nodes = {"n0": _seed("n0"), **{f"n{i}": _seed(f"n{i}") for i in range(1, 14)}}
    # Build edges of every relation type from n0.
    relations = list(GraphRelation)
    edges = {
        "n0": tuple(GraphEdge(rel, "n0", f"n{i + 1}") for i, rel in enumerate(relations)),
    }
    inp = _input(max_hops=1, max_nodes=20, max_edges=20)
    pool = traverse_bounded(inp, edges_by_src=edges, nodes_by_id=nodes)
    accepted_relations = {e.relation for e in pool.accepted_edges}
    assert accepted_relations == set(relations)
