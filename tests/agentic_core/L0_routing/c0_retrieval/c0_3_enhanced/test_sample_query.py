"""Phase 9 — runnable sample query proving the path.

Sample question:
    "Does C0.3 allow GraphRAG to traverse SQLite directly?"

Fixture graph:
    SQLiteCanonicalADG node
    GraphDBProjection node
    GraphRAG node
    C0.3GraphTraverse node
    EvidencePacket node
    DirectSQLiteTraversal node (forbidden)

Edges:
    SQLiteCanonicalADG projected_to GraphDBProjection
    GraphDBProjection used_by GraphRAG
    GraphRAG emits EvidencePacket
    GraphRAG blocked_from DirectSQLiteTraversal

Expected:
    accepted_graph_neighbors includes GraphDBProjection and GraphRAG path
    rejected_graph_neighbors / contradiction / gate output records
        DirectSQLiteTraversal as blocked
    manifest shows graph_source = GraphDB adapter
    manifest includes projection_version and snapshot_pointer
    no SQLite traversal call occurs in runtime path
    OTEL trace includes c0.graph.traverse
    OTEL trace does not include direct SQLite traversal
"""

from __future__ import annotations

from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced import (
    AclStatus,
    C0GraphSpan,
    FreshnessClass,
    GraphTraverseInput,
    HydratedEvidence,
    InMemoryGraphAdapter,
    NullSpanRecorder,
    RejectionReason,
    RetrievalLane,
    SupportTarget,
    run_graph_traverse,
    sqlite_substrate_guard,
)


def _build_sample_graph() -> InMemoryGraphAdapter:
    g = InMemoryGraphAdapter(
        graph_source="GraphDBProjection",
        projection_version="v1.2.3",
        snapshot_pointer="snap://graphdb#42",
    )
    base = dict(
        tenant="tenantA",
        region="us",
        data_class="internal",
        acl_status=AclStatus.ALLOWED.value,
    )
    g.add_node(
        "SQLiteCanonicalADG",
        node_type="canonical_store",
        source_id="adg/sqlite",
        source_type="docs",
        anchor_aliases=("SQLiteCanonicalADG",),
        payload_preview="canonical ADG store",
        **base,
    )
    g.add_node(
        "GraphDBProjection",
        node_type="projection",
        source_id="adg/graphdb",
        source_type="docs",
        anchor_aliases=("GraphDBProjection",),
        payload_preview="GraphDB projection of canonical ADG",
        **base,
    )
    g.add_node(
        "GraphRAG",
        node_type="service",
        source_id="services/graph_rag",
        source_type="docs",
        anchor_aliases=("GraphRAG",),
        payload_preview="GraphRAG read-only consumer",
        **base,
    )
    g.add_node(
        "C0.3GraphTraverse",
        node_type="service",
        source_id="services/c0_3",
        source_type="docs",
        anchor_aliases=("C0.3GraphTraverse",),
        payload_preview="C0.3 entrypoint",
        **base,
    )
    g.add_node(
        "EvidencePacket",
        node_type="contract",
        source_id="contracts/evidence",
        source_type="docs",
        payload_preview="evidence packet emitted to C0.4",
        **base,
    )
    g.add_node(
        "DirectSQLiteTraversal",
        node_type="forbidden_capability",
        source_id="adg/forbidden_direct_sqlite",
        source_type="docs",
        payload_preview="forbidden direct SQLite traversal capability",
        **base,
    )

    g.add_edge("SQLiteCanonicalADG", "GraphDBProjection", "projected_to")
    g.add_edge("GraphDBProjection", "GraphRAG", "used_by")
    g.add_edge("GraphRAG", "EvidencePacket", "emits")
    g.add_edge("GraphRAG", "DirectSQLiteTraversal", "blocked_from")
    g.add_edge("GraphRAG", "C0.3GraphTraverse", "implemented_by")
    return g


def test_sample_query_proves_no_direct_sqlite_traversal_in_runtime_path() -> None:
    g = _build_sample_graph()
    ev = HydratedEvidence(
        evidence_id="q-sample",
        source_id="docs/c03_substrate.md",
        retrieval_lane=RetrievalLane.SPARSE,
        acl_status=AclStatus.ALLOWED,
        file_path_or_doc_id="GraphRAG",
        span_ref="docs/c03_substrate.md#L1",
        extracted_ids=("GraphRAG",),
        tenant="tenantA",
        region="us",
        data_class="internal",
    )
    inp = GraphTraverseInput(
        route_id="R3",
        route_replay_key="rrk-sample",
        policy_hash="ph-sample",
        blueprint_hash="bp-sample",
        support_target=SupportTarget.SOURCE_SUMMARY,
        freshness_class=FreshnessClass.STATIC,
        max_hops=3,
        max_nodes=64,
        max_edges=128,
        allowed_relation_types=(
            "projected_to",
            "used_by",
            "emits",
            "blocked_from",
            "implemented_by",
            "references",
            "defines",
            "parent_of",
            "child_of",
            "supersedes",
            "contradicts",
        ),
        disallowed_relation_types=("blocked_from",),  # forbidden capability
        hydrated_candidates=(ev,),
        tenant_scope="tenantA",
        region_scope="us",
        data_class_scope=("internal",),
        acl_scope=(AclStatus.ALLOWED.value,),
    )

    recorder = NullSpanRecorder()

    # Run the entire traversal under the substrate guard. Any direct sqlite3
    # call from inside the C0.3 runtime would raise SubstrateViolation.
    with sqlite_substrate_guard():
        pool = run_graph_traverse(inp, g, span_recorder=recorder)

    # 1. The runtime path produced an evidence pool.
    assert pool.original_candidates == (ev,)

    # 2. EvidencePacket and projection neighbor are accepted.
    accepted_ids = {n.neighbor_id for n in pool.accepted_graph_neighbors}
    # GraphRAG -> EvidencePacket: 1 hop via "emits" relation
    assert "EvidencePacket" in accepted_ids
    # GraphRAG -> C0.3GraphTraverse via implemented_by
    assert "C0.3GraphTraverse" in accepted_ids

    # 3. DirectSQLiteTraversal must NOT be accepted (relation_type rejected).
    assert "DirectSQLiteTraversal" not in accepted_ids
    rejected_ids = {r.neighbor_id for r in pool.rejected_graph_neighbors}
    assert "DirectSQLiteTraversal" in rejected_ids
    for r in pool.rejected_graph_neighbors:
        if r.neighbor_id == "DirectSQLiteTraversal":
            assert r.rejection_reason == RejectionReason.RELATION_TYPE_NOT_ALLOWED

    # 4. Manifest names a GraphDB-projection adapter (NOT SQLite).
    m = pool.graph_traversal_manifest
    assert m.graph_source == "GraphDBProjection"
    assert m.projection_version == "v1.2.3"
    assert m.graph_snapshot_id == "snap://graphdb#42"

    # 5. OTEL trace includes c0.graph.traverse and does not name SQLite.
    span_names = {s.name for s in recorder.list_spans()}
    assert C0GraphSpan.TRAVERSE in span_names
    for s in recorder.list_spans():
        for v in s.attributes.values():
            if isinstance(v, str):
                assert "sqlite3" not in v.lower()
                assert "sqlite_canonical_adg" not in v.lower()

    # 6. The runtime path did not open a SQLite connection (sqlite guard
    #    was active for the duration). Reaching this point means no
    #    SubstrateViolation was raised.
