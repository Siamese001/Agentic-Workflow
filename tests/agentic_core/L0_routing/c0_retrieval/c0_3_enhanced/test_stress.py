"""Stress + fuzz tests for C0.3 — try to break it.

These tests exercise:
  * pathological graphs (large fan-out, deep chains, dense webs)
  * latency budget exhaustion mid-walk
  * adapter returning duplicate edges across hops
  * neighbor with extreme/degenerate field values
  * concurrent run safety (no shared mutable state)
  * mixed support_target switching on same graph
  * malformed payload preview / unicode / control chars
"""

from __future__ import annotations

import threading
from typing import List

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


# ---------------------------------------------------------------------------
# Pathological graphs
# ---------------------------------------------------------------------------


def _seed_evidence(node_id: str = "root") -> HydratedEvidence:
    return HydratedEvidence(
        evidence_id="e",
        source_id=node_id,
        retrieval_lane=RetrievalLane.SPARSE,
        acl_status=AclStatus.ALLOWED,
        file_path_or_doc_id=node_id,
        extracted_ids=(node_id,),
        tenant="tA",
        region="us",
        data_class="internal",
    )


def _seed_input(
    *, max_hops: int = 2, max_nodes: int = 64, max_edges: int = 128, allowed: tuple = ("references",)
) -> GraphTraverseInput:
    return GraphTraverseInput(
        route_id="r",
        route_replay_key="rrk",
        policy_hash="ph",
        blueprint_hash="bp",
        support_target=SupportTarget.SOURCE_SUMMARY,
        freshness_class=FreshnessClass.STATIC,
        max_hops=max_hops,
        max_nodes=max_nodes,
        max_edges=max_edges,
        max_parent_expansion=64,
        max_child_expansion=64,
        allowed_relation_types=allowed,
        hydrated_candidates=(_seed_evidence(),),
        tenant_scope="tA",
        region_scope="us",
        data_class_scope=("internal",),
        acl_scope=(AclStatus.ALLOWED.value,),
    )


def _common() -> dict:
    return dict(
        tenant="tA",
        region="us",
        data_class="internal",
        acl_status=AclStatus.ALLOWED.value,
    )


def test_high_fan_out_respects_max_nodes() -> None:
    """1000-leaf star graph; max_nodes=10 must cap at 10 edges seen."""
    g = InMemoryGraphAdapter()
    g.add_node("root", source_id="root", source_type="docs", **_common())
    for i in range(1000):
        nid = f"leaf-{i}"
        g.add_node(nid, source_id=nid, source_type="docs", **_common())
        g.add_edge("root", nid, "references")
    pool = run_graph_traverse(_seed_input(max_nodes=10, max_edges=10), g)
    assert pool.graph_traversal_manifest.nodes_seen <= 10
    assert pool.graph_traversal_manifest.edges_seen <= 10


def test_deep_chain_respects_max_hops() -> None:
    """500-deep chain; max_hops=3 must accept exactly 3."""
    g = InMemoryGraphAdapter()
    g.add_node("root", source_id="root", source_type="docs", **_common())
    prev = "root"
    for i in range(500):
        nid = f"n-{i}"
        g.add_node(nid, source_id=nid, source_type="docs", **_common())
        g.add_edge(prev, nid, "references")
        prev = nid
    pool = run_graph_traverse(
        _seed_input(max_hops=3, max_nodes=1000, max_edges=1000),
        g,
    )
    assert pool.graph_traversal_manifest.hops_used <= 3
    accepted_hops = [n.hop_distance for n in pool.accepted_graph_neighbors]
    assert all(h <= 3 for h in accepted_hops)


def test_dense_web_does_not_revisit_or_loop() -> None:
    """Complete graph K10 — every pair connected. Walk must terminate
    without infinite loop and dedup neighbors."""
    g = InMemoryGraphAdapter()
    nodes = [f"v{i}" for i in range(10)]
    for nid in nodes:
        g.add_node(nid, source_id=nid, source_type="docs", **_common())
    for src in nodes:
        for dst in nodes:
            if src != dst:
                g.add_edge(src, dst, "references")
    # Seed at v0.
    ev = _seed_evidence("v0")
    inp = GraphTraverseInput(
        route_id="r",
        route_replay_key="rrk",
        policy_hash="ph",
        blueprint_hash="bp",
        support_target=SupportTarget.SOURCE_SUMMARY,
        freshness_class=FreshnessClass.STATIC,
        max_hops=3,
        max_nodes=200,
        max_edges=200,
        max_parent_expansion=32,
        max_child_expansion=32,
        allowed_relation_types=("references",),
        hydrated_candidates=(ev,),
        tenant_scope="tA",
        region_scope="us",
        data_class_scope=("internal",),
        acl_scope=(AclStatus.ALLOWED.value,),
    )
    pool = run_graph_traverse(inp, g)
    # Each non-seed node must appear AT MOST once in accepted.
    accepted_ids = [n.neighbor_id for n in pool.accepted_graph_neighbors]
    assert len(accepted_ids) == len(set(accepted_ids))
    # Cycle/duplicate rejections must be recorded for the redundant paths.
    rejected_reasons = {r.rejection_reason for r in pool.rejected_graph_neighbors}
    assert RejectionReason.CYCLE_DETECTED in rejected_reasons


# ---------------------------------------------------------------------------
# Latency budget
# ---------------------------------------------------------------------------


def test_zero_latency_budget_does_not_crash() -> None:
    """max_latency_ms=0: walk must short-circuit without crashing."""
    g = InMemoryGraphAdapter()
    g.add_node("a", source_id="a", source_type="docs", **_common())
    g.add_node("b", source_id="b", source_type="docs", **_common())
    g.add_edge("a", "b", "references")
    inp = GraphTraverseInput(
        route_id="r",
        route_replay_key="rrk",
        policy_hash="ph",
        blueprint_hash="bp",
        support_target=SupportTarget.SOURCE_SUMMARY,
        freshness_class=FreshnessClass.STATIC,
        max_hops=3,
        max_nodes=8,
        max_edges=8,
        max_latency_ms=0,  # zero budget
        allowed_relation_types=("references",),
        hydrated_candidates=(_seed_evidence("a"),),
        tenant_scope="tA",
        region_scope="us",
        data_class_scope=("internal",),
        acl_scope=(AclStatus.ALLOWED.value,),
    )
    # Should not crash; may produce empty or partial output.
    pool = run_graph_traverse(inp, g)
    assert pool.graph_traversal_manifest is not None


# ---------------------------------------------------------------------------
# Concurrent safety (no shared mutable state in pipeline)
# ---------------------------------------------------------------------------


def test_concurrent_runs_are_independent() -> None:
    """Two threads running run_graph_traverse on the same adapter must
    produce identical, non-corrupted results."""
    g = InMemoryGraphAdapter()
    g.add_node("a", source_id="a", source_type="docs", **_common())
    g.add_node("b", source_id="b", source_type="docs", **_common())
    g.add_node("c", source_id="c", source_type="docs", **_common())
    g.add_edge("a", "b", "references")
    g.add_edge("a", "c", "supersedes")

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
        hydrated_candidates=(_seed_evidence("a"),),
        tenant_scope="tA",
        region_scope="us",
        data_class_scope=("internal",),
        acl_scope=(AclStatus.ALLOWED.value,),
    )
    results: List = []
    errors: List[BaseException] = []

    def worker() -> None:
        try:
            results.append(run_graph_traverse(inp, g))
        except BaseException as exc:  # noqa: BLE001 — test capture only
            errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)

    assert not errors, f"thread errors: {errors!r}"
    assert len(results) == 8
    # All threads must produce the same manifest_hash.
    hashes = {r.graph_traversal_manifest.manifest_hash for r in results}
    assert len(hashes) == 1


# ---------------------------------------------------------------------------
# Mixed support_target on same graph
# ---------------------------------------------------------------------------


def test_same_graph_under_different_support_targets() -> None:
    g = InMemoryGraphAdapter()
    for nid in ("a", "b", "c"):
        g.add_node(nid, source_id=nid, source_type="code", **_common())
    g.add_edge("a", "b", "imports")
    g.add_edge("a", "c", "calls")

    base = dict(
        route_id="r",
        route_replay_key="rrk",
        policy_hash="ph",
        blueprint_hash="bp",
        freshness_class=FreshnessClass.STATIC,
        max_hops=2,
        max_nodes=8,
        max_edges=8,
        allowed_relation_types=("imports", "calls", "references"),
        hydrated_candidates=(_seed_evidence("a"),),
        tenant_scope="tA",
        region_scope="us",
        data_class_scope=("internal",),
        acl_scope=(AclStatus.ALLOWED.value,),
    )
    pool_blast = run_graph_traverse(GraphTraverseInput(support_target=SupportTarget.BLAST_RADIUS, **base), g)
    pool_summary = run_graph_traverse(
        GraphTraverseInput(support_target=SupportTarget.SOURCE_SUMMARY, **base), g
    )
    # BLAST_RADIUS recommends imports/calls -> primary; SOURCE_SUMMARY does
    # not -> at most secondary.
    blast_primary = [n for n in pool_blast.accepted_graph_neighbors if n.support_contribution == "primary"]
    summary_primary = [
        n for n in pool_summary.accepted_graph_neighbors if n.support_contribution == "primary"
    ]
    assert len(blast_primary) >= 1
    assert all(n.relation_path[-1] not in ("imports", "calls") for n in summary_primary)


# ---------------------------------------------------------------------------
# Unicode / control char payload
# ---------------------------------------------------------------------------


def test_unicode_payload_preview_does_not_crash_security_scanner() -> None:
    g = InMemoryGraphAdapter()
    g.add_node("root", source_id="root", source_type="docs", **_common())
    g.add_node(
        "b",
        source_id="b",
        source_type="docs",
        # Unicode + zero-width + RLO + emoji + ascii control chars
        payload_preview="benign \u200b text \u202e \U0001f600 \x07 ok",
        **_common(),
    )
    g.add_edge("root", "b", "references")
    pool = run_graph_traverse(_seed_input(allowed=("references",)), g)
    accepted_ids = {n.neighbor_id for n in pool.accepted_graph_neighbors}
    assert "b" in accepted_ids


def test_extremely_long_payload_does_not_crash() -> None:
    g = InMemoryGraphAdapter()
    g.add_node("root", source_id="root", source_type="docs", **_common())
    g.add_node(
        "b",
        source_id="b",
        source_type="docs",
        payload_preview="x" * 1_000_000,  # 1 MB string
        **_common(),
    )
    g.add_edge("root", "b", "references")
    # Should complete without OOM / crash.
    pool = run_graph_traverse(_seed_input(allowed=("references",)), g)
    assert pool.graph_traversal_manifest is not None


# ---------------------------------------------------------------------------
# Adapter returning duplicate edges across iterations
# ---------------------------------------------------------------------------


class _DupAdapter(InMemoryGraphAdapter):
    """Returns duplicate edges twice on first call to test edge dedup."""

    def __init__(self) -> None:
        super().__init__()
        self._calls = 0

    def get_neighbors(self, node_id, relation_types, scope, limit):  # type: ignore[override]
        self._calls += 1
        base = super().get_neighbors(node_id, relation_types, scope, limit)
        if self._calls == 1 and base:
            # Return the first edge twice.
            return base + (base[0],)
        return base


def test_adapter_returning_duplicate_edges_is_deduped() -> None:
    g = _DupAdapter()
    g.add_node("root", source_id="root", source_type="docs", **_common())
    g.add_node("b", source_id="b", source_type="docs", **_common())
    g.add_edge("root", "b", "references")
    pool = run_graph_traverse(_seed_input(allowed=("references",)), g)
    accepted_ids = [n.neighbor_id for n in pool.accepted_graph_neighbors]
    # b accepted exactly once even though adapter returned the edge twice.
    assert accepted_ids.count("b") == 1
