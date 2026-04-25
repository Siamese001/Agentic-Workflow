"""Tests for C0.2 mode branching and C0.6 refinement tactic executors."""

from __future__ import annotations

import pytest

from agentic_core.knowledge.retrieval.evidence_contract_builder import (
    EvidenceContract,
    EvidenceContractBuilder,
    EvidenceStatus,
    RefinementDiagnostic,
    RefinementTactic,
    VerifiedChunk,
)
from agentic_core.knowledge.retrieval.retrieval_plan import (
    RetrievalMode,
    RetrievalPlan,
)


# ---------------------------------------------------------------------------
# C0.2 — Dense / Sparse / Hybrid mode branching
# ---------------------------------------------------------------------------


class StubVectorStore:
    def __init__(self, results: list[dict]) -> None:
        self._results = results

    def query(self, vec: list[float], k: int, filt: dict | None) -> list[dict]:  # noqa: ARG002
        return self._results


class StubSparseStore:
    def __init__(self, results: list[dict]) -> None:
        self._results = results

    def query(self, query: str, top_k: int = 10) -> list[dict]:  # noqa: ARG002
        return self._results


class TestRetrievalModeBranching:
    """C0.2: verify DENSE-only / SPARSE-only / HYBRID modes branch correctly."""

    def setup_method(self) -> None:
        from agentic_core.knowledge.retrieval.hybrid_recall_stage import (
            HybridRecallStage,
        )

        self.dense = StubVectorStore(
            [
                {"id": "d1", "score": 0.9, "content": "dense1", "metadata": {}},
                {"id": "d2", "score": 0.7, "content": "dense2", "metadata": {}},
            ]
        )
        self.sparse = StubSparseStore(
            [
                {"id": "s1", "score": 0.8, "content": "sparse1", "metadata": {}},
                {"id": "s2", "score": 0.6, "content": "sparse2", "metadata": {}},
            ]
        )
        self.stage = HybridRecallStage(
            vector_store=self.dense,
            sparse_store=self.sparse,
        )

    def test_dense_mode_skips_sparse(self) -> None:
        plan = RetrievalPlan(query_id="q1", retrieval_mode=RetrievalMode.DENSE)
        results = self.stage.recall(
            query_vector=[0.1, 0.2],
            query_terms=["foo"],
            plan=plan,
        )
        # All results from dense
        assert all(r.source == "dense" for r in results)
        assert {r.doc_id for r in results} == {"d1", "d2"}

    def test_sparse_mode_skips_dense(self) -> None:
        plan = RetrievalPlan(query_id="q1", retrieval_mode=RetrievalMode.SPARSE)
        results = self.stage.recall(
            query_vector=[0.1, 0.2],
            query_terms=["foo"],
            plan=plan,
        )
        assert all(r.source == "sparse" for r in results)
        assert {r.doc_id for r in results} == {"s1", "s2"}

    def test_hybrid_mode_runs_both(self) -> None:
        plan = RetrievalPlan(query_id="q1", retrieval_mode=RetrievalMode.HYBRID)
        results = self.stage.recall(
            query_vector=[0.1, 0.2],
            query_terms=["foo"],
            plan=plan,
        )
        # Should contain ids from both lanes
        ids = {r.doc_id for r in results}
        assert "d1" in ids or "d2" in ids
        assert "s1" in ids or "s2" in ids

    def test_dense_mode_propagates_replay_metadata(self) -> None:
        plan = RetrievalPlan(
            query_id="q1",
            retrieval_mode=RetrievalMode.DENSE,
            replay_key="rk_dense",
            policy_hash="ph_dense",
        )
        results = self.stage.recall(
            query_vector=[0.1, 0.2],
            query_terms=["foo"],
            plan=plan,
        )
        for r in results:
            assert r.metadata["replay_key"] == "rk_dense"
            assert r.metadata["policy_hash"] == "ph_dense"

    def test_sparse_mode_propagates_replay_metadata(self) -> None:
        plan = RetrievalPlan(
            query_id="q1",
            retrieval_mode=RetrievalMode.SPARSE,
            replay_key="rk_sparse",
            policy_hash="ph_sparse",
        )
        results = self.stage.recall(
            query_vector=[0.1, 0.2],
            query_terms=["foo"],
            plan=plan,
        )
        for r in results:
            assert r.metadata["replay_key"] == "rk_sparse"
            assert r.metadata["policy_hash"] == "ph_sparse"


# ---------------------------------------------------------------------------
# C0.6 — Refinement tactic executors
# ---------------------------------------------------------------------------


def _make_contract(
    refine_attempt: int = 0,
    diagnostics: list[RefinementDiagnostic] | None = None,
    verified_chunks: list[VerifiedChunk] | None = None,
) -> EvidenceContract:
    return EvidenceContract(
        query_id="q1",
        status=EvidenceStatus.WEAK,
        support_score=0.4,
        coverage_score=0.3,
        verified_chunks=verified_chunks or [],
        refinement_diagnostics=diagnostics or [],
        refine_attempt=refine_attempt,
        max_refine_attempts=3,
    )


class TestRefinementTacticExecutors:
    def setup_method(self) -> None:
        self.builder = EvidenceContractBuilder()
        self.plan = RetrievalPlan(
            query_id="q1",
            replay_key="rk1",
            policy_hash="ph1",
            tenant_id="acme",
            allowed_principals=["user:alice"],
            top_k=20,
            source_collections=["docs"],
        )

    def test_rewrite_strips_stopwords(self) -> None:
        contract = _make_contract()
        result = self.builder.execute_refinement_tactic(
            tactic=RefinementTactic.REWRITE,
            contract=contract,
            original_plan=self.plan,
            query="What is the meaning of the answer",
        )
        assert result["tactic"] == RefinementTactic.REWRITE
        assert result["abstain"] is False
        # Stopwords removed
        assert "the" not in result["new_query"].split()
        assert "what" not in result["new_query"].split()

    def test_rewrite_preserves_acl_and_replay(self) -> None:
        contract = _make_contract()
        result = self.builder.execute_refinement_tactic(
            RefinementTactic.REWRITE,
            contract,
            self.plan,
            "query",
        )
        refined = result["refined_plan"]
        assert refined.tenant_id == "acme"
        assert refined.allowed_principals == ["user:alice"]
        assert refined.replay_key == "rk1"
        assert refined.policy_hash == "ph1"
        assert refined.metadata["refinement_of"] == self.plan.plan_id

    def test_broaden_loosens_freshness_and_widens_top_k(self) -> None:
        contract = _make_contract()
        result = self.builder.execute_refinement_tactic(
            RefinementTactic.BROADEN,
            contract,
            self.plan,
            "query",
        )
        refined = result["refined_plan"]
        # top_k doubled (capped at 100)
        assert refined.top_k == min(self.plan.top_k * 2, 100)
        # source_collections widened to empty
        assert refined.source_collections == []
        # ACL preserved
        assert refined.allowed_principals == ["user:alice"]

    def test_narrow_uses_must_use_source_ids(self) -> None:
        chunks = [
            VerifiedChunk(
                chunk_id="c1",
                content="x",
                source_id="src_alpha",
                citation_anchor="a",
                support_score=0.9,
                is_must_use=True,
            ),
            VerifiedChunk(
                chunk_id="c2",
                content="y",
                source_id="src_beta",
                citation_anchor="a",
                support_score=0.85,
                is_must_use=True,
            ),
        ]
        contract = _make_contract(verified_chunks=chunks)
        result = self.builder.execute_refinement_tactic(
            RefinementTactic.NARROW,
            contract,
            self.plan,
            "query",
        )
        refined = result["refined_plan"]
        assert "src_alpha" in refined.source_collections
        assert "src_beta" in refined.source_collections
        # top_k halved (floor 5)
        assert refined.top_k == max(self.plan.top_k // 2, 5)

    def test_decompose_splits_on_and(self) -> None:
        contract = _make_contract()
        result = self.builder.execute_refinement_tactic(
            RefinementTactic.DECOMPOSE,
            contract,
            self.plan,
            "tell me about cats and dogs and birds",
        )
        assert result["tactic"] == RefinementTactic.DECOMPOSE
        assert len(result["decomposed_queries"]) == 3
        assert len(result["decomposed_plans"]) == 3

    def test_decompose_falls_back_to_broaden_when_no_split(self) -> None:
        contract = _make_contract()
        result = self.builder.execute_refinement_tactic(
            RefinementTactic.DECOMPOSE,
            contract,
            self.plan,
            "single query",
        )
        # Falls through to BROADEN since query can't decompose
        assert result["tactic"] == RefinementTactic.BROADEN

    def test_abstain_returns_no_plan(self) -> None:
        contract = _make_contract()
        result = self.builder.execute_refinement_tactic(
            RefinementTactic.ABSTAIN,
            contract,
            self.plan,
            "query",
        )
        assert result["abstain"] is True
        assert result["refined_plan"] is None

    def test_max_refine_attempts_forces_abstain(self) -> None:
        contract = _make_contract(refine_attempt=3)  # equal to max
        # Even REWRITE should be forced to ABSTAIN
        result = self.builder.execute_refinement_tactic(
            RefinementTactic.REWRITE,
            contract,
            self.plan,
            "q",
        )
        assert result["abstain"] is True
        assert result["tactic"] == RefinementTactic.ABSTAIN
        assert "max_refine_attempts" in result["rationale"]

    def test_unknown_tactic_returns_original_plan(self) -> None:
        contract = _make_contract()
        result = self.builder.execute_refinement_tactic(
            "nonexistent_tactic",
            contract,
            self.plan,
            "q",
        )
        assert result["abstain"] is False
        assert result["refined_plan"] is self.plan

    def test_graph_hop_dispatch_without_graph_stage(self) -> None:
        contract = _make_contract()
        result = self.builder.execute_refinement_tactic(
            RefinementTactic.GRAPH_HOP,
            contract,
            self.plan,
            "q",
        )
        assert result["tactic"] == RefinementTactic.GRAPH_HOP
        # No graph_stage wired → empty hop_results
        assert result["hop_results"] == []


class TestRefinementGuards:
    """C0.6 GUARDS — no source escape, replay preserved."""

    def setup_method(self) -> None:
        self.builder = EvidenceContractBuilder()
        self.plan = RetrievalPlan(
            query_id="q1",
            replay_key="rk_guard",
            policy_hash="ph_guard",
            tenant_id="tenant_a",
            allowed_principals=["user:bob"],
            top_k=10,
        )

    @pytest.mark.parametrize(
        "tactic",
        [
            RefinementTactic.REWRITE,
            RefinementTactic.BROADEN,
            RefinementTactic.NARROW,
            RefinementTactic.DECOMPOSE,
        ],
    )
    def test_acl_and_replay_preserved_across_all_tactics(self, tactic: str) -> None:
        contract = _make_contract()
        result = self.builder.execute_refinement_tactic(
            tactic,
            contract,
            self.plan,
            "thing and other",
        )
        refined = result.get("refined_plan")
        if refined is None:
            return
        # ACL never escapes
        assert refined.tenant_id == "tenant_a"
        assert refined.allowed_principals == ["user:bob"]
        # Replay preserved
        assert refined.replay_key == "rk_guard"
        assert refined.policy_hash == "ph_guard"
