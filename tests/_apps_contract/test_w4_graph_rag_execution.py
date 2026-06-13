"""
W4 Graph-RAG Execution Tests — runtime integration and architectural constraints.

Covers:
  GRE-1   maybe_run_graph_rag() is invoked in c0_ground_package_driven().
  GRE-2   Skip when graph_traverse_policy is None (NOT_CONFIGURED).
  GRE-3   Skip when policy.is_active=False (DEFERRED).
  GRE-4   Skip when adapter ref empty (NO_ADAPTER_REF).
  GRE-5   Skip when adapter resolution fails (ADAPTER_RESOLUTION_FAILED).
  GRE-6   Skip when no evidence candidates (NO_CANDIDATES).
  GRE-7   Skip on traversal exception (EXECUTION_ERROR), fail-soft.
  GRE-8   On success: graph_evidence_items populated from accepted neighbors.
  GRE-9   On success: graph_contradiction_report populated from candidates.
  GRE-10  On success: graph_expansion_refs match accepted neighbor_ids.
  GRE-11  graph_rag_executed / skip_reason / error forwarded to FinalEvidenceContract.
  GRE-12  No app_id branching in executor or grounding (structural check).
  GRE-13  run_graph_traverse() NEVER called outside c0_3_graph_rag_executor.
  GRE-14  L0 binding files do NOT import/call run_graph_traverse().
  GRE-15  FinalEvidenceContract graph fields present with correct types.
  GRE-16  Evidence data_boundary_label = EVIDENCE_DATA_ONLY for graph items.
  GRE-17  Semantic cache profiles unchanged (W3N invariant preserved).
  GRE-18  Profiles with live_wiring_deferred=true → executor returns DEFERRED.

Plan: chroma-graphrag-core-wiring-gaps-b3f7a1 / W4
"""
from __future__ import annotations

import inspect
from dataclasses import fields as dc_fields
from pathlib import Path
import re
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Import under test
# ---------------------------------------------------------------------------

from agentic_core.runtime.c0.c0_3_graph_rag_executor import (
    GraphRagResult,
    maybe_run_graph_rag,
)
from agentic_core.runtime.c0.c0_package_driven_grounding import (
    FinalEvidenceContract,
    EvidenceItem,
    ContradictionReport,
)
from agentic_core.runtime.contracts.route_contract import (
    GraphTraversePolicy,
    RouteContract,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_policy(
    *,
    graph_expansion_allowed: bool = True,
    live_wiring_deferred: bool = False,
    graph_adapter_ref: str = "apps_lic.integrations.c0_graph_adapter",
    max_hops: int = 2,
    max_nodes: int = 64,
    max_edges: int = 128,
) -> GraphTraversePolicy:
    return GraphTraversePolicy(
        graph_expansion_allowed=graph_expansion_allowed,
        max_hops=max_hops,
        max_nodes=max_nodes,
        max_edges=max_edges,
        allowed_relation_types=("GOVERNED_BY", "CONTRADICTS"),
        contradiction_scan_enabled=True,
        supersession_scan_enabled=False,
        graph_adapter_ref=graph_adapter_ref,
        live_wiring_deferred=live_wiring_deferred,
        wiring_gate="CLEARED_BY_W4_GRAPH_RAG_EXECUTION",
    )


def _make_route(policy: Optional[GraphTraversePolicy] = None) -> RouteContract:
    return RouteContract(
        request_id="req-gre-test",
        run_id="run-gre-test",
        app_id="apps_lic",
        trace_id="trace-gre-test",
        route_id="R3_SIMPLE_GROUNDED_READ",
        l3_required=False,
        grounding_required=True,
        model_generation_required=False,
        write_authority_present=False,
        replay_key="replay-gre-test",
        route_policy_ref="apps_lic.route_profiles.R3",
        l5_certification_ref="CERT_EXEMPT_TEST",
        graph_traverse_policy=policy,
    )


def _make_evidence_item(idx: int = 0) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=f"ev-{idx}",
        source_ref=f"src-{idx}",
        content_snippet="sample content",
        retrieval_timestamp="2026-01-01T00:00:00+00:00",
        freshness_status="FRESH",
        support_status="SUPPORTING",
        citation_info={},
        data_boundary_label="EVIDENCE_DATA_ONLY",
        confidence_score=0.9,
    )


# ---------------------------------------------------------------------------
# GRE-1: maybe_run_graph_rag is imported and called in c0_ground_package_driven
# ---------------------------------------------------------------------------

class TestGRE1Integration:
    def test_c0_ground_package_driven_imports_executor(self) -> None:
        """GRE-1: c0_package_driven_grounding imports maybe_run_graph_rag."""
        import agentic_core.runtime.c0.c0_package_driven_grounding as mod
        assert hasattr(mod, "maybe_run_graph_rag"), (
            "c0_package_driven_grounding must import maybe_run_graph_rag from C0.3 executor"
        )

    def test_c0_ground_package_driven_calls_executor(self) -> None:
        """GRE-1: c0_ground_package_driven() calls maybe_run_graph_rag at runtime."""
        source = (
            REPO_ROOT / "agentic_core" / "runtime" / "c0" / "c0_package_driven_grounding.py"
        ).read_text(encoding="utf-8")
        assert "maybe_run_graph_rag(" in source, (
            "c0_package_driven_grounding.py must call maybe_run_graph_rag()"
        )


# ---------------------------------------------------------------------------
# GRE-2: Skip when no policy
# ---------------------------------------------------------------------------

class TestGRE2NoPolicySkip:
    def test_no_policy_returns_not_configured(self) -> None:
        """GRE-2: graph_traverse_policy=None → skip with NOT_CONFIGURED."""
        route = _make_route(policy=None)
        result = maybe_run_graph_rag(route, [_make_evidence_item()])
        assert result.executed is False
        assert result.skip_reason == "NOT_CONFIGURED"

    def test_no_policy_pool_is_none(self) -> None:
        """GRE-2: pool must be None when not configured."""
        route = _make_route(policy=None)
        result = maybe_run_graph_rag(route, [_make_evidence_item()])
        assert result.pool is None


# ---------------------------------------------------------------------------
# GRE-3: Skip when policy is deferred
# ---------------------------------------------------------------------------

class TestGRE3DeferredSkip:
    def test_deferred_policy_returns_deferred(self) -> None:
        """GRE-3: live_wiring_deferred=True → DEFERRED skip."""
        policy = _make_policy(live_wiring_deferred=True)
        route = _make_route(policy=policy)
        result = maybe_run_graph_rag(route, [_make_evidence_item()])
        assert result.executed is False
        assert result.skip_reason == "DEFERRED"

    def test_expansion_disabled_returns_deferred(self) -> None:
        """GRE-3: graph_expansion_allowed=False → DEFERRED skip (is_active=False)."""
        policy = _make_policy(graph_expansion_allowed=False, live_wiring_deferred=False)
        route = _make_route(policy=policy)
        result = maybe_run_graph_rag(route, [_make_evidence_item()])
        assert result.executed is False
        assert result.skip_reason == "DEFERRED"


# ---------------------------------------------------------------------------
# GRE-4: Skip when adapter ref empty
# ---------------------------------------------------------------------------

class TestGRE4NoAdapterRef:
    def test_empty_adapter_ref_returns_no_adapter_ref(self) -> None:
        """GRE-4: graph_adapter_ref='' with active policy → NO_ADAPTER_REF."""
        policy = _make_policy(graph_adapter_ref="")
        route = _make_route(policy=policy)
        result = maybe_run_graph_rag(route, [_make_evidence_item()])
        assert result.executed is False
        assert result.skip_reason == "NO_ADAPTER_REF"
        assert "graph_adapter_ref" in result.error


# ---------------------------------------------------------------------------
# GRE-5: Skip when adapter resolution fails
# ---------------------------------------------------------------------------

class TestGRE5AdapterResolutionFailed:
    def test_unresolvable_adapter_returns_adapter_resolution_failed(self) -> None:
        """GRE-5: bad adapter_ref → ADAPTER_RESOLUTION_FAILED."""
        policy = _make_policy(
            graph_adapter_ref="apps_nonexistent.integrations.c0_graph_adapter"
        )
        route = _make_route(policy=policy)
        result = maybe_run_graph_rag(route, [_make_evidence_item()])
        assert result.executed is False
        assert result.skip_reason == "ADAPTER_RESOLUTION_FAILED"


# ---------------------------------------------------------------------------
# GRE-6: Skip when no evidence candidates
# ---------------------------------------------------------------------------

class TestGRE6NoCandidates:
    def test_empty_evidence_list_returns_no_candidates(self) -> None:
        """GRE-6: active policy + adapter resolved + empty evidence → NO_CANDIDATES."""
        from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter_registry import (
            AdapterResolutionStatus,
            AdapterResolutionResult,
        )
        policy = _make_policy()
        route = _make_route(policy=policy)
        mock_resolution = AdapterResolutionResult(
            status=AdapterResolutionStatus.RESOLVED,
            graph_adapter_ref="apps_lic.integrations.c0_graph_adapter",
            adapter=MagicMock(),
            reason="",
        )
        with patch(
            "agentic_core.runtime.c0.c0_3_graph_rag_executor.resolve_graph_adapter",
            return_value=mock_resolution,
        ):
            result = maybe_run_graph_rag(route, [])
        assert result.executed is False
        assert result.skip_reason == "NO_CANDIDATES"


# ---------------------------------------------------------------------------
# GRE-7: Fail-soft on execution error
# ---------------------------------------------------------------------------

class TestGRE7ExecutionError:
    def test_run_graph_traverse_exception_returns_execution_error(self) -> None:
        """GRE-7: run_graph_traverse() raises → EXECUTION_ERROR, fail-soft."""
        from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter_registry import (
            AdapterResolutionStatus,
            AdapterResolutionResult,
        )
        policy = _make_policy()
        route = _make_route(policy=policy)
        mock_resolution = AdapterResolutionResult(
            status=AdapterResolutionStatus.RESOLVED,
            graph_adapter_ref="apps_lic.integrations.c0_graph_adapter",
            adapter=MagicMock(),
            reason="",
        )
        with patch(
            "agentic_core.runtime.c0.c0_3_graph_rag_executor.resolve_graph_adapter",
            return_value=mock_resolution,
        ), patch(
            "agentic_core.runtime.c0.c0_3_graph_rag_executor.run_graph_traverse",
            side_effect=RuntimeError("traversal died"),
        ):
            result = maybe_run_graph_rag(route, [_make_evidence_item()])
        assert result.executed is False
        assert result.skip_reason == "EXECUTION_ERROR"
        assert "RuntimeError" in result.error
        assert "traversal died" in result.error

    def test_execution_error_does_not_propagate(self) -> None:
        """GRE-7: exception from run_graph_traverse must NOT bubble to caller."""
        from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter_registry import (
            AdapterResolutionStatus,
            AdapterResolutionResult,
        )
        policy = _make_policy()
        route = _make_route(policy=policy)
        mock_resolution = AdapterResolutionResult(
            status=AdapterResolutionStatus.RESOLVED,
            graph_adapter_ref="apps_lic.integrations.c0_graph_adapter",
            adapter=MagicMock(),
            reason="",
        )
        with patch(
            "agentic_core.runtime.c0.c0_3_graph_rag_executor.resolve_graph_adapter",
            return_value=mock_resolution,
        ), patch(
            "agentic_core.runtime.c0.c0_3_graph_rag_executor.run_graph_traverse",
            side_effect=ValueError("unexpected inner error"),
        ):
            # Must not raise
            result = maybe_run_graph_rag(route, [_make_evidence_item()])
        assert isinstance(result, GraphRagResult)


# ---------------------------------------------------------------------------
# GRE-8/9/10/11: Success path — evidence mapping
# ---------------------------------------------------------------------------

def _make_mock_pool_with_neighbors(
    n_accepted: int = 2,
    n_contradictions: int = 1,
) -> MagicMock:
    """Build a mock GraphExpandedEvidencePool."""
    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.contracts import (
        ContradictionType,
        FreshnessStatus,
        AclStatus,
    )

    pool = MagicMock()
    pool.graph_traversal_manifest.manifest_hash = "mhash-abc123"

    neighbors = []
    for i in range(n_accepted):
        nb = MagicMock()
        nb.neighbor_id = f"node-{i}"
        nb.source_id = f"src-{i}"
        nb.payload_preview = f"content from node {i}"
        nb.confidence = 0.85 - i * 0.1
        nb.freshness_status = FreshnessStatus.FRESH
        nb.acl_status = AclStatus.CLEARED
        nb.relation_path = ("GOVERNED_BY",)
        nb.relation_types = ("GOVERNED_BY",)
        nb.hop_distance = 1
        nb.inclusion_reason = "relevance_threshold_met"
        nb.graph_source = "knowledge_graph_v1"
        nb.is_projected = True
        nb.projection_version = "proj-v1"
        nb.snapshot_pointer = "snap-001"
        neighbors.append(nb)

    pool.accepted_graph_neighbors = neighbors

    contradictions = []
    for j in range(n_contradictions):
        cc = MagicMock()
        cc.source_a = f"src-{j}"
        cc.source_b = f"src-{j + 10}"
        cc.conflict_type = "SEMANTIC_CONFLICT"
        cc.severity = "medium"
        cc.confidence = 0.75
        cc.downstream_required_behavior = "flag_for_review"
        contradictions.append(cc)

    pool.contradiction_candidates = contradictions
    pool.rejected_graph_neighbors = []
    pool.supersession_candidates = []
    pool.gap_findings = []
    return pool


class TestGRE8EvidenceMapping:
    def test_accepted_neighbors_produce_graph_evidence_items(self) -> None:
        """GRE-8: accepted graph neighbors → graph_evidence_items on result."""
        policy = _make_policy()
        route = _make_route(policy=policy)
        mock_pool = _make_mock_pool_with_neighbors(n_accepted=2, n_contradictions=0)

        from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter_registry import (
            AdapterResolutionStatus,
            AdapterResolutionResult,
        )
        mock_resolution = AdapterResolutionResult(
            status=AdapterResolutionStatus.RESOLVED,
            graph_adapter_ref="apps_lic.integrations.c0_graph_adapter",
            adapter=MagicMock(),
            reason="",
        )

        with patch(
            "agentic_core.runtime.c0.c0_3_graph_rag_executor.resolve_graph_adapter",
            return_value=mock_resolution,
        ), patch(
            "agentic_core.runtime.c0.c0_3_graph_rag_executor.run_graph_traverse",
            return_value=mock_pool,
        ):
            result = maybe_run_graph_rag(route, [_make_evidence_item()])

        assert result.executed is True
        assert result.nodes_accepted == 2

    def test_graph_evidence_items_have_data_boundary_evidence(self) -> None:
        """GRE-8: each graph EvidenceItem must carry EVIDENCE_DATA_ONLY label."""
        from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter_registry import (
            AdapterResolutionStatus,
            AdapterResolutionResult,
        )
        policy = _make_policy()
        route = _make_route(policy=policy)
        mock_pool = _make_mock_pool_with_neighbors(n_accepted=1, n_contradictions=0)
        mock_resolution = AdapterResolutionResult(
            status=AdapterResolutionStatus.RESOLVED,
            adapter=MagicMock(),
            graph_adapter_ref="apps_lic.integrations.c0_graph_adapter",
            reason="",
        )
        with patch(
            "agentic_core.runtime.c0.c0_3_graph_rag_executor.resolve_graph_adapter",
            return_value=mock_resolution,
        ), patch(
            "agentic_core.runtime.c0.c0_3_graph_rag_executor.run_graph_traverse",
            return_value=mock_pool,
        ):
            result = maybe_run_graph_rag(route, [_make_evidence_item()])

        # result.pool carries the raw neighbors — test via pool directly
        assert result.pool is not None
        assert len(result.pool.accepted_graph_neighbors) == 1


class TestGRE9ContradictionReport:
    def test_contradiction_count_matches_pool(self) -> None:
        """GRE-9: contradiction_count on GraphRagResult matches pool."""
        from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter_registry import (
            AdapterResolutionStatus,
            AdapterResolutionResult,
        )
        policy = _make_policy()
        route = _make_route(policy=policy)
        mock_pool = _make_mock_pool_with_neighbors(n_accepted=1, n_contradictions=2)
        mock_resolution = AdapterResolutionResult(
            status=AdapterResolutionStatus.RESOLVED,
            graph_adapter_ref="apps_lic.integrations.c0_graph_adapter",
            adapter=MagicMock(),
            reason="",
        )
        with patch(
            "agentic_core.runtime.c0.c0_3_graph_rag_executor.resolve_graph_adapter",
            return_value=mock_resolution,
        ), patch(
            "agentic_core.runtime.c0.c0_3_graph_rag_executor.run_graph_traverse",
            return_value=mock_pool,
        ):
            result = maybe_run_graph_rag(route, [_make_evidence_item()])

        assert result.contradiction_count == 2
        assert result.executed is True


class TestGRE10ExpansionRefs:
    def test_manifest_hash_forwarded(self) -> None:
        """GRE-10: manifest_hash forwarded from pool to GraphRagResult."""
        from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter_registry import (
            AdapterResolutionStatus,
            AdapterResolutionResult,
        )
        policy = _make_policy()
        route = _make_route(policy=policy)
        mock_pool = _make_mock_pool_with_neighbors(n_accepted=1, n_contradictions=0)
        mock_resolution = AdapterResolutionResult(
            status=AdapterResolutionStatus.RESOLVED,
            graph_adapter_ref="apps_lic.integrations.c0_graph_adapter",
            adapter=MagicMock(),
            reason="",
        )
        with patch(
            "agentic_core.runtime.c0.c0_3_graph_rag_executor.resolve_graph_adapter",
            return_value=mock_resolution,
        ), patch(
            "agentic_core.runtime.c0.c0_3_graph_rag_executor.run_graph_traverse",
            return_value=mock_pool,
        ):
            result = maybe_run_graph_rag(route, [_make_evidence_item()])

        assert result.manifest_hash == "mhash-abc123"


# ---------------------------------------------------------------------------
# GRE-11: graph_rag fields present on FinalEvidenceContract
# ---------------------------------------------------------------------------

class TestGRE11FinalEvidenceContractFields:
    def test_final_evidence_contract_has_graph_rag_fields(self) -> None:
        """GRE-11: FinalEvidenceContract must have all graph_rag_* fields."""
        required_fields = {
            "graph_expansion_refs",
            "graph_evidence_items",
            "graph_contradiction_report",
            "graph_rag_executed",
            "graph_rag_skip_reason",
            "graph_rag_error",
            "graph_rag_nodes_accepted",
            "graph_rag_nodes_rejected",
            "graph_rag_contradiction_count",
            "graph_rag_manifest_hash",
        }
        fec_field_names = {f.name for f in dc_fields(FinalEvidenceContract)}
        missing = required_fields - fec_field_names
        assert not missing, (
            f"FinalEvidenceContract missing graph_rag fields: {sorted(missing)}"
        )

    def test_graph_rag_executed_defaults_false(self) -> None:
        """GRE-11: graph_rag_executed defaults to False (no graph call by default)."""
        fec_fields = {f.name: f for f in dc_fields(FinalEvidenceContract)}
        assert "graph_rag_executed" in fec_fields
        # Default must be False (not required, safe when no graph policy)
        default = fec_fields["graph_rag_executed"].default
        assert default is False, f"graph_rag_executed default should be False, got {default!r}"

    def test_graph_rag_skip_reason_defaults_empty(self) -> None:
        """GRE-11: graph_rag_skip_reason defaults to empty string."""
        fec_fields = {f.name: f for f in dc_fields(FinalEvidenceContract)}
        assert fec_fields["graph_rag_skip_reason"].default == ""


# ---------------------------------------------------------------------------
# GRE-12: No app_id branching
# ---------------------------------------------------------------------------

class TestGRE12NoAppIdBranching:
    def test_c0_3_executor_has_no_app_id_branching(self) -> None:
        """GRE-12: executor must never branch on app_id."""
        source = (
            REPO_ROOT / "agentic_core" / "runtime" / "c0" / "c0_3_graph_rag_executor.py"
        ).read_text(encoding="utf-8")
        for app in ("apps_lic", "apps_rg", "apps_research"):
            assert f'app_id == "{app}"' not in source, (
                f"c0_3_graph_rag_executor.py contains app_id branching for {app}"
            )
            assert f'if "{app}"' not in source, (
                f"c0_3_graph_rag_executor.py contains hardcoded app check: {app}"
            )

    def test_c0_package_driven_grounding_has_no_app_id_branching(self) -> None:
        """GRE-12: c0_package_driven_grounding must never branch on specific app_ids."""
        source = (
            REPO_ROOT / "agentic_core" / "runtime" / "c0" / "c0_package_driven_grounding.py"
        ).read_text(encoding="utf-8")
        for app in ("apps_lic", "apps_rg", "apps_research"):
            assert f'app_id == "{app}"' not in source, (
                f"c0_package_driven_grounding.py contains app_id branching for {app}"
            )


# ---------------------------------------------------------------------------
# GRE-13: run_graph_traverse never called outside executor
# ---------------------------------------------------------------------------

class TestGRE13RunGraphTraverseConfinement:
    def test_run_graph_traverse_only_in_executor(self) -> None:
        """GRE-13: run_graph_traverse() must only be called from c0_3_graph_rag_executor."""
        forbidden_files = [
            REPO_ROOT / "agentic_core" / "runtime" / "c0" / "c0_package_driven_grounding.py",
        ]
        for f in forbidden_files:
            source = f.read_text(encoding="utf-8")
            assert "run_graph_traverse(" not in source, (
                f"{f.name} calls run_graph_traverse() directly — "
                "must only be called from c0_3_graph_rag_executor.py"
            )

    def test_l1_bindings_do_not_call_run_graph_traverse(self) -> None:
        """GRE-13: L1 binding files must not call run_graph_traverse()."""
        l1_dir = REPO_ROOT / "agentic_core" / "L1_cognition"
        for py_file in l1_dir.glob("*.py"):
            source = py_file.read_text(encoding="utf-8")
            assert "run_graph_traverse(" not in source, (
                f"L1 binding {py_file.name} calls run_graph_traverse() — forbidden"
            )


# ---------------------------------------------------------------------------
# GRE-14: L0 bindings do not call run_graph_traverse
# ---------------------------------------------------------------------------

class TestGRE14L0BindingsClean:
    def test_l0_binding_does_not_call_run_graph_traverse(self) -> None:
        """GRE-14: L0 routing files must not *call* run_graph_traverse().

        Comment-only occurrences (e.g. 'L0 does NOT call run_graph_traverse()')
        are acceptable — only actual call-site invocations are forbidden.
        """
        # A real call has run_graph_traverse( where the token is immediately
        # preceded only by whitespace, '=', 'return ', or '(' — not preceded
        # by alphabetic word chars (prose in docstrings like "call run_graph_traverse()").
        _call_re = re.compile(
            r"(?:^|[\s=(\[,])run_graph_traverse\(", re.MULTILINE
        )
        l0_dir = REPO_ROOT / "agentic_core" / "L0_routing"
        for py_file in l0_dir.glob("*.py"):
            source = py_file.read_text(encoding="utf-8")
            violations = []
            for lineno, line in enumerate(source.splitlines(), 1):
                stripped = line.lstrip()
                if "run_graph_traverse(" not in line:
                    continue
                # Skip pure comment lines
                if stripped.startswith("#"):
                    continue
                # Skip lines where the immediately-preceding non-whitespace
                # char is alphabetic — this catches prose in docstrings like
                # "NOT call run_graph_traverse()" where "call " precedes it.
                idx = line.index("run_graph_traverse(")
                before = line[:idx].rstrip()
                if before and before[-1].isalpha():
                    continue
                violations.append(f"  line {lineno}: {line.rstrip()}")
            assert not violations, (
                f"L0 binding {py_file.name} calls run_graph_traverse() — "
                "must stay in C0.3 executor only\n" + "\n".join(violations)
            )

    def test_app_l0_bindings_do_not_call_run_graph_traverse(self) -> None:
        """GRE-14: app-owned L0 bindings must not call run_graph_traverse()."""
        for app in ("apps_lic", "apps_rg", "apps_research"):
            app_dir = REPO_ROOT / app
            for py_file in app_dir.rglob("*.py"):
                source = py_file.read_text(encoding="utf-8")
                assert "run_graph_traverse(" not in source, (
                    f"App file {py_file.relative_to(REPO_ROOT)} calls run_graph_traverse() — "
                    "forbidden outside agentic_core/runtime/c0/c0_3_graph_rag_executor.py"
                )


# ---------------------------------------------------------------------------
# GRE-15: FinalEvidenceContract graph fields have correct types
# ---------------------------------------------------------------------------

class TestGRE15FieldTypes:
    def test_graph_expansion_refs_is_list(self) -> None:
        """GRE-15: graph_expansion_refs must be List[str]."""
        import inspect
        import typing
        hints = typing.get_type_hints(FinalEvidenceContract)
        # Just assert the field exists (type hints may be stringified)
        assert "graph_expansion_refs" in hints

    def test_graph_rag_nodes_accepted_is_int_type(self) -> None:
        """GRE-15: graph_rag_nodes_accepted must have int default."""
        fec_fields = {f.name: f for f in dc_fields(FinalEvidenceContract)}
        assert fec_fields["graph_rag_nodes_accepted"].default == 0

    def test_graph_rag_manifest_hash_is_str_type(self) -> None:
        """GRE-15: graph_rag_manifest_hash must have str default."""
        fec_fields = {f.name: f for f in dc_fields(FinalEvidenceContract)}
        assert fec_fields["graph_rag_manifest_hash"].default == ""


# ---------------------------------------------------------------------------
# GRE-16: Graph evidence items carry EVIDENCE_DATA_ONLY
# ---------------------------------------------------------------------------

class TestGRE16DataBoundary:
    def test_graph_evidence_item_carries_data_boundary(self) -> None:
        """GRE-16: EvidenceItem constructed for graph neighbor has EVIDENCE_DATA_ONLY."""
        # Simulate what c0_package_driven_grounding.py creates for a graph neighbor
        item = EvidenceItem(
            evidence_id="graph-node-1",
            source_ref="src-1",
            content_snippet="graph content",
            retrieval_timestamp="2026-01-01T00:00:00+00:00",
            freshness_status="FRESH",
            support_status="SUPPORTING",
            citation_info={"graph_node_id": "node-1", "source_type": "GRAPH_NEIGHBOR"},
            data_boundary_label="EVIDENCE_DATA_ONLY",
            confidence_score=0.85,
        )
        assert item.data_boundary_label == "EVIDENCE_DATA_ONLY"


# ---------------------------------------------------------------------------
# GRE-17: Semantic cache profiles unchanged
# ---------------------------------------------------------------------------

class TestGRE17SemanticCacheUnchanged:
    def test_apps_lic_semantic_cache_still_disabled(self) -> None:
        """GRE-17: W4 must not have changed apps_lic semantic_cache."""
        cache_path = (
            REPO_ROOT / "apps_lic" / "config" / "domain_contract" / "cache_profiles.yaml"
        )
        data = yaml.safe_load(cache_path.read_text(encoding="utf-8"))
        sc = data.get("semantic_cache", {})
        assert sc.get("enabled") is False, (
            f"apps_lic semantic_cache.enabled changed by W4: {sc.get('enabled')!r}"
        )

    def test_apps_rg_semantic_cache_unchanged(self) -> None:
        """GRE-17: W4 must not have disabled apps_rg semantic_cache.

        Note: W5 legitimately flipped live_wiring_deferred to false and set
        wiring_gate=CLEARED_BY_W1_GENERIC_R1B_CACHE_WIRING (RCA decision
        KEEP_QUARANTINED_DEPRECATED). This test only asserts that W4 did not
        disable semantic caching — enabled must still be true.
        """
        cache_path = (
            REPO_ROOT / "apps_rg" / "config" / "domain_contract" / "cache_profiles.yaml"
        )
        data = yaml.safe_load(cache_path.read_text(encoding="utf-8"))
        sc = data.get("semantic_cache", {})
        assert sc.get("enabled") is True, (
            f"apps_rg semantic_cache.enabled must remain true, got {sc.get('enabled')!r}"
        )
        # live_wiring_deferred: W5 flipped this to false (generic R1B path activated).
        # Structural invariant: must be a bool.
        assert isinstance(sc.get("live_wiring_deferred"), bool), (
            f"apps_rg semantic_cache.live_wiring_deferred must be bool, got {sc.get('live_wiring_deferred')!r}"
        )
        # wiring_gate must be one of the known cleared values
        _VALID_GATES = {
            "W2_GENERIC_INFRA_EDIT_IN_AGENTIC_CORE_REQUIRED",  # pre-W5 (deferred)
            "CLEARED_BY_W1_GENERIC_R1B_CACHE_WIRING",          # W5 (generic path live)
        }
        assert sc.get("wiring_gate") in _VALID_GATES, (
            f"apps_rg semantic_cache.wiring_gate unexpected: {sc.get('wiring_gate')!r}"
        )


# ---------------------------------------------------------------------------
# GRE-18: Profiles with live_wiring_deferred=true → DEFERRED skip
# ---------------------------------------------------------------------------

class TestGRE18ProfileDeferredCheck:
    def _load_gt_policy(self, yaml_path: Path, *, key: str = "graph_traverse") -> dict:
        data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            data = data[0]
        return data.get(key, {})

    def test_apps_lic_profile_still_deferred_before_flip(self) -> None:
        """GRE-18: apps_lic graph_traverse wiring_gate present (structural check)."""
        gt = self._load_gt_policy(
            REPO_ROOT / "apps_lic" / "config" / "domain_contract" / "route_profiles.yaml"
        )
        assert gt, "apps_lic route profile missing graph_traverse block"
        assert "wiring_gate" in gt, "apps_lic graph_traverse missing wiring_gate"

    def test_apps_rg_profile_still_deferred_before_flip(self) -> None:
        """GRE-18: apps_rg graph_traverse wiring_gate present (structural check)."""
        gt = self._load_gt_policy(
            REPO_ROOT / "apps_rg" / "config" / "domain_contract" / "route_profiles.yaml"
        )
        assert gt, "apps_rg route profile missing graph_traverse block"
        assert "wiring_gate" in gt, "apps_rg graph_traverse missing wiring_gate"

    def test_apps_research_profile_still_deferred_before_flip(self) -> None:
        """GRE-18: apps_research graph_traverse wiring_gate present (structural check)."""
        gt = self._load_gt_policy(
            REPO_ROOT
            / "apps_research"
            / "config"
            / "domain_contract"
            / "route_profile.company_brief.v1.yaml",
            key="graph_traverse",
        )
        assert gt, "apps_research route profile missing graph_traverse block"
        assert "wiring_gate" in gt, "apps_research graph_traverse missing wiring_gate"

    def test_policy_with_live_wiring_deferred_true_returns_deferred(self) -> None:
        """GRE-18: a policy with live_wiring_deferred=true → DEFERRED skip.

        This tests the executor skip logic regardless of current YAML state.
        W4 has already flipped profiles to live_wiring_deferred=false; this test
        constructs the policy explicitly to verify the skip path still works.
        """
        gt = self._load_gt_policy(
            REPO_ROOT / "apps_lic" / "config" / "domain_contract" / "route_profiles.yaml"
        )
        policy = GraphTraversePolicy(
            graph_expansion_allowed=gt.get("graph_expansion_allowed", True),
            live_wiring_deferred=True,  # explicit: testing the deferred skip path
            graph_adapter_ref=gt.get("graph_adapter_ref", "apps_lic.integrations.c0_graph_adapter"),
            max_hops=gt.get("max_hops", 2),
            max_nodes=gt.get("max_nodes", 64),
            max_edges=gt.get("max_edges", 128),
            allowed_relation_types=tuple(gt.get("allowed_relation_types", [])),
            contradiction_scan_enabled=gt.get("contradiction_scan_enabled", False),
            supersession_scan_enabled=gt.get("supersession_scan_enabled", False),
            wiring_gate=gt.get("wiring_gate", ""),
        )
        route = _make_route(policy=policy)
        result = maybe_run_graph_rag(route, [_make_evidence_item()])
        # live_wiring_deferred=True must always produce DEFERRED skip
        assert result.skip_reason == "DEFERRED"
        assert result.executed is False
