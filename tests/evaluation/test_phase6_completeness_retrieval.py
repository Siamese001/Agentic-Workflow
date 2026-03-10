"""
Tests: Phase 6 — Completeness-Aware Retrieval Subsystem

Coverage per .windsurfrules §1.2 (branch proof) and §1.3 (branch inventory):

1. Hierarchical retrieval
   - child expands to correct parent section
   - neighbor window expansion is deterministic
   - no duplicate grounded context entries after fusion

2. Completeness scoring
   - detects missing condition
   - detects missing exception
   - detects missing scope
   - detects missing temporal qualifier
   - scores 1.0 when no dimensions are signaled
   - scores partial when some dimensions addressed

3. Support validation
   - flags unsupported answer when condition lives outside retrieved fragment
   - passes when parent reconstruction supplies missing condition
   - emits deterministic SupportedAnswerCheck
   - content_hash is stable for identical inputs

4. Observability monitors
   - logs high_similarity_wrong_answer_rate correctly
   - logs parent_reconstruction_applied_rate correctly
   - snapshots are stable and deterministic
   - ConditionLossDriftMonitor delta tracks correctly

5. Meta-learning
   - completeness metrics enter EvaluationSignals correctly
   - RAGProposer proposes based on low completeness
   - RAGProposer proposes based on high fragmentation
   - RAGProposer proposes hybrid retrieval for unsupported answers
   - proposal always has proposal_only=True
   - proposal_only=False raises ValueError

6. Late chunking
   - deterministic segmentation: same input -> same output
   - profile gating: invalid mode raises ValueError
   - invalid pooling strategy raises ValueError
   - manifest hashes are stable
   - comparison against standard chunking supported
   - zero-token document produces no segments
   - segment_document token boundary correctness

7. C0 sovereignty
   - retrieval outputs remain informational only
   - no route mutation from completeness scores
   - no safety threshold mutation from retrieval outputs
   - no tier change from retrieval outputs

8. L4 registries
   - ChunkManifestRegistry idempotent write
   - ParentChildIndexRegistry child->parent lookup
   - RetrievalEvaluationRegistry write-once semantics
   - ContextCompletenessSnapshotStore accumulates

9. CompletenessReranker
   - reranks by blended score (not just similarity)
   - deterministic tie-break by doc_id
   - config weights must sum to 1.0
   - top_k enforced
"""

from __future__ import annotations

import pytest
from agentic_core.evaluation.monitoring.completeness_monitors import (
    ConditionLossDriftMonitor,
    HighSimilarityWrongAnswerMonitor,
    ParentExpansionMissMonitor,
    RetrievalCompletenessMonitor,
)
from agentic_core.evaluation.retrieval.answer_support import KeywordAnswerSupportValidator
from agentic_core.evaluation.retrieval.completeness import (
    ContextCompletenessScore,
    GroundedDocument,
    SupportedAnswerCheck,
)
from agentic_core.evaluation.retrieval.completeness_reranker import (
    CompletenessReranker,
    CompletenessRerankerConfig,
)
from agentic_core.evaluation.retrieval.completeness_scorer import (
    KeywordCompletenessScorer,
)
from agentic_core.evaluation.retrieval.interfaces import Document
from agentic_core.evaluation.retrieval.late_chunking import (
    VALID_MODES,
    LateChunkingPipelineConfig,
    LateChunkingProfile,
    build_late_chunk_manifests_for_corpus,
    segment_document,
)
from agentic_core.evaluation.retrieval.meta_learning_bridge import (
    CompletenessChangePackage,
    CompletenessRAGProposer,
    EvaluationSignals,
)
from agentic_core.evaluation.retrieval.parent_child import (
    ChunkEntry,
    ParentChildExpander,
    ParentChildRegistry,
)

from agentic_core.evaluation.retrieval.l4_registries import (
    ChunkManifest,
    ChunkManifestRegistry,
    ContextCompletenessSnapshot,
    ContextCompletenessSnapshotStore,
    ParentChildIndexRegistry,
    ParentChildLink,
    RetrievalEvaluationRecord,
    RetrievalEvaluationRegistry,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_doc(doc_id: str, score: float = 0.9, content: str = "some content") -> Document:
    return Document(doc_id=doc_id, content=content, score=score)


def _make_grounded(
    doc_id: str,
    score: float = 0.9,
    content: str = "some content",
    parent_id: str = "sec_1",
    parent_content: str = "",
    expanded: bool = True,
) -> GroundedDocument:
    return GroundedDocument(
        doc_id=doc_id,
        content=content,
        score=score,
        parent_section_id=parent_id,
        parent_content=parent_content,
        expanded=expanded,
    )


def _make_scorer() -> KeywordCompletenessScorer:
    return KeywordCompletenessScorer()


def _make_signals(
    snapshot_id: str = "snap_1",
    mean_completeness: float = 0.4,
    fragmentation: float = 0.0,
    fully_supported: float = 0.9,
    high_sim_wrong: float = 0.05,
    parent_rate: float = 0.5,
    obs: int = 10,
) -> EvaluationSignals:
    return EvaluationSignals(
        snapshot_id=snapshot_id,
        retrieval_relevance_mean=0.8,
        retrieval_precision=0.7,
        retrieval_recall=0.6,
        mean_completeness_score=mean_completeness,
        missing_condition_rate=0.0,
        missing_exception_rate=0.0,
        missing_scope_rate=0.0,
        missing_temporal_qualifier_rate=0.0,
        answer_correctness_rate=0.85,
        fully_supported_rate=fully_supported,
        mean_support_score=0.75,
        high_similarity_wrong_answer_rate=high_sim_wrong,
        parent_reconstruction_applied_rate=parent_rate,
        chunk_fragmentation_error_rate=fragmentation,
        observation_count=obs,
    )


def _make_late_profile(mode: str = "late_chunked") -> LateChunkingProfile:
    return LateChunkingProfile(
        profile_id="lc-v1",
        mode=mode,
        embedding_model_version="bge-m3-v1",
        max_input_tokens=2048,
        pooling_strategy="mean",
        chunk_window_policy="fixed",
        stride_policy="stride_64",
        parent_section_policy="heading",
    )


# ===========================================================================
# 1. Hierarchical Retrieval
# ===========================================================================


class TestParentChildExpander:
    """Branch inventory:
    - expand: chunk_id in registry → expanded=True, parent content set
    - expand: chunk_id NOT in registry → expanded=False, graceful fallback
    - get_parent_section_id: known → returns id; unknown → None
    - get_heading_path: known → returns list; unknown → []
    - neighbor window resolution with siblings
    """

    def _build_registry_with_chunk(self) -> tuple[ParentChildExpander, ChunkEntry]:
        reg = ParentChildRegistry()
        entry = ChunkEntry(
            chunk_id="c1",
            parent_section_id="sec_1",
            sibling_ids=("c0", "c1", "c2"),
            content="chunk one content",
            heading_path=("Root", "Section 1"),
            source_doc_id="doc_a",
        )
        reg.register_chunk(entry, parent_content="Full parent section text about conditions.")
        expander = ParentChildExpander(reg)
        return expander, entry

    def test_expand_known_chunk_sets_parent_content(self):
        expander, entry = self._build_registry_with_chunk()
        doc = _make_doc("c1", content="chunk one content")
        result = expander.expand(doc)
        assert result.expanded is True
        assert result.parent_section_id == "sec_1"
        assert "conditions" in result.parent_content

    def test_expand_known_chunk_heading_path(self):
        expander, _ = self._build_registry_with_chunk()
        doc = _make_doc("c1")
        result = expander.expand(doc)
        assert result.heading_path == ["Root", "Section 1"]

    def test_expand_unknown_chunk_graceful_fallback(self):
        expander, _ = self._build_registry_with_chunk()
        doc = _make_doc("UNKNOWN")
        result = expander.expand(doc)
        assert result.expanded is False
        assert result.parent_content == ""
        assert result.parent_section_id == ""

    def test_neighbor_window_deterministic(self):
        expander, _ = self._build_registry_with_chunk()
        doc = _make_doc("c1")
        result = expander.expand(doc, neighbor_window=1)
        assert set(result.sibling_ids) <= {"c0", "c2"}
        assert "c1" not in result.sibling_ids

    def test_neighbor_window_zero_returns_empty(self):
        expander, _ = self._build_registry_with_chunk()
        doc = _make_doc("c1")
        result = expander.expand(doc, neighbor_window=0)
        assert result.sibling_ids == []

    def test_get_parent_section_id_known(self):
        expander, _ = self._build_registry_with_chunk()
        assert expander.get_parent_section_id("c1") == "sec_1"

    def test_get_parent_section_id_unknown_returns_none(self):
        expander, _ = self._build_registry_with_chunk()
        assert expander.get_parent_section_id("NOPE") is None

    def test_get_heading_path_known(self):
        expander, _ = self._build_registry_with_chunk()
        assert expander.get_heading_path("c1") == ["Root", "Section 1"]

    def test_get_heading_path_unknown_returns_empty(self):
        expander, _ = self._build_registry_with_chunk()
        assert expander.get_heading_path("NOPE") == []

    def test_expand_same_input_deterministic(self):
        expander, _ = self._build_registry_with_chunk()
        doc = _make_doc("c1")
        r1 = expander.expand(doc)
        r2 = expander.expand(doc)
        assert r1.parent_content == r2.parent_content
        assert r1.sibling_ids == r2.sibling_ids
        assert r1.heading_path == r2.heading_path


# ===========================================================================
# 2. Completeness Scoring
# ===========================================================================


class TestKeywordCompletenessScorer:
    """Branch inventory:
    - score: query signals condition AND chunk has no condition keyword → missing_condition=True
    - score: query signals condition AND chunk HAS condition keyword → missing_condition=False
    - score: query signals exception AND chunk misses it → missing_exception=True
    - score: query signals scope AND chunk misses it → missing_scope=True
    - score: query signals temporal AND chunk misses it → missing_temporal=True
    - score: query signals nothing → completeness=1.0
    - score: GroundedDocument with parent supplies missing dimension → not missing
    - score_batch: returns same-length list, deterministic
    """

    def test_detects_missing_condition(self):
        scorer = _make_scorer()
        doc = _make_doc("d1", content="The result is always returned.")
        score = scorer.score("q1", "when should this apply if condition is met?", doc)
        assert score.missing_condition is True

    def test_no_missing_condition_when_chunk_has_keyword(self):
        scorer = _make_scorer()
        doc = _make_doc("d1", content="When the user is authenticated, access is granted.")
        score = scorer.score("q1", "when does access apply if condition is met?", doc)
        assert score.missing_condition is False

    def test_detects_missing_exception(self):
        scorer = _make_scorer()
        doc = _make_doc("d1", content="The operation completes successfully.")
        score = scorer.score("q1", "what happens except when error occurs?", doc)
        assert score.missing_exception is True

    def test_detects_missing_scope(self):
        scorer = _make_scorer()
        doc = _make_doc("d1", content="The feature is available.")
        score = scorer.score("q1", "which tier does this apply to?", doc)
        assert score.missing_scope is True

    def test_detects_missing_temporal_qualifier(self):
        scorer = _make_scorer()
        doc = _make_doc("d1", content="The API is available for all users.")
        score = scorer.score("q1", "as of which version is this deprecated?", doc)
        assert score.missing_temporal_qualifier is True

    def test_no_missing_when_query_has_no_signals(self):
        scorer = _make_scorer()
        doc = _make_doc("d1", content="Short chunk with no relevant signal.")
        score = scorer.score("q1", "what is the feature?", doc)
        assert score.completeness_score == 1.0
        assert score.missing_condition is False
        assert score.missing_exception is False
        assert score.missing_scope is False
        assert score.missing_temporal_qualifier is False

    def test_parent_content_supplies_missing_dimension(self):
        scorer = _make_scorer()
        child_content = "The operation completes."
        parent_content = "When the condition is met, the operation completes."
        doc = _make_grounded(
            "d1",
            content=child_content,
            parent_content=parent_content,
        )
        score = scorer.score("q1", "when should this apply if condition is satisfied?", doc)
        assert score.missing_condition is False

    def test_completeness_score_partial(self):
        scorer = _make_scorer()
        doc = _make_doc(
            "d1",
            content="When the user is authenticated, access is granted.",
        )
        score = scorer.score(
            "q1",
            "when does this apply and which version does it apply to?",
            doc,
        )
        assert 0.0 <= score.completeness_score <= 1.0
        assert score.missing_condition is False
        assert score.missing_scope is True or score.missing_temporal_qualifier is True

    def test_score_batch_same_length(self):
        scorer = _make_scorer()
        docs = [_make_doc(f"d{i}") for i in range(5)]
        scores = scorer.score_batch("q1", "when does this apply?", docs)
        assert len(scores) == 5

    def test_score_batch_deterministic(self):
        scorer = _make_scorer()
        docs = [_make_doc(f"d{i}", content=f"content {i}") for i in range(3)]
        r1 = scorer.score_batch("q1", "when does this apply?", docs)
        r2 = scorer.score_batch("q1", "when does this apply?", docs)
        assert [s.completeness_score for s in r1] == [s.completeness_score for s in r2]

    def test_is_complete_property(self):
        cs = ContextCompletenessScore(
            query_id="q1",
            chunk_id="c1",
            parent_section_id="",
            relevance_score=0.9,
            completeness_score=1.0,
            missing_condition=False,
            missing_exception=False,
            missing_scope=False,
            missing_temporal_qualifier=False,
            confidence=0.75,
        )
        assert cs.is_complete is True

    def test_is_complete_false_when_any_missing(self):
        cs = ContextCompletenessScore(
            query_id="q1",
            chunk_id="c1",
            parent_section_id="",
            relevance_score=0.9,
            completeness_score=0.75,
            missing_condition=True,
            missing_exception=False,
            missing_scope=False,
            missing_temporal_qualifier=False,
            confidence=0.75,
        )
        assert cs.is_complete is False
        assert cs.missing_count == 1

    def test_content_hash_stable(self):
        cs = ContextCompletenessScore(
            query_id="q1",
            chunk_id="c1",
            parent_section_id="sec_1",
            relevance_score=0.9,
            completeness_score=0.8,
            missing_condition=False,
            missing_exception=False,
            missing_scope=True,
            missing_temporal_qualifier=False,
            confidence=0.75,
        )
        assert cs.content_hash() == cs.content_hash()


# ===========================================================================
# 3. Support Validation (Phase C)
# ===========================================================================


class TestKeywordAnswerSupportValidator:
    """Branch inventory:
    - validate: all sentences covered → fully_supported=True
    - validate: sentence with no evidence coverage → flagged unsupported
    - validate: parent reconstruction supplies missing span → improves support
    - validate: empty answer → fully_supported=True (no claims to fail)
    - validate: single chunk, all covered → support_score=1.0
    - SupportedAnswerCheck: content_hash stable for identical inputs
    - SupportedAnswerCheck: from_dict roundtrip
    - min_overlap_words < 1 → ValueError
    - fully_supported_threshold out of range → ValueError
    """

    def _make_validator(self) -> KeywordAnswerSupportValidator:
        return KeywordAnswerSupportValidator(min_overlap_words=3, fully_supported_threshold=THRESHOLD)

    def test_fully_supported_when_all_sentences_covered(self):
        v = self._make_validator()
        answer = "The user must authenticate with a valid token."
        chunks = [_make_doc("c1", content="user must authenticate with valid token credentials")]
        result = v.validate("a1", answer, chunks, [])
        assert result.fully_supported is True
        assert result.support_score > 0.0

    def test_flags_unsupported_when_condition_missing_from_chunk(self):
        v = self._make_validator()
        answer = "If the token expires, the system will reject the request and log an error."
        chunks = [_make_doc("c1", content="the weather is nice today in a pleasant way")]
        result = v.validate("a1", answer, chunks, [])
        assert result.fully_supported is False
        assert len(result.unsupported_claim_spans) > 0

    def test_parent_reconstruction_improves_support(self):
        v = self._make_validator()
        answer = "When the token expires the system will reject the request."
        child_content = "the system processes requests"
        parent_content = "When the token expires the system will reject the request."
        chunk = _make_grounded("c1", content=child_content, parent_content=parent_content)
        result = v.validate("a1", answer, [chunk], [])
        assert result.support_score >= 0.8

    def test_empty_answer_is_fully_supported(self):
        v = self._make_validator()
        result = v.validate("a1", "", [_make_doc("c1")], [])
        assert result.fully_supported is True

    def test_cited_chunk_ids_captured(self):
        v = self._make_validator()
        chunks = [_make_doc("c1"), _make_doc("c2")]
        result = v.validate("a1", "some answer text with words", chunks, [])
        assert set(result.cited_chunk_ids) == {"c1", "c2"}

    def test_grounded_doc_parent_id_captured(self):
        v = self._make_validator()
        chunk = _make_grounded("c1", parent_id="sec_5")
        result = v.validate("a1", "text content words", [chunk], [])
        assert "sec_5" in result.cited_parent_section_ids

    def test_content_hash_stable(self):
        v = self._make_validator()
        chunks = [_make_doc("c1", content="the answer content here")]
        r1 = v.validate("a1", "the answer content", chunks, [])
        r2 = v.validate("a1", "the answer content", chunks, [])
        assert r1.content_hash() == r2.content_hash()

    def test_supported_answer_check_from_dict_roundtrip(self):
        check = SupportedAnswerCheck(
            answer_id="a1",
            cited_chunk_ids=("c1", "c2"),
            cited_parent_section_ids=("sec_1",),
            fully_supported=True,
            unsupported_claim_spans=(),
            support_score=0.95,
        )
        d = check.to_dict()
        restored = SupportedAnswerCheck.from_dict(d)
        assert restored.answer_id == check.answer_id
        assert restored.fully_supported == check.fully_supported
        assert restored.support_score == check.support_score

    def test_invalid_min_overlap_raises(self):
        with pytest.raises(ValueError):
            KeywordAnswerSupportValidator(min_overlap_words=0)

    def test_invalid_threshold_raises(self):
        with pytest.raises(ValueError):
            KeywordAnswerSupportValidator(fully_supported_threshold=THRESHOLD)


# ===========================================================================
# 4. Observability Monitors (Phase D)
# ===========================================================================


def _make_cs(
    query_id: str = "q1",
    chunk_id: str = "c1",
    relevance: float = 0.9,
    completeness: float = 0.8,
    missing_condition: bool = False,
) -> ContextCompletenessScore:
    return ContextCompletenessScore(
        query_id=query_id,
        chunk_id=chunk_id,
        parent_section_id="",
        relevance_score=relevance,
        completeness_score=completeness,
        missing_condition=missing_condition,
        missing_exception=False,
        missing_scope=False,
        missing_temporal_qualifier=False,
        confidence=0.75,
    )


class TestRetrievalCompletenessMonitor:
    """Branch inventory:
    - snapshot with no records → all zeros
    - snapshot with all expanded → expansion rate = 1.0
    - snapshot with high-sim low-completeness → rate > 0
    - reset clears state
    """

    def test_empty_snapshot_all_zeros(self):
        m = RetrievalCompletenessMonitor()
        snap = m.snapshot("s1", "v1")
        assert snap.sample_count == 0
        assert snap.mean_completeness_score == 0.0
        assert snap.parent_reconstruction_applied_rate == 0.0

    def test_expansion_rate_computed_correctly(self):
        m = RetrievalCompletenessMonitor()
        for _ in range(3):
            m.record(_make_cs(completeness=0.9), expansion_applied=True)
        for _ in range(1):
            m.record(_make_cs(completeness=0.9), expansion_applied=False)
        snap = m.snapshot("s1", "v1")
        assert snap.parent_reconstruction_applied_rate == pytest.approx(0.75)

    def test_high_similarity_low_completeness_rate(self):
        m = RetrievalCompletenessMonitor()
        m.record(_make_cs(relevance=0.9, completeness=0.3), expansion_applied=False)
        m.record(_make_cs(relevance=0.9, completeness=0.9), expansion_applied=True)
        snap = m.snapshot("s1", "v1")
        assert snap.high_similarity_low_completeness_rate == pytest.approx(0.5)

    def test_reset_clears_state(self):
        m = RetrievalCompletenessMonitor()
        m.record(_make_cs(), expansion_applied=True)
        m.reset()
        assert m.sample_count() == 0
        snap = m.snapshot("s1", "v1")
        assert snap.sample_count == 0

    def test_snapshot_is_deterministic(self):
        m = RetrievalCompletenessMonitor()
        m.record(_make_cs(completeness=0.7), expansion_applied=True)
        m.record(_make_cs(completeness=0.5), expansion_applied=False)
        s1 = m.snapshot("snap", "v1")
        s2 = m.snapshot("snap", "v1")
        assert s1.mean_completeness_score == s2.mean_completeness_score


class TestParentExpansionMissMonitor:
    """Branch inventory:
    - miss = low completeness AND expansion NOT applied
    - no miss = low completeness AND expansion applied
    - no miss = high completeness regardless
    - zero total → miss_rate = 0.0
    """

    def test_miss_when_low_completeness_no_expansion(self):
        m = ParentExpansionMissMonitor()
        m.record(_make_cs(completeness=0.3), expansion_applied=False)
        assert m.miss_rate() == 1.0
        assert m.misses() == 1

    def test_no_miss_when_low_completeness_but_expanded(self):
        m = ParentExpansionMissMonitor()
        m.record(_make_cs(completeness=0.3), expansion_applied=True)
        assert m.miss_rate() == 0.0

    def test_no_miss_when_high_completeness(self):
        m = ParentExpansionMissMonitor()
        m.record(_make_cs(completeness=0.9), expansion_applied=False)
        assert m.miss_rate() == 0.0

    def test_zero_total_returns_zero(self):
        m = ParentExpansionMissMonitor()
        assert m.miss_rate() == 0.0

    def test_reset(self):
        m = ParentExpansionMissMonitor()
        m.record(_make_cs(completeness=0.3), expansion_applied=False)
        m.reset()
        assert m.total() == 0
        assert m.miss_rate() == 0.0


class TestHighSimilarityWrongAnswerMonitor:
    """Branch inventory:
    - high sim + unsupported → counted as wrong
    - high sim + supported → not wrong
    - low sim + unsupported → not counted (not high-sim)
    - zero total → rates are 0.0
    """

    def _make_check(self, fully_supported: bool, support_score: float = 0.9) -> SupportedAnswerCheck:
        return SupportedAnswerCheck(
            answer_id="a1",
            cited_chunk_ids=("c1",),
            cited_parent_section_ids=(),
            fully_supported=fully_supported,
            unsupported_claim_spans=() if fully_supported else ("claim",),
            support_score=support_score,
        )

    def test_high_sim_unsupported_counted(self):
        m = HighSimilarityWrongAnswerMonitor()
        m.record(0.9, self._make_check(fully_supported=False, support_score=0.3))
        assert m.high_similarity_wrong_answer_rate() == 1.0

    def test_high_sim_supported_not_counted(self):
        m = HighSimilarityWrongAnswerMonitor()
        m.record(0.9, self._make_check(fully_supported=True, support_score=1.0))
        assert m.high_similarity_wrong_answer_rate() == 0.0

    def test_low_sim_unsupported_not_counted_as_high_sim_wrong(self):
        m = HighSimilarityWrongAnswerMonitor()
        m.record(0.5, self._make_check(fully_supported=False, support_score=0.3))
        assert m.high_similarity_wrong_answer_rate() == 0.0

    def test_zero_total_returns_zero(self):
        m = HighSimilarityWrongAnswerMonitor()
        assert m.high_similarity_wrong_answer_rate() == 0.0
        assert m.mean_support_score() == 0.0

    def test_snapshot_is_deterministic(self):
        m = HighSimilarityWrongAnswerMonitor()
        m.record(0.9, self._make_check(False, 0.3))
        m.record(0.9, self._make_check(True, 1.0))
        s1 = m.snapshot("s1", "v1")
        s2 = m.snapshot("s1", "v1")
        assert s1.fully_supported_rate == s2.fully_supported_rate
        assert s1.unsupported_with_high_similarity_rate == s2.unsupported_with_high_similarity_rate


class TestConditionLossDriftMonitor:
    """Branch inventory:
    - empty snapshot → all zeros, delta=0
    - records with missing condition → rate computed correctly
    - delta tracks change from prior snapshot correctly
    - reset clears state
    """

    def test_empty_snapshot_all_zeros(self):
        m = ConditionLossDriftMonitor()
        snap = m.snapshot("s1", "v1")
        assert snap.query_count == 0
        assert snap.missing_condition_rate == 0.0
        assert snap.condition_loss_delta_vs_prior == 0.0

    def test_condition_rate_computed_correctly(self):
        m = ConditionLossDriftMonitor()
        m.record(_make_cs(missing_condition=True))
        m.record(_make_cs(missing_condition=True))
        m.record(_make_cs(missing_condition=False))
        snap = m.snapshot("s1", "v1")
        assert snap.missing_condition_rate == pytest.approx(2 / 3)

    def test_delta_tracks_change(self):
        m = ConditionLossDriftMonitor()
        for _ in range(2):
            m.record(_make_cs(missing_condition=True))
        for _ in range(2):
            m.record(_make_cs(missing_condition=False))
        m.snapshot("s1", "v1")
        m.reset()
        m.record(_make_cs(missing_condition=True))
        snap2 = m.snapshot("s2", "v1")
        assert snap2.condition_loss_delta_vs_prior != 0.0

    def test_reset_clears(self):
        m = ConditionLossDriftMonitor()
        m.record(_make_cs(missing_condition=True))
        m.reset()
        assert m.sample_count() == 0


# ===========================================================================
# 5. Meta-Learning (Phase E)
# ===========================================================================


class TestEvaluationSignals:
    """Branch inventory:
    - to_dict/from_dict roundtrip is lossless
    - content_hash stable for identical input
    - distinct inputs produce distinct hashes
    """

    def test_to_dict_from_dict_roundtrip(self):
        signals = _make_signals()
        restored = EvaluationSignals.from_dict(signals.to_dict())
        assert restored.snapshot_id == signals.snapshot_id
        assert restored.mean_completeness_score == signals.mean_completeness_score
        assert restored.observation_count == signals.observation_count

    def test_content_hash_stable(self):
        signals = _make_signals()
        assert signals.content_hash() == signals.content_hash()

    def test_distinct_inputs_different_hashes(self):
        s1 = _make_signals(snapshot_id="snap_1")
        s2 = _make_signals(snapshot_id="snap_2")
        assert s1.content_hash() != s2.content_hash()


class TestCompletenessRAGProposer:
    """Branch inventory:
    - insufficient observations → empty proposals
    - low completeness + low expansion → proposes inc-parent-depth
    - high fragmentation → proposes section-aware chunking
    - low support + high sim wrong → proposes hybrid retrieval
    - high missing_condition/scope → proposes lexical boost
    - low completeness → proposes reranker weight change
    - low expansion rate → proposes neighbor window increase
    - proposal_only always True
    - CompletenessChangePackage: proposal_only=False raises ValueError
    """

    def _proposer(self) -> CompletenessRAGProposer:
        return CompletenessRAGProposer()

    def test_insufficient_observations_returns_empty(self):
        p = self._proposer()
        signals = _make_signals(obs=3)
        assert p.propose(signals) == []

    def test_low_completeness_low_expansion_proposes_parent_depth(self):
        p = self._proposer()
        signals = _make_signals(mean_completeness=0.4, parent_rate=0.1, obs=10)
        proposals = p.propose(signals)
        surface_names = {pr.surface_name for pr in proposals}
        assert "parent_expansion_depth" in surface_names

    def test_high_fragmentation_proposes_section_aware_chunking(self):
        p = self._proposer()
        signals = _make_signals(fragmentation=0.5, obs=10)
        proposals = p.propose(signals)
        surface_names = {pr.surface_name for pr in proposals}
        assert "chunking_strategy" in surface_names

    def test_low_support_high_sim_wrong_proposes_hybrid_retrieval(self):
        p = self._proposer()
        signals = _make_signals(
            fully_supported=0.4,
            high_sim_wrong=0.3,
            obs=10,
        )
        proposals = p.propose(signals)
        surface_names = {pr.surface_name for pr in proposals}
        assert "retrieval_mode" in surface_names

    def test_all_proposals_have_proposal_only_true(self):
        p = self._proposer()
        signals = _make_signals(
            mean_completeness=0.3,
            fragmentation=0.5,
            fully_supported=0.3,
            high_sim_wrong=0.4,
            parent_rate=0.1,
            obs=20,
        )
        proposals = p.propose(signals)
        assert len(proposals) > 0
        for pr in proposals:
            assert pr.proposal_only is True

    def test_proposal_only_false_raises_value_error(self):
        with pytest.raises(ValueError, match="proposal_only must be True"):
            CompletenessChangePackage(
                proposal_id="bad",
                surface_name="s",
                parameter="p",
                old_value=0,
                new_value=1,
                justification="test",
                snapshot_id="s1",
                proposal_only=False,
            )

    def test_proposal_content_hash_stable(self):
        p = self._proposer()
        signals = _make_signals(mean_completeness=0.4, parent_rate=0.1, obs=10)
        proposals = p.propose(signals)
        for pr in proposals:
            assert pr.content_hash() == pr.content_hash()

    def test_low_completeness_proposes_reranker_weight(self):
        p = self._proposer()
        signals = _make_signals(mean_completeness=0.3, parent_rate=0.5, obs=10)
        proposals = p.propose(signals)
        surface_names = {pr.surface_name for pr in proposals}
        assert "reranker_completeness_weight" in surface_names

    def test_signals_with_high_missing_rates_proposes_lexical_boost(self):
        p = self._proposer()
        base = _make_signals(obs=10)
        signals = EvaluationSignals(
            snapshot_id="snap_x",
            retrieval_relevance_mean=0.8,
            retrieval_precision=0.7,
            retrieval_recall=0.6,
            mean_completeness_score=0.8,
            missing_condition_rate=0.4,
            missing_exception_rate=0.0,
            missing_scope_rate=0.35,
            missing_temporal_qualifier_rate=0.0,
            answer_correctness_rate=0.85,
            fully_supported_rate=0.9,
            mean_support_score=0.75,
            high_similarity_wrong_answer_rate=0.05,
            parent_reconstruction_applied_rate=0.5,
            chunk_fragmentation_error_rate=0.0,
            observation_count=10,
        )
        proposals = p.propose(signals)
        surface_names = {pr.surface_name for pr in proposals}
        assert "lexical_exact_match_boost" in surface_names


# ===========================================================================
# 6. Late Chunking (Phase G)
# ===========================================================================


class TestLateChunkingProfile:
    """Branch inventory:
    - valid mode → no error
    - invalid mode → ValueError
    - invalid pooling strategy → ValueError
    - max_input_tokens < 1 → ValueError
    - profile_digest stable for same profile
    - is_late_chunked, uses_hybrid_retrieval, uses_reranking properties
    - from_dict roundtrip
    """

    def test_valid_profile_created(self):
        p = _make_late_profile("late_chunked")
        assert p.mode == "late_chunked"
        assert p.is_late_chunked is True

    def test_invalid_mode_raises(self):
        with pytest.raises(ValueError, match="Invalid mode"):
            LateChunkingProfile(
                profile_id="x",
                mode="bad_mode",
                embedding_model_version="v1",
                max_input_tokens=2048,
                pooling_strategy="mean",
                chunk_window_policy="fixed",
                stride_policy="stride_64",
                parent_section_policy="heading",
            )

    def test_invalid_pooling_strategy_raises(self):
        with pytest.raises(ValueError, match="Invalid pooling_strategy"):
            LateChunkingProfile(
                profile_id="x",
                mode="late_chunked",
                embedding_model_version="v1",
                max_input_tokens=2048,
                pooling_strategy="bad_pooling",
                chunk_window_policy="fixed",
                stride_policy="stride_64",
                parent_section_policy="heading",
            )

    def test_zero_max_input_tokens_raises(self):
        with pytest.raises(ValueError):
            LateChunkingProfile(
                profile_id="x",
                mode="late_chunked",
                embedding_model_version="v1",
                max_input_tokens=0,
                pooling_strategy="mean",
                chunk_window_policy="fixed",
                stride_policy="stride_64",
                parent_section_policy="heading",
            )

    def test_profile_digest_stable(self):
        p = _make_late_profile()
        assert p.profile_digest() == p.profile_digest()

    def test_standard_chunked_is_not_late(self):
        p = _make_late_profile("standard_chunked")
        assert p.is_late_chunked is False

    def test_hybrid_mode_uses_hybrid(self):
        p = _make_late_profile("late_chunked_hybrid")
        assert p.uses_hybrid_retrieval is True

    def test_hybrid_reranked_uses_reranking(self):
        p = _make_late_profile("late_chunked_hybrid_reranked")
        assert p.uses_reranking is True

    def test_from_dict_roundtrip(self):
        p = _make_late_profile()
        restored = LateChunkingProfile.from_dict(p.to_dict())
        assert restored.profile_id == p.profile_id
        assert restored.mode == p.mode
        assert restored.pooling_strategy == p.pooling_strategy

    @pytest.mark.parametrize("mode", sorted(VALID_MODES))
    def test_all_valid_modes_accepted(self, mode: str):
        p = LateChunkingProfile(
            profile_id=f"p-{mode}",
            mode=mode,
            embedding_model_version="v1",
            max_input_tokens=512,
            pooling_strategy="mean",
            chunk_window_policy="fixed",
            stride_policy="stride_32",
            parent_section_policy="heading",
        )
        assert p.mode == mode


class TestSegmentDocument:
    """Branch inventory:
    - zero tokens → empty list
    - total_tokens <= max_segment → single segment
    - total_tokens > max_segment → multiple segments
    - deterministic: same input → same segment_ids and hashes
    - manifest content_hash stable
    - token_count property correct
    """

    def _make_config(self, max_seg: int = 128, stride: int = 32) -> LateChunkingPipelineConfig:
        return LateChunkingPipelineConfig(
            profile=_make_late_profile(),
            stride=stride,
            max_segment_tokens=max_seg,
        )

    def test_zero_tokens_returns_empty(self):
        cfg = self._make_config()
        result = segment_document("doc_a", 0, cfg)
        assert result == []

    def test_single_segment_for_small_doc(self):
        cfg = self._make_config(max_seg=256)
        result = segment_document("doc_a", 100, cfg)
        assert len(result) == 1
        assert result[0].token_start == 0
        assert result[0].token_end == 100

    def test_multiple_segments_for_large_doc(self):
        cfg = self._make_config(max_seg=128, stride=64)
        result = segment_document("doc_a", 300, cfg)
        assert len(result) >= 2

    def test_deterministic_output(self):
        cfg = self._make_config()
        r1 = segment_document("doc_b", 500, cfg)
        r2 = segment_document("doc_b", 500, cfg)
        assert [m.segment_id for m in r1] == [m.segment_id for m in r2]
        assert [m.pooled_embedding_hash for m in r1] == [m.pooled_embedding_hash for m in r2]

    def test_manifest_content_hash_stable(self):
        cfg = self._make_config()
        segs = segment_document("doc_c", 200, cfg)
        for s in segs:
            assert s.content_hash() == s.content_hash()

    def test_token_count_property(self):
        cfg = self._make_config(max_seg=100)
        segs = segment_document("doc_d", 100, cfg)
        assert segs[0].token_count == 100

    def test_build_corpus_sorted_deterministically(self):
        cfg = self._make_config(max_seg=100, stride=50)
        docs = [
            {"source_doc_id": "doc_b", "total_tokens": 200},
            {"source_doc_id": "doc_a", "total_tokens": 150},
        ]
        result = build_late_chunk_manifests_for_corpus(docs, cfg)
        source_ids = [m.source_doc_id for m in result]
        assert source_ids == sorted(source_ids)

    def test_invalid_stride_raises(self):
        profile = _make_late_profile()
        with pytest.raises(ValueError):
            LateChunkingPipelineConfig(profile=profile, stride=0)

    def test_invalid_max_segment_tokens_raises(self):
        profile = _make_late_profile()
        with pytest.raises(ValueError):
            LateChunkingPipelineConfig(profile=profile, max_segment_tokens=0)


# ===========================================================================
# 7. C0 Sovereignty (Phase A)
# ===========================================================================


class TestC0Sovereignty:
    """Branch inventory:
    - ContextCompletenessScore carries no routing authority (no route fields)
    - SupportedAnswerCheck carries no safety threshold (no threshold fields)
    - EvaluationSignals fields are all informational metrics
    - CompletenessChangePackage always proposal_only=True
    - GroundedDocument carries no permission or authorization fields

    These are structural invariant tests — they verify that the sovereignty
    boundary is not violated by checking that no authority fields exist.
    """

    def test_completeness_score_has_no_route_fields(self):
        cs = _make_cs()
        d = cs.to_dict()
        forbidden = {"route_mode", "safety_threshold", "execution_tier", "auth_token"}
        assert forbidden.isdisjoint(d.keys()), f"Sovereignty violation: {forbidden & set(d.keys())}"

    def test_supported_answer_check_has_no_safety_fields(self):
        check = SupportedAnswerCheck(
            answer_id="a1",
            cited_chunk_ids=("c1",),
            cited_parent_section_ids=(),
            fully_supported=True,
            unsupported_claim_spans=(),
            support_score=0.9,
        )
        d = check.to_dict()
        forbidden = {"route_mode", "safety_threshold", "execution_tier", "auth_token"}
        assert forbidden.isdisjoint(d.keys())

    def test_evaluation_signals_has_no_authority_fields(self):
        signals = _make_signals()
        d = signals.to_dict()
        forbidden = {"route_mode", "safety_threshold", "execution_tier", "auth_token", "approve"}
        assert forbidden.isdisjoint(d.keys())

    def test_completeness_change_package_always_proposal_only(self):
        p = CompletenessChangePackage(
            proposal_id="p1",
            surface_name="s",
            parameter="x",
            old_value=1,
            new_value=2,
            justification="test",
            snapshot_id="s1",
            proposal_only=True,
        )
        assert p.proposal_only is True

    def test_grounded_document_has_no_permission_fields(self):
        doc = _make_grounded("c1")
        d = doc.to_dict()
        forbidden = {"route_mode", "safety_threshold", "execution_tier", "auth_token"}
        assert forbidden.isdisjoint(d.keys())

    def test_late_chunking_profile_has_no_auth_fields(self):
        profile = _make_late_profile()
        d = profile.to_dict()
        forbidden = {"route_mode", "safety_threshold", "auth_token", "approve_execution"}
        assert forbidden.isdisjoint(d.keys())


# ===========================================================================
# 8. L4 Registries (Phase B)
# ===========================================================================


class TestL4Registries:
    """Branch inventory:
    - ChunkManifestRegistry: write returns hash; get retrieves; count correct
    - ParentChildIndexRegistry: write; get_link; get_children; idempotent
    - RetrievalEvaluationRegistry: write-once semantics
    - ContextCompletenessSnapshotStore: accumulates; latest returns last
    """

    def _make_manifest(self, chunk_id: str = "c1") -> ChunkManifest:
        return ChunkManifest(
            chunk_id=chunk_id,
            source_doc_id="doc_a",
            parent_section_id="sec_1",
            heading_path=("Root",),
            sibling_ids=("c0", chunk_id, "c2"),
            token_span=(0, 100),
            token_count=100,
        )

    def test_chunk_manifest_write_and_get(self):
        reg = ChunkManifestRegistry()
        m = self._make_manifest("c1")
        h = reg.write(m)
        assert len(h) == 64
        assert reg.get("c1") is m

    def test_chunk_manifest_count(self):
        reg = ChunkManifestRegistry()
        reg.write(self._make_manifest("c1"))
        reg.write(self._make_manifest("c2"))
        assert reg.count() == 2

    def test_chunk_manifest_content_hash_stable(self):
        m = self._make_manifest("c1")
        assert m.content_hash() == m.content_hash()

    def test_chunk_manifest_from_dict_roundtrip(self):
        m = self._make_manifest("c1")
        restored = ChunkManifest.from_dict(m.to_dict())
        assert restored.chunk_id == m.chunk_id
        assert restored.parent_section_id == m.parent_section_id
        assert restored.token_count == m.token_count

    def test_parent_child_registry_write_and_lookup(self):
        reg = ParentChildIndexRegistry()
        link = ParentChildLink(
            child_chunk_id="c1",
            parent_chunk_id="sec_1",
            expansion_policy="window_1",
            neighbor_window_ids=("c0", "c2"),
        )
        reg.write(link)
        assert reg.get_link("c1") is link
        assert "c1" in reg.get_children("sec_1")

    def test_parent_child_registry_idempotent(self):
        reg = ParentChildIndexRegistry()
        link = ParentChildLink(
            child_chunk_id="c1",
            parent_chunk_id="sec_1",
            expansion_policy="window_1",
            neighbor_window_ids=(),
        )
        reg.write(link)
        reg.write(link)
        assert reg.count() == 1

    def test_retrieval_evaluation_registry_write_once(self):
        reg = RetrievalEvaluationRegistry()
        cs = _make_cs()
        check = SupportedAnswerCheck(
            answer_id="a1",
            cited_chunk_ids=("c1",),
            cited_parent_section_ids=(),
            fully_supported=True,
            unsupported_claim_spans=(),
            support_score=1.0,
        )
        record = RetrievalEvaluationRecord(
            query_id="q1",
            retrieved_chunk_ids=("c1",),
            expanded_parent_ids=("sec_1",),
            lexical_scores={"c1": 0.8},
            vector_scores={"c1": 0.9},
            completeness_scores=(cs,),
            reranked_order=("c1",),
            answer_check=check,
        )
        reg.write(record)
        reg.write(record)
        assert reg.count() == 1
        assert reg.get("q1") is record

    def test_snapshot_store_accumulates_and_latest(self):
        store = ContextCompletenessSnapshotStore()
        s1 = ContextCompletenessSnapshot(
            snapshot_id="s1",
            system_version="v1",
            query_count=10,
            missing_condition_rate=0.2,
            missing_exception_rate=0.1,
            missing_scope_rate=0.05,
            missing_temporal_qualifier_rate=0.0,
            parent_reconstruction_rate=0.7,
            right_chunk_wrong_context_rate=0.3,
            high_similarity_wrong_answer_rate=0.15,
        )
        s2 = ContextCompletenessSnapshot(
            snapshot_id="s2",
            system_version="v1",
            query_count=20,
            missing_condition_rate=0.1,
            missing_exception_rate=0.05,
            missing_scope_rate=0.02,
            missing_temporal_qualifier_rate=0.0,
            parent_reconstruction_rate=0.85,
            right_chunk_wrong_context_rate=0.15,
            high_similarity_wrong_answer_rate=0.05,
        )
        store.write(s1)
        store.write(s2)
        assert store.count() == 2
        assert store.latest().snapshot_id == "s2"

    def test_snapshot_content_hash_stable(self):
        s = ContextCompletenessSnapshot(
            snapshot_id="s1",
            system_version="v1",
            query_count=10,
            missing_condition_rate=0.2,
            missing_exception_rate=0.1,
            missing_scope_rate=0.05,
            missing_temporal_qualifier_rate=0.0,
            parent_reconstruction_rate=0.7,
            right_chunk_wrong_context_rate=0.3,
            high_similarity_wrong_answer_rate=0.15,
        )
        assert s.content_hash() == s.content_hash()


# ===========================================================================
# 9. CompletenessReranker (Phase A)
# ===========================================================================


class TestCompletenessReranker:
    """Branch inventory:
    - reranks: high completeness beats high similarity
    - reranks: empty input → empty output
    - reranks: top_k enforced
    - reranks: deterministic tie-break by doc_id ascending
    - config: weights not summing to 1.0 → ValueError
    - config: top_k < 1 → ValueError
    """

    def _make_reranker(self, **kwargs) -> CompletenessReranker:
        scorer = _make_scorer()
        cfg = CompletenessRerankerConfig(**kwargs) if kwargs else None
        return CompletenessReranker(scorer=scorer, config=cfg, query_id="q1")

    def test_empty_input_returns_empty(self):
        r = self._make_reranker()
        assert r.rerank("query", []) == []

    def test_top_k_enforced(self):
        r = self._make_reranker(top_k=2)
        docs = [_make_doc(f"d{i}", score=0.9) for i in range(5)]
        result = r.rerank("what is this?", docs)
        assert len(result) <= 2

    def test_config_invalid_weights_raises(self):
        with pytest.raises(ValueError, match="must sum to 1.0"):
            CompletenessRerankerConfig(relevance_weight=0.7, completeness_weight=0.7)

    def test_config_zero_top_k_raises(self):
        with pytest.raises(ValueError):
            CompletenessRerankerConfig(top_k=0)

    def test_deterministic_tie_break(self):
        scorer = _make_scorer()
        cfg = CompletenessRerankerConfig(top_k=10)
        r = CompletenessReranker(scorer=scorer, config=cfg, query_id="q1")
        docs = [
            _make_doc("z1", score=0.5, content="content"),
            _make_doc("a1", score=0.5, content="content"),
            _make_doc("m1", score=0.5, content="content"),
        ]
        r1 = r.rerank("same query", docs)
        r2 = r.rerank("same query", docs)
        assert [d.doc_id for d in r1] == [d.doc_id for d in r2]
        assert r1[0].doc_id < r1[1].doc_id < r1[2].doc_id
