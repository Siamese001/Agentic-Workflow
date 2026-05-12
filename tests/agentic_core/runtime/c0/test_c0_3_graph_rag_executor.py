"""Tests for agentic_core.runtime.c0.c0_3_graph_rag_executor.

Coverage:
  - maybe_run_graph_rag skips when policy is None (NOT_CONFIGURED)
  - maybe_run_graph_rag skips when policy.is_active=False (DEFERRED)
  - maybe_run_graph_rag skips when adapter_ref is empty (NO_ADAPTER_REF)
  - maybe_run_graph_rag skips on failed adapter resolution (ADAPTER_RESOLUTION_FAILED)
  - maybe_run_graph_rag skips when evidence_items is empty (NO_CANDIDATES)
  - maybe_run_graph_rag returns GraphRagResult(executed=True) on success
  - maybe_run_graph_rag fails-soft on run_graph_traverse exception (EXECUTION_ERROR)
  - _hydrate_candidates_from_evidence_items builds correct stubs
  - _build_traverse_input maps policy fields to GraphTraverseInput fields
  - GraphRagResult computed properties (nodes_accepted, contradiction_count, manifest_hash)

W4: chroma-graphrag-core-wiring-gaps-b3f7a1
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.runtime.c0.c0_3_graph_rag_executor import (
    GraphRagResult,
    _build_traverse_input,
    _hydrate_candidates_from_evidence_items,
    maybe_run_graph_rag,
)
from agentic_core.runtime.contracts.route_contract import GraphTraversePolicy, RouteContract
from agentic_core.runtime.contracts.posture import POSTURE_READ_ONLY


# ---------------------------------------------------------------------------
# Minimal stub helpers
# ---------------------------------------------------------------------------


def _make_route(
    *,
    graph_traverse_policy: Optional[GraphTraversePolicy] = None,
    route_id: str = "R3_GROUNDED",
    replay_key: str = "rrk-test",
    route_policy_ref: str = "apps_rg/config/route_profile.yaml",
    signature: str = "sig-abc123",
) -> RouteContract:
    return RouteContract(
        request_id="req-001",
        run_id="run-001",
        app_id="apps_rg",
        trace_id="trace-001",
        route_id=route_id,
        l3_required=False,
        grounding_required=True,
        model_generation_required=True,
        write_authority_present=False,
        replay_key=replay_key,
        route_policy_ref=route_policy_ref,
        signature=signature,
        l5_certification_ref="UNKNOWN",
        graph_traverse_policy=graph_traverse_policy,
    )


def _active_policy(
    *,
    graph_adapter_ref: str = "apps_rg.integrations.c0_graph_adapter",
    max_hops: int = 2,
    max_nodes: int = 50,
    max_edges: int = 100,
    allowed_relation_types: tuple[str, ...] = ("references", "defines", "depends_on"),
) -> GraphTraversePolicy:
    return GraphTraversePolicy(
        graph_expansion_allowed=True,
        max_hops=max_hops,
        max_nodes=max_nodes,
        max_edges=max_edges,
        allowed_relation_types=allowed_relation_types,
        contradiction_scan_enabled=True,
        supersession_scan_enabled=True,
        graph_adapter_ref=graph_adapter_ref,
        live_wiring_deferred=False,
    )


def _deferred_policy() -> GraphTraversePolicy:
    return GraphTraversePolicy(
        graph_expansion_allowed=True,
        live_wiring_deferred=True,
        graph_adapter_ref="apps_rg.integrations.c0_graph_adapter",
    )


@dataclass
class _FakeEvidence:
    evidence_id: str = "ev-001"
    source_ref: str = "src-001"
    content_snippet: str = "Some evidence text"


# ---------------------------------------------------------------------------
# GraphRagResult computed properties
# ---------------------------------------------------------------------------


class TestGraphRagResult:
    def test_no_pool_returns_zero_counts(self) -> None:
        r = GraphRagResult(executed=False, skip_reason="NOT_CONFIGURED")
        assert r.nodes_accepted == 0
        assert r.nodes_rejected == 0
        assert r.contradiction_count == 0
        assert r.manifest_hash == ""

    def test_executed_false_with_pool_yields_counts(self) -> None:
        mock_pool = MagicMock()
        mock_pool.accepted_graph_neighbors = [MagicMock(), MagicMock()]
        mock_pool.rejected_graph_neighbors = [MagicMock()]
        mock_pool.contradiction_candidates = []
        mock_pool.graph_traversal_manifest.manifest_hash = "abc123"
        r = GraphRagResult(executed=True, pool=mock_pool)
        assert r.nodes_accepted == 2
        assert r.nodes_rejected == 1
        assert r.contradiction_count == 0
        assert r.manifest_hash == "abc123"


# ---------------------------------------------------------------------------
# _hydrate_candidates_from_evidence_items
# ---------------------------------------------------------------------------


class TestHydrateCandidates:
    def test_empty_sequence_returns_empty_tuple(self) -> None:
        result = _hydrate_candidates_from_evidence_items([])
        assert result == ()

    def test_single_evidence_item_stubbed_correctly(self) -> None:
        from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.contracts import (
            AclStatus,
            RetrievalLane,
        )

        ev = _FakeEvidence(evidence_id="ev-x", source_ref="src-x", content_snippet="hello")
        stubs = _hydrate_candidates_from_evidence_items([ev])
        assert len(stubs) == 1
        stub = stubs[0]
        assert stub.evidence_id == "ev-x"
        assert stub.source_id == "src-x"
        assert stub.candidate_text_or_payload == "hello"
        assert stub.retrieval_lane == RetrievalLane.GRAPH_SEED
        assert stub.acl_status == AclStatus.CLEARED

    def test_missing_fields_fall_back_gracefully(self) -> None:
        class Bare:
            pass  # no evidence_id, source_ref, content_snippet

        stubs = _hydrate_candidates_from_evidence_items([Bare()])
        assert len(stubs) == 1
        stub = stubs[0]
        assert stub.evidence_id  # falls back to str(id(raw))
        assert stub.source_id == stub.evidence_id  # source_ref absent → same as ev_id
        assert stub.candidate_text_or_payload == ""

    def test_multiple_items_all_stubbed(self) -> None:
        items = [_FakeEvidence(evidence_id=f"ev-{i}") for i in range(5)]
        stubs = _hydrate_candidates_from_evidence_items(items)
        assert len(stubs) == 5
        ids = {s.evidence_id for s in stubs}
        assert ids == {"ev-0", "ev-1", "ev-2", "ev-3", "ev-4"}


# ---------------------------------------------------------------------------
# _build_traverse_input
# ---------------------------------------------------------------------------


class TestBuildTraverseInput:
    def test_maps_policy_limits(self) -> None:
        policy = _active_policy(max_hops=3, max_nodes=75, max_edges=150)
        route = _make_route(graph_traverse_policy=policy)
        stubs = _hydrate_candidates_from_evidence_items([_FakeEvidence()])
        inp = _build_traverse_input(route, policy, stubs)
        assert inp.max_hops == 3
        assert inp.max_nodes == 75
        assert inp.max_edges == 150

    def test_maps_allowed_relation_types(self) -> None:
        rels = ("defines", "references", "calls")
        policy = _active_policy(allowed_relation_types=rels)
        route = _make_route(graph_traverse_policy=policy)
        stubs = _hydrate_candidates_from_evidence_items([_FakeEvidence()])
        inp = _build_traverse_input(route, policy, stubs)
        assert inp.allowed_relation_types == rels

    def test_route_id_passed_through(self) -> None:
        policy = _active_policy()
        route = _make_route(route_id="R3_SPECIAL", graph_traverse_policy=policy)
        stubs = _hydrate_candidates_from_evidence_items([_FakeEvidence()])
        inp = _build_traverse_input(route, policy, stubs)
        assert inp.route_id == "R3_SPECIAL"

    def test_policy_hash_never_empty(self) -> None:
        policy = _active_policy()
        route = _make_route(graph_traverse_policy=policy, signature="")
        stubs = _hydrate_candidates_from_evidence_items([_FakeEvidence()])
        inp = _build_traverse_input(route, policy, stubs)
        assert inp.policy_hash  # falls back to route_id

    def test_blueprint_hash_never_empty(self) -> None:
        policy = _active_policy()
        route = _make_route(graph_traverse_policy=policy, route_policy_ref="")
        stubs = _hydrate_candidates_from_evidence_items([_FakeEvidence()])
        inp = _build_traverse_input(route, policy, stubs)
        assert inp.blueprint_hash  # falls back to route_id

    def test_zero_max_nodes_uses_default(self) -> None:
        policy = _active_policy(max_nodes=0, max_edges=0)
        route = _make_route(graph_traverse_policy=policy)
        stubs = _hydrate_candidates_from_evidence_items([_FakeEvidence()])
        inp = _build_traverse_input(route, policy, stubs)
        assert inp.max_nodes == 200
        assert inp.max_edges == 400


# ---------------------------------------------------------------------------
# maybe_run_graph_rag — skip paths
# ---------------------------------------------------------------------------


class TestMaybeRunGraphRagSkips:
    def test_no_policy_returns_not_configured(self) -> None:
        route = _make_route(graph_traverse_policy=None)
        result = maybe_run_graph_rag(route, [_FakeEvidence()])
        assert not result.executed
        assert result.skip_reason == "NOT_CONFIGURED"

    def test_deferred_policy_returns_deferred(self) -> None:
        route = _make_route(graph_traverse_policy=_deferred_policy())
        result = maybe_run_graph_rag(route, [_FakeEvidence()])
        assert not result.executed
        assert result.skip_reason == "DEFERRED"

    def test_disabled_expansion_returns_deferred(self) -> None:
        policy = GraphTraversePolicy(
            graph_expansion_allowed=False,
            live_wiring_deferred=False,
            graph_adapter_ref="apps_rg.integrations.c0_graph_adapter",
        )
        route = _make_route(graph_traverse_policy=policy)
        result = maybe_run_graph_rag(route, [_FakeEvidence()])
        assert not result.executed
        assert result.skip_reason == "DEFERRED"

    def test_empty_adapter_ref_returns_no_adapter_ref(self) -> None:
        policy = GraphTraversePolicy(
            graph_expansion_allowed=True,
            live_wiring_deferred=False,
            graph_adapter_ref="",
        )
        route = _make_route(graph_traverse_policy=policy)
        result = maybe_run_graph_rag(route, [_FakeEvidence()])
        assert not result.executed
        assert result.skip_reason == "NO_ADAPTER_REF"

    def test_failed_adapter_resolution_returns_adapter_resolution_failed(self) -> None:
        policy = _active_policy(graph_adapter_ref="nonexistent.module.path")
        route = _make_route(graph_traverse_policy=policy)
        result = maybe_run_graph_rag(route, [_FakeEvidence()])
        assert not result.executed
        assert result.skip_reason == "ADAPTER_RESOLUTION_FAILED"
        assert result.error

    def test_empty_evidence_items_returns_no_candidates(self) -> None:
        policy = _active_policy(graph_adapter_ref="nonexistent.module.path")
        route = _make_route(graph_traverse_policy=policy)
        # Pass empty evidence so NO_CANDIDATES fires before adapter resolution
        with patch(
            "agentic_core.runtime.c0.c0_3_graph_rag_executor.resolve_graph_adapter"
        ) as mock_resolve:
            mock_resolve.return_value = MagicMock(
                status=__import__(
                    "agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter_registry",
                    fromlist=["AdapterResolutionStatus"],
                ).AdapterResolutionStatus.RESOLVED,
                adapter=MagicMock(),
            )
            result = maybe_run_graph_rag(route, [])
        assert not result.executed
        assert result.skip_reason == "NO_CANDIDATES"


# ---------------------------------------------------------------------------
# maybe_run_graph_rag — success path (with InMemoryGraphAdapter)
# ---------------------------------------------------------------------------


class TestMaybeRunGraphRagSuccess:
    def test_successful_traversal_with_in_memory_adapter(self) -> None:
        """End-to-end: active policy + InMemoryGraphAdapter → executed=True."""
        from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced import InMemoryGraphAdapter

        adapter = InMemoryGraphAdapter()
        base = dict(tenant=None, region=None, data_class="internal")
        adapter.add_node(
            "doc:seed",
            node_type="document",
            source_id="docs/seed.md",
            source_type="docs",
            span_ref="docs/seed.md#L1",
            payload_preview="seed node",
            **base,
        )
        adapter.add_node(
            "doc:neighbor",
            node_type="document",
            source_id="docs/neighbor.md",
            source_type="docs",
            span_ref="docs/neighbor.md#L1",
            payload_preview="neighbor",
            **base,
        )
        adapter.add_edge("doc:seed", "doc:neighbor", "references")

        adapter_module = MagicMock()
        adapter_module.get_graph_adapter = MagicMock(return_value=adapter)

        with patch(
            "agentic_core.runtime.c0.c0_3_graph_rag_executor.resolve_graph_adapter"
        ) as mock_resolve:
            from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter_registry import (
                AdapterResolutionResult,
                AdapterResolutionStatus,
            )

            mock_resolve.return_value = AdapterResolutionResult(
                status=AdapterResolutionStatus.RESOLVED,
                graph_adapter_ref="fake.adapter",
                adapter=adapter,
            )

            policy = _active_policy(
                graph_adapter_ref="fake.adapter",
                max_hops=1,
                max_nodes=50,
                max_edges=100,
                allowed_relation_types=("references",),
            )
            route = _make_route(graph_traverse_policy=policy)
            ev = _FakeEvidence(
                evidence_id="ev-seed",
                source_ref="docs/seed.md",
                content_snippet="seed content",
            )
            result = maybe_run_graph_rag(route, [ev])

        assert result.executed
        assert result.pool is not None
        assert isinstance(result.manifest_hash, str)
        assert result.manifest_hash  # non-empty

    def test_execution_error_fails_soft(self) -> None:
        with patch(
            "agentic_core.runtime.c0.c0_3_graph_rag_executor.resolve_graph_adapter"
        ) as mock_resolve, patch(
            "agentic_core.runtime.c0.c0_3_graph_rag_executor.run_graph_traverse",
            side_effect=RuntimeError("adapter exploded"),
        ):
            from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter_registry import (
                AdapterResolutionResult,
                AdapterResolutionStatus,
            )

            mock_resolve.return_value = AdapterResolutionResult(
                status=AdapterResolutionStatus.RESOLVED,
                graph_adapter_ref="fake.adapter",
                adapter=MagicMock(),
            )
            policy = _active_policy(graph_adapter_ref="fake.adapter")
            route = _make_route(graph_traverse_policy=policy)
            result = maybe_run_graph_rag(route, [_FakeEvidence()])

        assert not result.executed
        assert result.skip_reason == "EXECUTION_ERROR"
        assert "adapter exploded" in result.error
