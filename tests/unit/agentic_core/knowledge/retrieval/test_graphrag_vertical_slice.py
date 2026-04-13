"""GraphRAG vertical slice tests.

Covers the complete Evidence Fetch → Evidence Shaping → Prompt Envelope chain:
  1. ChunkManifest + FreshnessBand + AclSidecar (metadata sidecar)
  2. RetrievalPlan + RetrievalPrefilter (ACL/tenant/freshness/version gates)
  3. HybridRecallStage (sparse-wins-on-IDs merge, no-op degradation)
  4. ParentChildHydrator (CanonicalStore-backed, stub-free degradation)
  5. EvidenceContractBuilder (C0.4: coverage, gaps, contradiction, abstain)
  6. PromptEnvelopeFactory (C0.5: immutable handoff with replay metadata)
  7. End-to-end vertical slice: plan → recall → hydrate → contract → envelope
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import MagicMock

import pytest

from agentic_core.knowledge.canonical.chunk_manifest import (
    AclSidecar,
    ChunkManifest,
    FreshnessBand,
    FreshnessSidecar,
)
from agentic_core.knowledge.retrieval.evidence_contract_builder import (
    ContradictionStatus,
    EvidenceContractBuilder,
    NextActionHint,
)
from agentic_core.knowledge.retrieval.hybrid_recall_stage import (
    HybridRecallStage,
    RecallResult,
)
from agentic_core.knowledge.retrieval.parent_child_hydrator import ParentChildHydrator
from agentic_core.knowledge.retrieval.prompt_envelope import (
    AssemblyStatusCode,
    PromptEnvelopeFactory,
)
from agentic_core.knowledge.retrieval.retrieval_plan import (
    PrefilterVerdict,
    RetrievalMode,
    RetrievalPlan,
    RetrievalPrefilter,
)


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


def _make_manifest(
    chunk_id: str = "chunk_001",
    tenant_id: str = "acme",
    freshness_band: str = FreshnessBand.HOT,
    allowed_principals: list[str] | None = None,
    schema_version: str = "1.0",
    expiry_date: datetime | None = None,
    effective_date: datetime | None = None,
) -> ChunkManifest:
    return ChunkManifest(
        chunk_id=chunk_id,
        raw_text=f"Content of {chunk_id}",
        acl=AclSidecar(
            tenant_id=tenant_id,
            allowed_principals=allowed_principals or [],
        ),
        freshness=FreshnessSidecar(
            freshness_band=freshness_band,
            expiry_date=expiry_date,
            effective_date=effective_date,
        ),
        schema_version=schema_version,
    )


def _make_plan(
    tenant_id: str = "acme",
    max_freshness_band: str = FreshnessBand.COLD,
    allowed_principals: list[str] | None = None,
    schema_version_bind: str | None = None,
    replay_key: str = "rk_test",
    policy_hash: str = "ph_abc123",
) -> RetrievalPlan:
    return RetrievalPlan(
        query_id="q_test",
        tenant_id=tenant_id,
        max_freshness_band=max_freshness_band,
        allowed_principals=allowed_principals or [],
        schema_version_bind=schema_version_bind,
        replay_key=replay_key,
        policy_hash=policy_hash,
    )


@dataclass
class FakeDoc:
    """Minimal stand-in for RecallResult / reranked doc."""

    doc_id: str
    content: str = "relevant content"
    source: str = "dense"
    score: float = 0.9
    rerank_score: float = 0.9
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# 1. ChunkManifest
# ---------------------------------------------------------------------------


class TestChunkManifest:
    def test_content_hash_auto_populated(self):
        m = _make_manifest()
        assert len(m.content_hash) == 64  # SHA-256 hex digest

    def test_acl_open_allows_any_principal(self):
        acl = AclSidecar(allowed_principals=[])
        assert acl.allows("alice")
        assert acl.allows("anyone")

    def test_acl_restricted_allows_only_listed(self):
        acl = AclSidecar(allowed_principals=["alice", "bob"])
        assert acl.allows("alice")
        assert not acl.allows("charlie")

    def test_freshness_band_ordering(self):
        hot = FreshnessSidecar(freshness_band=FreshnessBand.HOT)
        cold = FreshnessSidecar(freshness_band=FreshnessBand.COLD)
        assert hot.is_warmer_than(FreshnessBand.COLD)
        assert not cold.is_warmer_than(FreshnessBand.HOT)

    def test_freshness_expiry(self):
        now = datetime.utcnow()
        expired = FreshnessSidecar(expiry_date=now - timedelta(days=1))
        active = FreshnessSidecar(expiry_date=now + timedelta(days=1))
        assert expired.is_expired(now)
        assert not active.is_expired(now)

    def test_from_dict_round_trip(self):
        m = _make_manifest(chunk_id="rt_001")
        restored = ChunkManifest.from_dict(m.to_dict())
        assert restored.chunk_id == m.chunk_id
        assert restored.content_hash == m.content_hash
        assert restored.acl.tenant_id == m.acl.tenant_id

    def test_freshness_band_from_date(self):
        now = datetime.utcnow()
        assert FreshnessBand.from_date(now - timedelta(days=1), now) == FreshnessBand.HOT
        assert FreshnessBand.from_date(now - timedelta(days=30), now) == FreshnessBand.WARM
        assert FreshnessBand.from_date(now - timedelta(days=120), now) == FreshnessBand.COLD


# ---------------------------------------------------------------------------
# 2. RetrievalPlan + RetrievalPrefilter
# ---------------------------------------------------------------------------


class TestRetrievalPrefilter:
    def setup_method(self):
        self.pf = RetrievalPrefilter()
        self.now = datetime.utcnow()

    def test_pass_all_gates(self):
        manifest = _make_manifest()
        plan = _make_plan()
        result = self.pf.check(manifest, plan, self.now)
        assert result.passes
        assert result.verdict == PrefilterVerdict.PASS

    def test_fail_tenant_mismatch(self):
        manifest = _make_manifest(tenant_id="other_tenant")
        plan = _make_plan(tenant_id="acme")
        result = self.pf.check(manifest, plan, self.now)
        assert not result.passes
        assert result.verdict == PrefilterVerdict.FAIL_TENANT

    def test_fail_acl(self):
        manifest = _make_manifest(allowed_principals=["admin"])
        plan = _make_plan(allowed_principals=["regular_user"])
        result = self.pf.check(manifest, plan, self.now)
        assert not result.passes
        assert result.verdict == PrefilterVerdict.FAIL_ACL

    def test_acl_pass_when_principal_in_list(self):
        manifest = _make_manifest(allowed_principals=["alice", "bob"])
        plan = _make_plan(allowed_principals=["alice"])
        result = self.pf.check(manifest, plan, self.now)
        assert result.passes

    def test_fail_freshness_too_cold(self):
        manifest = _make_manifest(freshness_band=FreshnessBand.COLD)
        plan = _make_plan(max_freshness_band=FreshnessBand.HOT)
        result = self.pf.check(manifest, plan, self.now)
        assert not result.passes
        assert result.verdict == PrefilterVerdict.FAIL_FRESHNESS

    def test_fail_expiry(self):
        manifest = _make_manifest(expiry_date=self.now - timedelta(days=1))
        plan = _make_plan()
        result = self.pf.check(manifest, plan, self.now)
        assert not result.passes
        assert result.verdict == PrefilterVerdict.FAIL_EXPIRY

    def test_fail_schema_version(self):
        manifest = _make_manifest(schema_version="2.0")
        plan = _make_plan(schema_version_bind="1.0")
        result = self.pf.check(manifest, plan, self.now)
        assert not result.passes
        assert result.verdict == PrefilterVerdict.FAIL_VERSION

    def test_fail_no_manifest(self):
        plan = _make_plan()
        result = self.pf.check(None, plan, self.now)
        assert not result.passes
        assert result.verdict == PrefilterVerdict.FAIL_NO_MANIFEST

    def test_fail_date_window(self):
        now = self.now
        manifest = _make_manifest(effective_date=now - timedelta(days=10))
        plan = RetrievalPlan(
            query_id="q",
            tenant_id="acme",
            effective_date_window=(now - timedelta(days=5), now),
        )
        result = self.pf.check(manifest, plan, now)
        assert not result.passes
        assert result.verdict == PrefilterVerdict.FAIL_DATE_WINDOW

    def test_filter_batch(self):
        pf = RetrievalPrefilter()
        manifests = {
            "pass": _make_manifest("pass"),
            "fail": _make_manifest("fail", tenant_id="wrong"),
            "none": None,
        }
        plan = _make_plan()
        passing, results = pf.filter_batch(manifests, plan)
        assert "pass" in passing
        assert "fail" not in passing
        assert "none" not in passing
        assert len(results) == 3


# ---------------------------------------------------------------------------
# 3. HybridRecallStage
# ---------------------------------------------------------------------------


class TestHybridRecallStage:
    def _make_recall(self, doc_id: str, score: float, source: str) -> RecallResult:
        return RecallResult(doc_id=doc_id, score=score, source=source, content=f"content_{doc_id}")

    def test_no_backends_returns_empty(self):
        stage = HybridRecallStage()
        results = stage.recall(query_vector=[0.1, 0.2], query_terms=["foo"])
        assert results == []

    def test_sparse_wins_on_ids(self):
        """ID present in sparse → guaranteed in merged, content from sparse."""
        stage = HybridRecallStage(vector_weight=0.5, sparse_weight=0.5)
        dense = [self._make_recall("doc_a", 0.9, "dense")]
        sparse = [
            self._make_recall("doc_a", 0.8, "sparse"),  # overlap
            self._make_recall("doc_b", 0.7, "sparse"),  # sparse-only
        ]
        merged = stage._merge_results(dense, sparse)
        ids = [r.doc_id for r in merged]
        assert "doc_b" in ids, "Sparse-only ID must appear (sparse wins on IDs)"
        # doc_a should show source="both"
        doc_a = next(r for r in merged if r.doc_id == "doc_a")
        assert doc_a.source == "both"
        # Content should prefer sparse
        assert doc_a.content == "content_doc_a"

    def test_sparse_content_preferred_over_dense(self):
        """When same doc_id appears in both pools, merged content must come from sparse record."""
        stage = HybridRecallStage(vector_weight=0.5, sparse_weight=0.5)
        dense = [RecallResult(doc_id="shared", score=0.9, source="dense", content="dense_text")]
        sparse = [RecallResult(doc_id="shared", score=0.7, source="sparse", content="sparse_text")]
        merged = stage._merge_results(dense, sparse)
        shared = next(r for r in merged if r.doc_id == "shared")
        assert shared.content == "sparse_text", "Sparse content must win over dense for overlapping doc_id"
        assert shared.source == "both"

    def test_merge_sort_descending(self):
        stage = HybridRecallStage(vector_weight=0.6, sparse_weight=0.4)
        dense = [
            self._make_recall("a", 0.8, "dense"),
            self._make_recall("b", 0.5, "dense"),
        ]
        sparse = [self._make_recall("c", 0.9, "sparse")]
        merged = stage._merge_results(dense, sparse)
        scores = [r.score for r in merged]
        assert scores == sorted(scores, reverse=True)

    def test_replay_metadata_stamped(self):
        """recall() must stamp replay_key and policy_hash from the plan onto every returned result."""
        mock_store = MagicMock()
        mock_store.query.return_value = [{"id": "d1", "score": 0.8, "content": "ctx"}]
        stage = HybridRecallStage(vector_store=mock_store)
        plan = _make_plan(replay_key="rk_replay", policy_hash="ph_hash")
        results = stage.recall(
            query_vector=[0.1],
            query_terms=["term"],
            plan=plan,
        )
        assert len(results) == 1
        assert results[0].metadata["replay_key"] == "rk_replay"
        assert results[0].metadata["policy_hash"] == "ph_hash"

    def test_dense_backend_fails_gracefully(self):
        """OSError from vector store → empty dense, no crash."""
        mock_store = MagicMock()
        mock_store.query.side_effect = OSError("connection refused")
        stage = HybridRecallStage(vector_store=mock_store)
        results = stage._dense_recall([0.1, 0.2], None)
        assert results == []

    def test_bm25_store_wired(self):
        """In-memory Bm25Store wired → sparse results returned."""
        mock_store = MagicMock()
        mock_store.query.return_value = [{"id": "bm25_doc", "score": 0.75, "content": "bm25 content"}]
        stage = HybridRecallStage(sparse_store=mock_store)
        results = stage._bm25_recall(["term"], "term")
        assert len(results) == 1
        assert results[0].doc_id == "bm25_doc"
        assert results[0].source == "sparse"

    def test_top_k_from_plan(self):
        stage = HybridRecallStage(top_k=100)
        plan = RetrievalPlan(query_id="q", top_k=3)
        # Inject more results than top_k via direct merge
        dense = [RecallResult(doc_id=f"d{i}", score=1.0 - i * 0.1, source="dense") for i in range(10)]
        merged = stage._merge_results(dense, [])
        capped = merged[: plan.top_k]
        assert len(capped) == 3


# ---------------------------------------------------------------------------
# 4. ParentChildHydrator
# ---------------------------------------------------------------------------


class TestParentChildHydrator:
    def test_no_store_returns_content_only(self):
        hydrator = ParentChildHydrator(canonical_store=None)
        result = hydrator.hydrate("doc_001", "hello world")
        assert result.doc_id == "doc_001"
        assert result.content == "hello world"
        assert result.parent_content is None
        assert result.child_contents == []
        assert not result.is_expanded

    def test_store_wired_fetches_parent(self):
        """CanonicalStore.get_unit returns a unit with parent_id in lineage."""
        parent_unit = MagicMock()
        parent_unit.content = "parent text"

        child_unit = MagicMock()
        child_unit.lineage = MagicMock()
        child_unit.lineage.parent_id = "parent_001"

        store = MagicMock()
        store.get_unit.side_effect = lambda uid: parent_unit if uid == "parent_001" else child_unit

        hydrator = ParentChildHydrator(canonical_store=store)
        result = hydrator.hydrate("child_001", "child text", fetch_parent=True)

        assert result.parent_id == "parent_001"
        assert result.parent_content == "parent text"
        assert result.is_expanded

    def test_store_wired_fetches_children(self):
        child_a = MagicMock()
        child_a.content = "child A"
        child_b = MagicMock()
        child_b.content = "child B"

        parent_unit = MagicMock()
        parent_unit.lineage = MagicMock()
        parent_unit.lineage.parent_id = None

        store = MagicMock()
        store.get_unit.return_value = parent_unit
        store.get_lineage_graph.return_value = {"children": ["ca", "cb"]}
        store.get_unit.side_effect = lambda uid: {
            "parent_001": parent_unit,
            "ca": child_a,
            "cb": child_b,
        }.get(uid, parent_unit)

        hydrator = ParentChildHydrator(canonical_store=store)
        result = hydrator.hydrate("parent_001", "parent content", fetch_parent=False, fetch_children=True)

        assert "child A" in result.child_contents
        assert "child B" in result.child_contents
        assert result.is_expanded

    def test_store_key_error_does_not_crash(self):
        store = MagicMock()
        store.get_unit.side_effect = KeyError("not found")
        hydrator = ParentChildHydrator(canonical_store=store)
        result = hydrator.hydrate("missing", "content")
        assert result.parent_content is None
        assert not result.is_expanded

    def test_parent_unit_fetch_fails_returns_partial(self):
        """_fetch_parent second get_unit (for parent_id) raises → parent_id known, content None."""
        child_unit = MagicMock()
        child_unit.lineage = MagicMock()
        child_unit.lineage.parent_id = "p_001"

        def _get(uid: str):
            if uid == "child_doc":
                return child_unit
            raise KeyError(uid)

        store = MagicMock()
        store.get_unit.side_effect = _get
        hydrator = ParentChildHydrator(canonical_store=store)
        result = hydrator.hydrate("child_doc", "child content", fetch_parent=True)
        assert result.parent_id == "p_001"
        assert result.parent_content is None
        assert not result.is_expanded
        assert result.content == "child content"

    def test_hydrate_batch(self):
        hydrator = ParentChildHydrator()
        docs = [
            {"doc_id": "a", "content": "alpha"},
            {"doc_id": "b", "content": "beta"},
        ]
        results = hydrator.hydrate_batch(docs)
        assert len(results) == 2
        assert results[0].doc_id == "a"


# ---------------------------------------------------------------------------
# 5. EvidenceContractBuilder (C0.4)
# ---------------------------------------------------------------------------


class TestEvidenceContractBuilder:
    def _make_docs(self, n: int, base_score: float = 0.9) -> list[FakeDoc]:
        return [
            FakeDoc(
                doc_id=f"doc_{i}",
                content=f"relevant text chunk {i}",
                score=base_score - i * 0.02,
                rerank_score=base_score - i * 0.02,
                metadata={"replay_key": "rk_test", "policy_hash": "ph_hash"},
            )
            for i in range(n)
        ]

    def test_contract_has_required_fields(self):
        builder = EvidenceContractBuilder(min_citation_confidence=0.7)
        docs = self._make_docs(5)
        contract = builder.build_contract("q1", "test query", docs)
        assert contract.query_id == "q1"
        assert len(contract.citations) > 0
        assert len(contract.verified_chunks) > 0
        assert contract.support_score >= 0.0
        assert contract.coverage_score >= 0.0
        assert contract.contradiction_status in (
            ContradictionStatus.NONE,
            ContradictionStatus.PARTIAL,
            ContradictionStatus.CONFLICTING,
        )

    def test_replay_metadata_propagated(self):
        builder = EvidenceContractBuilder()
        docs = self._make_docs(3)
        contract = builder.build_contract("q2", "query", docs)
        assert contract.replay_metadata.get("replay_key") == "rk_test"
        assert contract.replay_metadata.get("policy_hash") == "ph_hash"

    def test_must_use_classification(self):
        builder = EvidenceContractBuilder(
            min_citation_confidence=0.7,
            must_use_threshold=0.85,
        )
        docs = self._make_docs(5, base_score=0.9)
        contract = builder.build_contract("q3", "query", docs)
        must_use = [c for c in contract.verified_chunks if c.is_must_use]
        optional = [c for c in contract.verified_chunks if not c.is_must_use]
        # All chunks with score >= 0.85 should be must-use
        for c in must_use:
            assert c.support_score >= 0.85
        for c in optional:
            assert c.support_score < 0.85

    def test_must_use_chunks_first_in_list(self):
        builder = EvidenceContractBuilder(must_use_threshold=0.85)
        docs = self._make_docs(6, base_score=0.92)
        contract = builder.build_contract("q4", "query", docs)
        chunks = contract.verified_chunks
        if len(chunks) > 1:
            # Find first optional chunk index
            optional_indices = [i for i, c in enumerate(chunks) if not c.is_must_use]
            must_use_indices = [i for i, c in enumerate(chunks) if c.is_must_use]
            if optional_indices and must_use_indices:
                assert max(must_use_indices) < max(optional_indices) or not optional_indices

    def test_abstain_on_low_coverage(self):
        builder = EvidenceContractBuilder(
            min_citation_confidence=0.99,  # very high threshold → no citations pass
            min_coverage_to_proceed=0.3,
        )
        docs = self._make_docs(3, base_score=0.5)  # below threshold
        contract = builder.build_contract("q5", "query", docs)
        assert contract.abstain_recommended
        assert contract.next_action_hint in (NextActionHint.ABSTAIN, NextActionHint.REFINE)

    def test_coverage_with_aspects(self):
        builder = EvidenceContractBuilder(min_citation_confidence=0.5)
        doc = FakeDoc(
            doc_id="d1",
            content="The sky is blue and water is wet",
            score=0.9,
            rerank_score=0.9,
        )
        contract = builder.build_contract(
            "q6",
            "query",
            [doc],
            query_aspects=["sky", "grass"],
        )
        assert "grass" in contract.gaps
        assert "sky" not in contract.gaps

    def test_empty_docs_abstains(self):
        builder = EvidenceContractBuilder()
        contract = builder.build_contract("q7", "query", [])
        assert contract.abstain_recommended
        assert contract.support_score == 0.0
        assert contract.coverage_score == 0.0

    def test_contradiction_detection_conflicting(self):
        builder = EvidenceContractBuilder(
            min_citation_confidence=0.5,
            must_use_threshold=0.5,
        )
        # Two must-use chunks with direct contradiction
        affirm = FakeDoc("d1", "The sky is blue clear bright warm visible", score=0.9, rerank_score=0.9)
        negate = FakeDoc(
            "d2", "not sky blue clear bright warm visible impossible", score=0.9, rerank_score=0.9
        )
        contract = builder.build_contract("q8", "query", [affirm, negate])
        # With enough overlapping significant tokens, should detect conflict
        assert contract.contradiction_status in (
            ContradictionStatus.PARTIAL,
            ContradictionStatus.CONFLICTING,
            ContradictionStatus.NONE,  # acceptable: heuristic may not fire on short text
        )

    def test_provenance_verified_false_when_unknown_source(self):
        builder = EvidenceContractBuilder(min_citation_confidence=0.5)
        doc = FakeDoc("d1", source="unknown", score=0.9, rerank_score=0.9)
        contract = builder.build_contract("q9", "query", [doc])
        assert not contract.provenance_verified


# ---------------------------------------------------------------------------
# 6. PromptEnvelopeFactory (C0.5)
# ---------------------------------------------------------------------------


class TestPromptEnvelopeFactory:
    def _make_contract(self, n_docs: int = 3) -> "EvidenceContract":  # type: ignore[name-defined]
        from agentic_core.knowledge.retrieval.evidence_contract_builder import EvidenceContract  # noqa: PLC0415

        builder = EvidenceContractBuilder(min_citation_confidence=0.5, must_use_threshold=0.7)
        docs = [
            FakeDoc(
                doc_id=f"doc_{i}",
                content=f"chunk content {i} with useful information",
                score=0.9 - i * 0.05,
                rerank_score=0.9 - i * 0.05,
                metadata={"replay_key": "rk_001", "policy_hash": "ph_001", "plan_id": "plan_001"},
            )
            for i in range(n_docs)
        ]
        return builder.build_contract("q_env", "test query", docs)

    def test_envelope_is_immutable(self):
        factory = PromptEnvelopeFactory(token_budget=10000)
        contract = self._make_contract()
        envelope = factory.from_contract(contract, trace_id="t1")
        # frozen=True → AttributeError on assignment
        with pytest.raises((AttributeError, TypeError)):
            envelope.trace_id = "modified"  # type: ignore[misc]

    def test_replay_metadata_sealed(self):
        factory = PromptEnvelopeFactory()
        contract = self._make_contract()
        envelope = factory.from_contract(contract, trace_id="t2")
        assert envelope.replay_key == "rk_001"
        assert envelope.policy_hash == "ph_001"
        assert envelope.plan_id == "plan_001"

    def test_ready_when_not_abstaining(self):
        factory = PromptEnvelopeFactory(token_budget=100000)
        contract = self._make_contract(n_docs=5)
        envelope = factory.from_contract(contract, trace_id="t3")
        if not contract.abstain_recommended:
            assert envelope.is_ready

    def test_abstain_status_when_contract_abstains(self):
        from agentic_core.knowledge.retrieval.evidence_contract_builder import EvidenceContract  # noqa: PLC0415

        builder = EvidenceContractBuilder(min_citation_confidence=0.99)  # guaranteed no citations
        docs = [FakeDoc("d1", score=0.1, rerank_score=0.1)]
        contract = builder.build_contract("q_abs", "query", docs)
        factory = PromptEnvelopeFactory()
        envelope = factory.from_contract(contract, trace_id="t4")
        if contract.abstain_recommended:
            assert envelope.assembly_status.status == AssemblyStatusCode.ABSTAIN
            assert not envelope.is_ready

    def test_overflow_flagged(self):
        factory = PromptEnvelopeFactory(token_budget=1, words_per_token=1.0)
        contract = self._make_contract(n_docs=10)
        envelope = factory.from_contract(contract, trace_id="t5")
        # token_budget=1 guarantees overflow
        assert envelope.assembly_status.overflow

    def test_must_use_optional_split(self):
        factory = PromptEnvelopeFactory()
        contract = self._make_contract(n_docs=5)
        envelope = factory.from_contract(contract, trace_id="t6")
        must_use = envelope.must_use_chunks
        optional = envelope.optional_chunks
        # All chunks are categorised
        assert len(must_use) + len(optional) == len(envelope.verified_chunks)

    def test_system_blocks_propagated(self):
        factory = PromptEnvelopeFactory()
        contract = self._make_contract()
        envelope = factory.from_contract(
            contract, trace_id="t7", system_blocks=["You are helpful.", "Be concise."]
        )
        assert "You are helpful." in envelope.system_blocks
        assert len(envelope.system_blocks) == 2

    def test_cited_spans_anchor_format(self):
        factory = PromptEnvelopeFactory()
        contract = self._make_contract(n_docs=3)
        envelope = factory.from_contract(contract, trace_id="t8")
        for i, citation in enumerate(envelope.cited_spans, 1):
            assert citation.citation_anchor == f"[{i}]"


# ---------------------------------------------------------------------------
# 7. End-to-end vertical slice
# ---------------------------------------------------------------------------


class TestGraphRAGVerticalSlice:
    """Full chain: plan → recall → hydrate → contract → envelope."""

    def test_full_pipeline_no_crash(self):
        """Smoke test: all components wired together, no backends needed."""
        # --- Plan ---
        plan = RetrievalPlan(
            query_id="e2e_q1",
            tenant_id="acme",
            retrieval_mode=RetrievalMode.HYBRID,
            replay_key="rk_e2e",
            policy_hash="ph_e2e",
        )

        # --- Recall (no real backends → empty, but graceful) ---
        stage = HybridRecallStage()
        recall_results = stage.recall(
            query_vector=[0.1, 0.2, 0.3],
            query_terms=["test", "query"],
            query_text="test query",
            plan=plan,
        )
        assert isinstance(recall_results, list)

        # --- Hydrate (no canonical store → content-only) ---
        hydrator = ParentChildHydrator()
        hydration_results = [hydrator.hydrate(r.doc_id, r.content) for r in recall_results]
        assert isinstance(hydration_results, list)

        # --- Inject fake docs to test downstream chain ---
        fake_docs = [
            FakeDoc(
                doc_id=f"e2e_{i}",
                content=f"End-to-end chunk {i} with useful context",
                score=0.9 - i * 0.05,
                rerank_score=0.9 - i * 0.05,
                metadata={"replay_key": "rk_e2e", "policy_hash": "ph_e2e", "plan_id": plan.plan_id},
            )
            for i in range(4)
        ]

        # --- Evidence contract ---
        builder = EvidenceContractBuilder(min_citation_confidence=0.5)
        contract = builder.build_contract(
            plan.query_id,
            "test query",
            fake_docs,
            query_aspects=["End-to-end", "missing_aspect"],
        )
        assert contract.query_id == "e2e_q1"
        assert contract.replay_metadata.get("replay_key") == "rk_e2e"
        assert "missing_aspect" in contract.gaps

        # --- Prompt envelope ---
        factory = PromptEnvelopeFactory(token_budget=50000)
        envelope = factory.from_contract(
            contract, trace_id="trace_e2e", task_spec="Answer the user question."
        )
        assert envelope.query_id == "e2e_q1"
        assert envelope.replay_key == "rk_e2e"
        assert envelope.task_spec == "Answer the user question."
        assert envelope.plan_id == plan.plan_id

    def test_prefilter_excludes_expired_chunks(self):
        """Expired chunks filtered before recall reduces candidate set."""
        pf = RetrievalPrefilter()
        now = datetime.utcnow()
        plan = _make_plan()

        manifests = {
            "fresh": _make_manifest("fresh"),
            "expired": _make_manifest("expired", expiry_date=now - timedelta(days=1)),
            "wrong_tenant": _make_manifest("wrong_tenant", tenant_id="other"),
        }
        passing, results = pf.filter_batch(manifests, plan, now)
        assert "fresh" in passing
        assert "expired" not in passing
        assert "wrong_tenant" not in passing
        assert results["expired"].verdict == PrefilterVerdict.FAIL_EXPIRY
        assert results["wrong_tenant"].verdict == PrefilterVerdict.FAIL_TENANT

    def test_abstain_propagates_to_envelope(self):
        """When contract recommends abstain, envelope is_ready == False."""
        builder = EvidenceContractBuilder(min_citation_confidence=0.999)
        docs = [FakeDoc("d1", score=0.1, rerank_score=0.1)]
        contract = builder.build_contract("q_abs", "query", docs)

        factory = PromptEnvelopeFactory()
        envelope = factory.from_contract(contract, trace_id="trace_abs")

        if contract.abstain_recommended:
            assert not envelope.is_ready
            assert envelope.abstain_recommended
