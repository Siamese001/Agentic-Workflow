"""Deep hardening tests for the C0 Context Engine.

Categories:
  1. Plan immutability (refinement does not mutate source plan)
  2. Determinism (same inputs -> same outputs)
  3. ACL escape regression (no tactic widens ACL/tenant)
  4. C0.1 budget/limit propagation across refinement
  5. Status -> disposition transition matrix
  6. Boundary cases (empty query, single doc, threshold edges)
  7. End-to-end C0.1 -> C0.6 pipeline integration
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any

import pytest

from agentic_core.knowledge.retrieval.evidence_contract_builder import (
    ContradictionStatus,
    EvidenceClass,
    EvidenceContractBuilder,
    EvidenceStatus,
    RecommendedDisposition,
    RefinementDiagnostic,
    RefinementTactic,
    VerifiedChunk,
)
from agentic_core.knowledge.retrieval.retrieval_plan import (
    RetrievalMode,
    RetrievalPlan,
    SupportTarget,
    WeakSupportPolicy,
)


@dataclass
class StubDoc:
    doc_id: str
    content: str = "stub content"
    score: float = 0.9
    source: str = "dense"
    metadata: dict[str, Any] = field(default_factory=dict)


def _baseline_plan(**overrides: Any) -> RetrievalPlan:
    """Plan with rich C0.1 fields for hardening assertions."""
    base: dict[str, Any] = {
        "query_id": "q-baseline",
        "retrieval_mode": RetrievalMode.HYBRID,
        "tenant_id": "acme",
        "region": "EU",
        "allowed_principals": ["user:alice", "role:analyst"],
        "source_collections": ["docs", "policy"],
        "disallowed_sources": ["legacy_archive"],
        "top_k": 20,
        "support_target": SupportTarget.SOURCE_BACKED_SUMMARY,
        "weak_support_policy": WeakSupportPolicy.REFINE_ONCE,
        "max_parent_expansion": 4,
        "max_graph_hops": 3,
        "max_refine_attempts": 3,
        "slo_budget_ms": 8000,
        "token_budget": 6000,
        "latency_budget_ms": 4000,
        "cost_budget_usd": 0.05,
        "replay_key": "rk-1",
        "policy_hash": "ph-1",
    }
    base.update(overrides)
    return RetrievalPlan(**base)


def _make_contract(
    refine_attempt: int = 0,
    verified_chunks: list[VerifiedChunk] | None = None,
) -> Any:
    from agentic_core.knowledge.retrieval.evidence_contract_builder import (
        EvidenceContract,
    )
    return EvidenceContract(
        query_id="q-baseline",
        verified_chunks=verified_chunks or [],
        status=EvidenceStatus.WEAK,
        refine_attempt=refine_attempt,
        max_refine_attempts=3,
    )


# ===========================================================================
# 1. Plan Immutability — refinement MUST NOT mutate the source plan
# ===========================================================================


class TestPlanImmutability:

    def setup_method(self) -> None:
        self.builder = EvidenceContractBuilder()

    @pytest.mark.parametrize("tactic", [
        RefinementTactic.REWRITE,
        RefinementTactic.BROADEN,
        RefinementTactic.NARROW,
        RefinementTactic.DECOMPOSE,
    ])
    def test_source_plan_unchanged_after_refinement(self, tactic: str) -> None:
        plan = _baseline_plan()
        snapshot = copy.deepcopy(plan)
        self.builder.execute_refinement_tactic(
            tactic, _make_contract(), plan, "what about cats and dogs",
        )
        # Every single field must be unchanged on the source plan
        for f in [
            "tenant_id", "region", "allowed_principals", "source_collections",
            "disallowed_sources", "top_k", "support_target",
            "weak_support_policy", "max_parent_expansion", "max_graph_hops",
            "max_refine_attempts", "slo_budget_ms", "token_budget",
            "latency_budget_ms", "cost_budget_usd", "max_freshness_band",
            "replay_key", "policy_hash", "retrieval_mode",
        ]:
            assert getattr(plan, f) == getattr(snapshot, f), (
                f"tactic={tactic} mutated source plan.{f}: "
                f"before={getattr(snapshot, f)!r} after={getattr(plan, f)!r}"
            )

    def test_source_plan_metadata_unchanged(self) -> None:
        plan = _baseline_plan(metadata={"req": "r1", "trace": "t1"})
        original_metadata = dict(plan.metadata)
        self.builder.execute_refinement_tactic(
            RefinementTactic.REWRITE, _make_contract(), plan, "q",
        )
        assert plan.metadata == original_metadata
        # Source must not have been tagged with refinement_of
        assert "refinement_of" not in plan.metadata

    def test_refined_plan_has_new_plan_id(self) -> None:
        plan = _baseline_plan()
        result = self.builder.execute_refinement_tactic(
            RefinementTactic.REWRITE, _make_contract(), plan, "q",
        )
        refined = result["refined_plan"]
        assert refined.plan_id != plan.plan_id
        assert refined.metadata["refinement_of"] == plan.plan_id


# ===========================================================================
# 2. Determinism — same inputs -> same outputs
# ===========================================================================


class TestDeterminism:

    def setup_method(self) -> None:
        self.builder = EvidenceContractBuilder()
        self.docs = [
            StubDoc(
                doc_id=f"d{i}",
                score=0.9 - i * 0.05,
                content=f"content {i}" * 10,
                metadata={"source_id": f"src_{i}", "rerank_score": 0.9 - i * 0.05},
            )
            for i in range(5)
        ]

    def test_build_contract_deterministic(self) -> None:
        c1 = self.builder.build_contract("q1", "test query", list(self.docs))
        c2 = self.builder.build_contract("q1", "test query", list(self.docs))
        assert c1.status == c2.status
        assert c1.support_score == c2.support_score
        assert c1.coverage_score == c2.coverage_score
        assert c1.source_ids == c2.source_ids
        assert c1.evidence_classes == c2.evidence_classes
        assert c1.recommended_disposition == c2.recommended_disposition
        assert len(c1.verified_chunks) == len(c2.verified_chunks)
        assert c1.prompt_budget_hint["packing_order"] == \
            c2.prompt_budget_hint["packing_order"]

    def test_rewrite_tactic_deterministic(self) -> None:
        plan = _baseline_plan()
        r1 = self.builder.execute_refinement_tactic(
            RefinementTactic.REWRITE, _make_contract(), plan,
            "what is the meaning of the answer",
        )
        r2 = self.builder.execute_refinement_tactic(
            RefinementTactic.REWRITE, _make_contract(), plan,
            "what is the meaning of the answer",
        )
        assert r1["new_query"] == r2["new_query"]


# ===========================================================================
# 3. ACL Escape Regression — no tactic widens ACL/tenant/region
# ===========================================================================


class TestACLEscapeRegression:

    def setup_method(self) -> None:
        self.builder = EvidenceContractBuilder()
        self.original = _baseline_plan(
            tenant_id="locked-tenant",
            region="restricted-region",
            allowed_principals=["user:only-bob"],
            disallowed_sources=["never-touch-this"],
        )

    @pytest.mark.parametrize("tactic", [
        RefinementTactic.REWRITE,
        RefinementTactic.BROADEN,
        RefinementTactic.NARROW,
        RefinementTactic.DECOMPOSE,
    ])
    def test_tenant_never_widens(self, tactic: str) -> None:
        chunks = [
            VerifiedChunk(
                chunk_id="c1", content="x", source_id="src_a",
                citation_anchor="a", support_score=0.9, is_must_use=True,
            ),
        ]
        result = self.builder.execute_refinement_tactic(
            tactic, _make_contract(verified_chunks=chunks), self.original,
            "thing and other thing",
        )
        refined = result.get("refined_plan")
        if refined is None:
            return
        assert refined.tenant_id == "locked-tenant"

    @pytest.mark.parametrize("tactic", [
        RefinementTactic.REWRITE,
        RefinementTactic.BROADEN,
        RefinementTactic.NARROW,
        RefinementTactic.DECOMPOSE,
    ])
    def test_region_never_widens(self, tactic: str) -> None:
        result = self.builder.execute_refinement_tactic(
            tactic, _make_contract(), self.original, "alpha and beta",
        )
        refined = result.get("refined_plan")
        if refined is None:
            return
        assert refined.region == "restricted-region"

    @pytest.mark.parametrize("tactic", [
        RefinementTactic.REWRITE,
        RefinementTactic.BROADEN,
        RefinementTactic.NARROW,
        RefinementTactic.DECOMPOSE,
    ])
    def test_allowed_principals_never_widens(self, tactic: str) -> None:
        result = self.builder.execute_refinement_tactic(
            tactic, _make_contract(), self.original, "a and b",
        )
        refined = result.get("refined_plan")
        if refined is None:
            return
        # Refined must be subset of (or equal to) original principals
        assert set(refined.allowed_principals) <= {"user:only-bob"}

    @pytest.mark.parametrize("tactic", [
        RefinementTactic.REWRITE,
        RefinementTactic.BROADEN,
        RefinementTactic.NARROW,
        RefinementTactic.DECOMPOSE,
    ])
    def test_disallowed_sources_never_dropped(self, tactic: str) -> None:
        result = self.builder.execute_refinement_tactic(
            tactic, _make_contract(), self.original, "a and b",
        )
        refined = result.get("refined_plan")
        if refined is None:
            return
        # Disallowed entries must be retained (denylist preserved)
        assert "never-touch-this" in refined.disallowed_sources


# ===========================================================================
# 4. Budget & Limit Propagation across refinement
# ===========================================================================


class TestBudgetAndLimitPropagation:

    def setup_method(self) -> None:
        self.builder = EvidenceContractBuilder()

    @pytest.mark.parametrize("tactic", [
        RefinementTactic.REWRITE,
        RefinementTactic.BROADEN,
        RefinementTactic.NARROW,
        RefinementTactic.DECOMPOSE,
    ])
    def test_budgets_propagate(self, tactic: str) -> None:
        plan = _baseline_plan(
            slo_budget_ms=12345,
            token_budget=7777,
            latency_budget_ms=4444,
            cost_budget_usd=0.123,
        )
        result = self.builder.execute_refinement_tactic(
            tactic, _make_contract(), plan, "alpha and beta",
        )
        refined = result.get("refined_plan")
        if refined is None:
            return
        assert refined.slo_budget_ms == 12345
        assert refined.token_budget == 7777
        assert refined.latency_budget_ms == 4444
        assert refined.cost_budget_usd == 0.123

    @pytest.mark.parametrize("tactic", [
        RefinementTactic.REWRITE,
        RefinementTactic.BROADEN,
        RefinementTactic.NARROW,
        RefinementTactic.DECOMPOSE,
    ])
    def test_limits_propagate(self, tactic: str) -> None:
        plan = _baseline_plan(
            max_parent_expansion=7,
            max_graph_hops=5,
            max_refine_attempts=4,
        )
        result = self.builder.execute_refinement_tactic(
            tactic, _make_contract(), plan, "alpha and beta",
        )
        refined = result.get("refined_plan")
        if refined is None:
            return
        assert refined.max_parent_expansion == 7
        assert refined.max_graph_hops == 5
        assert refined.max_refine_attempts == 4

    @pytest.mark.parametrize("tactic", [
        RefinementTactic.REWRITE,
        RefinementTactic.BROADEN,
        RefinementTactic.NARROW,
        RefinementTactic.DECOMPOSE,
    ])
    def test_support_target_propagates(self, tactic: str) -> None:
        plan = _baseline_plan(support_target=SupportTarget.POLICY_CLAUSE)
        result = self.builder.execute_refinement_tactic(
            tactic, _make_contract(), plan, "alpha and beta",
        )
        refined = result.get("refined_plan")
        if refined is None:
            return
        assert refined.support_target == SupportTarget.POLICY_CLAUSE


# ===========================================================================
# 5. Status -> Disposition transition matrix
# ===========================================================================


class TestStatusDispositionMatrix:

    def setup_method(self) -> None:
        self.builder = EvidenceContractBuilder(
            min_coverage_to_proceed=0.30,
        )

    @pytest.mark.parametrize("status,coverage,expected", [
        (EvidenceStatus.PASS, 0.9, RecommendedDisposition.PROCEED),
        (EvidenceStatus.PASS, 0.5, RecommendedDisposition.PROCEED),
        (EvidenceStatus.WEAK_WITH_CAVEATS, 0.5, RecommendedDisposition.CAVEAT),
        (EvidenceStatus.WEAK_WITH_CAVEATS, 0.1, RecommendedDisposition.CAVEAT),
        (EvidenceStatus.CONFLICTED, 0.5, RecommendedDisposition.CAVEAT),
        (EvidenceStatus.CONFLICTED, 0.1, RecommendedDisposition.CAVEAT),
        (EvidenceStatus.EMPTY, 0.5, RecommendedDisposition.ABSTAIN),
        (EvidenceStatus.EMPTY, 0.0, RecommendedDisposition.ABSTAIN),
        (EvidenceStatus.BLOCKED, 0.5, RecommendedDisposition.ABSTAIN),
        (EvidenceStatus.BLOCKED, 0.0, RecommendedDisposition.ABSTAIN),
        (EvidenceStatus.WEAK, 0.25, RecommendedDisposition.CAVEAT),  # > threshold/2
        (EvidenceStatus.WEAK, 0.10, RecommendedDisposition.REROUTE),  # < threshold/2
        (EvidenceStatus.WEAK, 0.05, RecommendedDisposition.REROUTE),
    ])
    def test_full_status_disposition_matrix(
        self, status: str, coverage: float, expected: str,
    ) -> None:
        result = self.builder._decide_disposition(status, "none", coverage)
        assert result == expected, (
            f"status={status} coverage={coverage} -> got={result} expected={expected}"
        )


# ===========================================================================
# 6. Boundary & malformed cases
# ===========================================================================


class TestBoundaryCases:

    def setup_method(self) -> None:
        self.builder = EvidenceContractBuilder()

    def test_empty_query_does_not_crash_rewrite(self) -> None:
        result = self.builder.execute_refinement_tactic(
            RefinementTactic.REWRITE, _make_contract(), _baseline_plan(), "",
        )
        # Empty query — new_query falls back to ""
        assert result["new_query"] == ""
        assert result["abstain"] is False

    def test_only_stopwords_returns_original_query(self) -> None:
        result = self.builder.execute_refinement_tactic(
            RefinementTactic.REWRITE, _make_contract(), _baseline_plan(),
            "the a an of",
        )
        # All stopwords -> falls back to original query
        assert result["new_query"] == "the a an of"

    def test_decompose_with_no_split_falls_through_to_broaden(self) -> None:
        result = self.builder.execute_refinement_tactic(
            RefinementTactic.DECOMPOSE, _make_contract(), _baseline_plan(),
            "single query no conjunction",
        )
        assert result["tactic"] == RefinementTactic.BROADEN

    def test_decompose_top_k_floor_3(self) -> None:
        plan = _baseline_plan(top_k=2)  # Below floor
        result = self.builder.execute_refinement_tactic(
            RefinementTactic.DECOMPOSE, _make_contract(), plan,
            "x and y and z and w",
        )
        # Each sub-plan: max(2 // 4, 3) = 3
        for sub in result["decomposed_plans"]:
            assert sub.top_k == 3

    def test_narrow_top_k_floor_5(self) -> None:
        plan = _baseline_plan(top_k=4)
        result = self.builder.execute_refinement_tactic(
            RefinementTactic.NARROW, _make_contract(), plan, "q",
        )
        # max(4 // 2, 5) = 5
        assert result["refined_plan"].top_k == 5

    def test_broaden_top_k_ceiling_100(self) -> None:
        plan = _baseline_plan(top_k=80)
        result = self.builder.execute_refinement_tactic(
            RefinementTactic.BROADEN, _make_contract(), plan, "q",
        )
        # min(80*2, 100) = 100
        assert result["refined_plan"].top_k == 100

    def test_narrow_with_no_must_use_chunks_keeps_original_collections(self) -> None:
        # No must_use chunks (or none with valid source_id)
        plan = _baseline_plan(source_collections=["original_a", "original_b"])
        result = self.builder.execute_refinement_tactic(
            RefinementTactic.NARROW, _make_contract(), plan, "q",
        )
        assert result["refined_plan"].source_collections == ["original_a", "original_b"]

    def test_unknown_status_falls_through_to_proceed(self) -> None:
        # Unknown status string
        result = self.builder._decide_disposition("not-a-status", "none", 0.5)
        assert result == RecommendedDisposition.PROCEED

    def test_unknown_status_with_contradiction_returns_caveat(self) -> None:
        result = self.builder._decide_disposition(
            "not-a-status", ContradictionStatus.CONFLICTING, 0.5,
        )
        assert result == RecommendedDisposition.CAVEAT

    def test_build_contract_with_empty_docs_returns_empty_status(self) -> None:
        contract = self.builder.build_contract("q1", "test", [])
        assert contract.status == EvidenceStatus.EMPTY
        assert contract.recommended_disposition == RecommendedDisposition.ABSTAIN
        assert contract.cited_spans == []
        assert contract.source_ids == []
        assert contract.evidence_classes == {}

    def test_build_contract_freshness_report_handles_missing_metadata(self) -> None:
        docs = [StubDoc(doc_id="d1", metadata={})]  # No source_id
        contract = self.builder.build_contract("q1", "test", docs)
        # Should not crash; freshness_report has empty by_source
        assert "by_source" in contract.freshness_report
        assert contract.freshness_report["fresh_count"] + contract.freshness_report["stale_count"] >= 0


# ===========================================================================
# 7. End-to-end pipeline integration C0.1 -> C0.5 -> C0.6
# ===========================================================================


class TestEndToEndPipeline:
    """Walk the full C0 contract: plan -> recall -> contract -> refinement."""

    def setup_method(self) -> None:
        self.builder = EvidenceContractBuilder()

    def test_pass_path_proceeds_no_refinement_needed(self) -> None:
        plan = _baseline_plan()
        # Strong evidence
        docs = [
            StubDoc(
                doc_id=f"d{i}", score=0.95, content=f"strong content about retrieval {i}" * 5,
                metadata={
                    "source_id": f"src_{i}",
                    "rerank_score": 0.95,
                    "freshness_band": "warm",
                    "acl_cleared": True,
                },
            )
            for i in range(4)
        ]
        contract = self.builder.build_contract(
            plan.query_id, "retrieval", docs, query_aspects=["retrieval"],
        )
        assert contract.status == EvidenceStatus.PASS
        assert contract.recommended_disposition == RecommendedDisposition.PROCEED
        # Lineage manifest records the lane
        assert "dense" in contract.lineage_manifest["retrieval_modes_used"]
        # Source IDs deduped
        assert len(contract.source_ids) == 4

    def test_weak_path_triggers_refinement_then_recovers(self) -> None:
        plan = _baseline_plan()
        # Initial weak contract
        contract = _make_contract(refine_attempt=0)

        # Run REWRITE -> refined plan available for second pass
        result = self.builder.execute_refinement_tactic(
            RefinementTactic.REWRITE, contract, plan, "what is the answer",
        )
        assert result["abstain"] is False
        refined_plan = result["refined_plan"]
        assert refined_plan.metadata["refinement_of"] == plan.plan_id

        # Verify the refined plan still has the same governance footprint
        assert refined_plan.tenant_id == plan.tenant_id
        assert refined_plan.allowed_principals == plan.allowed_principals
        assert refined_plan.support_target == plan.support_target

    def test_max_refine_attempts_eventually_aborts(self) -> None:
        plan = _baseline_plan()
        # Already at cap
        contract = _make_contract(refine_attempt=3)

        for tactic in [
            RefinementTactic.REWRITE,
            RefinementTactic.BROADEN,
            RefinementTactic.NARROW,
            RefinementTactic.DECOMPOSE,
            RefinementTactic.GRAPH_HOP,
        ]:
            result = self.builder.execute_refinement_tactic(
                tactic, contract, plan, "x and y",
            )
            assert result["abstain"] is True
            assert result["tactic"] == RefinementTactic.ABSTAIN

    def test_workflow_sized_task_recommends_reroute(self) -> None:
        # Build a contract whose coverage is below threshold/2
        # by giving weak docs with low rerank scores
        plan = _baseline_plan()
        docs = [
            StubDoc(
                doc_id="d1", score=0.71,  # just above min_citation_confidence
                content="x",
                metadata={"source_id": "s1", "rerank_score": 0.71},
            ),
        ]
        builder = EvidenceContractBuilder(
            min_citation_confidence=0.7,
            min_coverage_to_proceed=0.5,  # high threshold so single doc is workflow-sized
        )
        contract = builder.build_contract(
            plan.query_id, "very specific intricate compound query x", docs,
            query_aspects=["aspect1", "aspect2", "aspect3", "aspect4"],
        )
        # Status should be WEAK with very-low coverage
        assert contract.status == EvidenceStatus.WEAK
        # Disposition should be REROUTE for workflow-sized
        assert contract.recommended_disposition == RecommendedDisposition.REROUTE


# ===========================================================================
# 8. Evidence class taxonomy edge cases
# ===========================================================================


class TestEvidenceClassTaxonomy:

    def setup_method(self) -> None:
        self.builder = EvidenceContractBuilder()

    def test_contradicting_chunk_classified_contradicts(self) -> None:
        chunks = [
            VerifiedChunk(
                chunk_id="c1", content="x", source_id="s1",
                citation_anchor="a", support_score=0.95,
                is_must_use=True, contradiction_flag=True,
            ),
        ]
        classes = self.builder._build_evidence_classes(chunks, [])
        assert classes["c1"] == EvidenceClass.CONTRADICTS

    def test_low_support_chunk_classified_background(self) -> None:
        chunks = [
            VerifiedChunk(
                chunk_id="c1", content="x", source_id="s1",
                citation_anchor="a", support_score=0.3,
                is_must_use=False, contradiction_flag=False,
            ),
        ]
        classes = self.builder._build_evidence_classes(chunks, [])
        assert classes["c1"] == EvidenceClass.BACKGROUND

    def test_mid_support_chunk_classified_supporting(self) -> None:
        chunks = [
            VerifiedChunk(
                chunk_id="c1", content="x", source_id="s1",
                citation_anchor="a", support_score=0.65,
                is_must_use=False, contradiction_flag=False,
            ),
        ]
        classes = self.builder._build_evidence_classes(chunks, [])
        assert classes["c1"] == EvidenceClass.SUPPORTING

    def test_must_use_classified_must_use(self) -> None:
        chunks = [
            VerifiedChunk(
                chunk_id="c1", content="x", source_id="s1",
                citation_anchor="a", support_score=0.95,
                is_must_use=True, contradiction_flag=False,
            ),
        ]
        classes = self.builder._build_evidence_classes(chunks, [])
        assert classes["c1"] == EvidenceClass.MUST_USE


# ===========================================================================
# 9. Diagnostic-driven graph_hop targeting
# ===========================================================================


class FakeGraphStage:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def graph_hop(self, chunk_id: str, source_path: str, plan: Any) -> list[Any]:  # noqa: ARG002
        self.calls.append((chunk_id, source_path))
        return []


class TestGraphHopTargeting:

    def test_uses_diagnostics_when_available(self) -> None:
        from agentic_core.knowledge.retrieval.evidence_contract_builder import (
            EvidenceContract,
        )
        graph = FakeGraphStage()
        builder = EvidenceContractBuilder(graph_stage=graph)
        contract = EvidenceContract(
            query_id="q1",
            verified_chunks=[
                VerifiedChunk(
                    chunk_id=f"c{i}", content="x", source_id=f"s{i}",
                    citation_anchor="a", support_score=0.9, is_must_use=True,
                )
                for i in range(5)
            ],
            refinement_diagnostics=[
                RefinementDiagnostic(
                    issue_type="missing_graph_neighbor",
                    description="...",
                    suggested_tactic=RefinementTactic.GRAPH_HOP,
                    affected_chunks=["c2", "c3"],
                ),
            ],
        )
        builder.execute_refinement_tactic(
            RefinementTactic.GRAPH_HOP, contract, _baseline_plan(), "",
        )
        # Should have hopped only the diagnostic-targeted chunks
        called_chunk_ids = {c[0] for c in graph.calls}
        assert "c2" in called_chunk_ids
        assert "c3" in called_chunk_ids
        # Must NOT have hopped non-targeted chunks
        assert "c0" not in called_chunk_ids
        assert "c1" not in called_chunk_ids

    def test_hops_top_must_use_when_no_diagnostics(self) -> None:
        from agentic_core.knowledge.retrieval.evidence_contract_builder import (
            EvidenceContract,
        )
        graph = FakeGraphStage()
        builder = EvidenceContractBuilder(graph_stage=graph)
        contract = EvidenceContract(
            query_id="q1",
            verified_chunks=[
                VerifiedChunk(
                    chunk_id=f"c{i}", content="x", source_id=f"s{i}",
                    citation_anchor="a", support_score=0.9, is_must_use=True,
                )
                for i in range(5)
            ],
        )
        builder.execute_refinement_tactic(
            RefinementTactic.GRAPH_HOP, contract, _baseline_plan(), "",
        )
        # Top-3 chunks
        assert len(graph.calls) == 3
        called_ids = {c[0] for c in graph.calls}
        assert called_ids == {"c0", "c1", "c2"}
