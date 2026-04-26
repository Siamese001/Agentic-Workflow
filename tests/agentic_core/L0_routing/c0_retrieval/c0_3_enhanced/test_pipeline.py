"""Phase 8 — pipeline tests."""

from __future__ import annotations

from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced import (
    GraphExpandedEvidencePool,
    SupportTarget,
    run_graph_traverse,
)


def test_c0_3_runs_from_hydrated_candidates(make_input, make_basic_graph) -> None:
    pool = run_graph_traverse(make_input(), make_basic_graph())
    assert isinstance(pool, GraphExpandedEvidencePool)


def test_c0_3_preserves_original_candidates(make_evidence, make_input, make_basic_graph) -> None:
    ev = make_evidence(evidence_id="ev-original")
    pool = run_graph_traverse(make_input(candidates=(ev,)), make_basic_graph())
    assert pool.original_candidates == (ev,)
    assert pool.original_candidates[0].evidence_id == "ev-original"


def test_c0_3_extracts_anchors_from_symbols_entities_and_source_ids(
    make_evidence, make_input, make_basic_graph
) -> None:
    ev = make_evidence(
        extracted_ids=("doc:example",),
        extracted_symbols=("MySymbol",),
        extracted_entities=("MyEntity",),
    )
    pool = run_graph_traverse(make_input(candidates=(ev,)), make_basic_graph())
    assert len(pool.accepted_graph_neighbors) >= 1


def test_c0_3_resolves_exact_anchor(make_input, make_basic_graph) -> None:
    pool = run_graph_traverse(make_input(), make_basic_graph())
    accepted_ids = {n.neighbor_id for n in pool.accepted_graph_neighbors}
    assert "doc:example_v2" in accepted_ids


def test_c0_3_marks_unresolved_anchors_as_gap(make_evidence, make_input, make_basic_graph) -> None:
    ev = make_evidence(
        evidence_id="ev-unresolved",
        file_path_or_doc_id=None,
        extracted_ids=("nonexistent_node_xyz",),
        extracted_symbols=(),
        extracted_entities=(),
    )
    pool = run_graph_traverse(make_input(candidates=(ev,)), make_basic_graph())
    assert any(a.original_evidence_id == "ev-unresolved" for a in pool.unresolved_anchors)


def test_c0_3_builds_plan_from_support_target(make_input, make_basic_graph) -> None:
    pool_summary = run_graph_traverse(
        make_input(support_target=SupportTarget.SOURCE_SUMMARY), make_basic_graph()
    )
    pool_blast = run_graph_traverse(make_input(support_target=SupportTarget.BLAST_RADIUS), make_basic_graph())
    assert (
        pool_summary.graph_traversal_manifest.replay_seed != pool_blast.graph_traversal_manifest.replay_seed
    )


def test_c0_3_emits_graph_expanded_evidence_pool(make_input, make_basic_graph) -> None:
    pool = run_graph_traverse(make_input(), make_basic_graph())
    for attr in (
        "accepted_graph_neighbors",
        "rejected_graph_neighbors",
        "graph_traversal_manifest",
        "contradiction_candidates",
        "supersession_candidates",
        "lineage_edges",
        "dependency_context",
        "ownership_context",
        "implementation_context",
        "runtime_context",
        "instruction_payload_flags",
    ):
        assert hasattr(pool, attr)


def test_c0_3_output_compatible_with_c0_4_input(make_input, make_basic_graph) -> None:
    pool = run_graph_traverse(make_input(), make_basic_graph())
    assert pool.original_candidates
    m = pool.graph_traversal_manifest
    assert m.manifest_hash and m.graph_source and m.projection_version and m.replay_seed


def test_c0_3_zero_max_hops_short_circuits(make_input, make_basic_graph) -> None:
    inp = make_input(max_hops=0, allowed_relation_types=("references",))
    pool = run_graph_traverse(inp, make_basic_graph())
    assert pool.accepted_graph_neighbors == ()
    assert pool.graph_traversal_manifest.hops_used == 0


def test_c0_3_deterministic_manifest_hash_under_replay(make_input, make_basic_graph) -> None:
    inp = make_input()
    pool1 = run_graph_traverse(inp, make_basic_graph())
    pool2 = run_graph_traverse(inp, make_basic_graph())
    assert pool1.graph_traversal_manifest.replay_seed == pool2.graph_traversal_manifest.replay_seed
    assert {n.neighbor_id for n in pool1.accepted_graph_neighbors} == {
        n.neighbor_id for n in pool2.accepted_graph_neighbors
    }
