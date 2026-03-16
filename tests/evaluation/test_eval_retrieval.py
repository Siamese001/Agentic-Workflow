"""
Tests: Phase 2 — Hybrid Retrieval and Reranking

Branch coverage:
- Document: to_dict
- ReciprocalRankFusion: invalid k, single list empty, both populated, dedup
- ScoreFusion: empty inputs, single source, dual source normalization
- HeuristicReranker: empty candidates, top_k truncation, scorer injection
- PassthroughReranker: truncation, empty
- RetrievalPipeline: vector_only, hybrid, hybrid_reranked, unknown mode
- make_profile: valid modes, invalid mode
- RetrievalProfileConfig: to_dict, from_dict roundtrip
"""

import pytest
from agentic_core.evaluation.retrieval.fusion import ReciprocalRankFusion, ScoreFusion
from agentic_core.evaluation.retrieval.interfaces import (
    Document,
    IRetrieverLexical,
    IRetrieverVector,
)
from agentic_core.evaluation.retrieval.profiles import (
    PROFILE_HYBRID,
    PROFILE_HYBRID_RERANKED,
    PROFILE_VECTOR_ONLY,
    RetrievalPipeline,
    RetrievalProfileConfig,
    make_profile,
)
from agentic_core.evaluation.retrieval.reranker import HeuristicReranker, PassthroughReranker

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("test_eval_retrieval", "p4obs", "metric_1")
_emit_emits_metric_event("test_eval_retrieval", "p4obs", "metric_2")
_emit_emits_metric_event("test_eval_retrieval", "p4obs", "metric_3")
_emit_emits_metric_event("test_eval_retrieval", "p4obs", "metric_4")
_emit_emits_metric_event("test_eval_retrieval", "p4obs", "metric_5")
_emit_emits_metric_event("test_eval_retrieval", "p4obs", "metric_6")
_emit_records_incident_event("test_eval_retrieval", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_eval_retrieval", "p4obs", "anomaly")
_emit_writes_observability_log("test_eval_retrieval", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_eval_retrieval", "p4obs", "mon_state")
_emit_triggers_alert("test_eval_retrieval", "p4obs", "alert")
_emit_links_incident_trace("test_eval_retrieval", "p4obs", "trace_link")
_emit_captures_pattern("test_eval_retrieval", "p3lm", "pattern")
_emit_records_learning_event("test_eval_retrieval", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_eval_retrieval", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_eval_retrieval", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_eval_retrieval", "p3lm", "routing")
_emit_improves_agent_policy("test_eval_retrieval", "p3lm", "policy")
_emit_stores_learning_state("test_eval_retrieval", "p3lm", "state")
_emit_records_execution_trace("test_eval_retrieval", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_eval_retrieval", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_eval_retrieval", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_eval_retrieval", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_eval_retrieval", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_eval_retrieval", "env_read", "p2_env_1")
_emit_reads_environ("test_eval_retrieval", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_eval_retrieval", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_eval_retrieval", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_eval_retrieval")
_emit_applies_guardrail("p0", "test_eval_retrieval", "p0_governance")
_emit_reads_policy_state("p0", "test_eval_retrieval", "policy_binding")
_emit_snapshots_state("p0", "test_eval_retrieval", "state_snapshot")
_emit_pulls_context("p1", "test_eval_retrieval", "context_pull")
_emit_pulls_context("p1", "test_eval_retrieval", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_eval_retrieval", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_eval_retrieval", "uwg_term_secondary")
_emit_writes_through("p1", "test_eval_retrieval", "write_through")
_emit_writes_through("p1", "test_eval_retrieval", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_eval_retrieval", "safety_validation")
_emit_invokes_eval("p1", "test_eval_retrieval", "eval_call")
_emit_proposal_commits_routing("p1", "test_eval_retrieval", "routing_commit")
emit_replay_key("p0", "test_eval_retrieval")
emit_determinism_digest("p0", "test_eval_retrieval")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_eval_retrieval", "execution_auth")
_emit_validates_capability("p2", "test_eval_retrieval", "capability_check")
_emit_routes_to_capability("p2", "test_eval_retrieval", "capability_route")
_emit_writes_via_uwg("p2", "test_eval_retrieval", "uwg_write")
_emit_blocks_direct_write("p2", "test_eval_retrieval", "direct_write_block")
_emit_records_tool_invocation("p2", "test_eval_retrieval", "tool_invocation")
_emit_captures_execution_output("p2", "test_eval_retrieval", "exec_output")
_emit_dispatches_agent("p3", "test_eval_retrieval", "agent_dispatch")
_emit_coordinates_agents("p3", "test_eval_retrieval", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_eval_retrieval", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_eval_retrieval", "healing_outcome")
_emit_escalates_failure("p3", "test_eval_retrieval", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_eval_retrieval", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_eval_retrieval", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_eval_retrieval", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_eval_retrieval", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_eval_retrieval", "eval_metric")
_emit_stores_embedding("p4", "test_eval_retrieval", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_eval_retrieval", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_eval_retrieval", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Stub retrievers for testing
# ---------------------------------------------------------------------------


class StubLexicalRetriever(IRetrieverLexical):
    def __init__(self, docs):
        self._docs = docs

    def retrieve(self, query: str, top_k: int = 50) -> list[Document]:
        return self._docs[:top_k]


class StubVectorRetriever(IRetrieverVector):
    def __init__(self, docs):
        self._docs = docs

    def retrieve(self, query_embedding, top_k=50) -> list[Document]:
        return self._docs[:top_k]

    def embed_query(self, query: str) -> list[float]:
        return [0.1, 0.2, 0.3]


def _make_doc(doc_id, score=1.0, content="content"):
    return Document(doc_id=doc_id, content=content, score=score)


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------


class TestDocument:
    def test_to_dict_keys(self):
        d = _make_doc("doc_1", 0.8).to_dict()
        assert set(d.keys()) == {"doc_id", "content", "score", "metadata"}

    def test_defaults(self):
        doc = Document(doc_id="x", content="text")
        assert doc.score == 0.0
        assert doc.metadata == {}


# ---------------------------------------------------------------------------
# ReciprocalRankFusion
# ---------------------------------------------------------------------------


class TestReciprocalRankFusion:
    def test_invalid_k_raises(self):
        with pytest.raises(ValueError):
            ReciprocalRankFusion(k=0)
        with pytest.raises(ValueError):
            ReciprocalRankFusion(k=-1)

    def test_empty_both_returns_empty(self):
        rrf = ReciprocalRankFusion()
        assert rrf.merge([], []) == []

    def test_one_empty_list(self):
        rrf = ReciprocalRankFusion()
        docs = [_make_doc("doc_1"), _make_doc("doc_2")]
        result = rrf.merge(docs, [])
        assert len(result) == 2

    def test_merge_deduplicates(self):
        rrf = ReciprocalRankFusion()
        lexical = [_make_doc("doc_1", 1.0), _make_doc("doc_2", 0.9)]
        vector = [_make_doc("doc_1", 0.95), _make_doc("doc_3", 0.8)]
        result = rrf.merge(lexical, vector)
        ids = [d.doc_id for d in result]
        assert ids.count("doc_1") == 1

    def test_doc_in_both_lists_ranked_higher(self):
        rrf = ReciprocalRankFusion()
        shared = _make_doc("doc_shared", 1.0)
        lexical = [shared, _make_doc("doc_lex_only", 0.9)]
        vector = [shared, _make_doc("doc_vec_only", 0.85)]
        result = rrf.merge(lexical, vector)
        # doc_shared appears in both → higher RRF score than single-list docs
        top_id = result[0].doc_id
        assert top_id == "doc_shared"

    def test_result_sorted_by_descending_score(self):
        rrf = ReciprocalRankFusion()
        lexical = [_make_doc(f"lex_{i}", 1.0 / (i + 1)) for i in range(5)]
        vector = [_make_doc(f"vec_{i}", 1.0 / (i + 1)) for i in range(5)]
        result = rrf.merge(lexical, vector)
        scores = [d.score for d in result]
        assert scores == sorted(scores, reverse=True)

    def test_deterministic_same_input(self):
        rrf = ReciprocalRankFusion()
        lexical = [_make_doc("a"), _make_doc("b")]
        vector = [_make_doc("b"), _make_doc("c")]
        r1 = [d.doc_id for d in rrf.merge(lexical, vector)]
        r2 = [d.doc_id for d in rrf.merge(lexical, vector)]
        assert r1 == r2


# ---------------------------------------------------------------------------
# ScoreFusion
# ---------------------------------------------------------------------------


class TestScoreFusion:
    def test_empty_both(self):
        sf = ScoreFusion()
        assert sf.merge([], []) == []

    def test_single_source(self):
        sf = ScoreFusion()
        docs = [_make_doc("doc_1", 0.9), _make_doc("doc_2", 0.5)]
        result = sf.merge(docs, [])
        assert {d.doc_id for d in result} == {"doc_1", "doc_2"}

    def test_all_same_scores_normalized_to_one(self):
        sf = ScoreFusion()
        docs = [_make_doc(f"doc_{i}", 0.5) for i in range(3)]
        result = sf.merge(docs, [])
        # all scores equal → normalized to 1.0
        for d in result:
            assert d.score == pytest.approx(1.0)

    def test_shared_doc_gets_averaged_score(self):
        sf = ScoreFusion()
        # doc_shared in both with max score → fused score = avg(1.0, 1.0) = 1.0
        lexical = [_make_doc("doc_shared", 1.0), _make_doc("doc_lex", 0.5)]
        vector = [_make_doc("doc_shared", 1.0), _make_doc("doc_vec", 0.3)]
        result = sf.merge(lexical, vector)
        shared = next(d for d in result if d.doc_id == "doc_shared")
        assert shared.score == pytest.approx(1.0)

    def test_result_sorted_descending(self):
        sf = ScoreFusion()
        lexical = [_make_doc("a", 1.0), _make_doc("b", 0.5)]
        vector = [_make_doc("c", 0.8)]
        result = sf.merge(lexical, vector)
        scores = [d.score for d in result]
        assert scores == sorted(scores, reverse=True)


# ---------------------------------------------------------------------------
# HeuristicReranker
# ---------------------------------------------------------------------------


class TestHeuristicReranker:
    def test_empty_candidates(self):
        reranker = HeuristicReranker()
        assert reranker.rerank("query", []) == []

    def test_top_k_truncation(self):
        reranker = HeuristicReranker(top_k=2)
        docs = [_make_doc(f"doc_{i}", 0.5, content=f"word_{i}") for i in range(5)]
        result = reranker.rerank("word_0 word_1", docs)
        assert len(result) <= 2

    def test_scorer_injection(self):
        scored = {}

        def custom_scorer(query, content):
            scored["called"] = True
            return 0.99

        reranker = HeuristicReranker(scorer=custom_scorer)
        docs = [_make_doc("doc_1", content="some text")]
        result = reranker.rerank("query", docs)
        assert scored.get("called") is True
        assert result[0].score == pytest.approx(0.99)

    def test_sorted_by_descending_rerank_score(self):
        reranker = HeuristicReranker(top_k=5)
        docs = [
            _make_doc("doc_1", content="governance validator enforces"),
            _make_doc("doc_2", content="unrelated text about weather"),
            _make_doc("doc_3", content="governance rules policy"),
        ]
        result = reranker.rerank("governance validator", docs)
        scores = [d.score for d in result]
        assert scores == sorted(scores, reverse=True)

    def test_metadata_includes_rerank_score(self):
        reranker = HeuristicReranker(top_k=3)
        docs = [_make_doc("doc_1", content="hello world")]
        result = reranker.rerank("hello", docs)
        assert "rerank_score" in result[0].metadata

    def test_deterministic(self):
        reranker = HeuristicReranker()
        docs = [_make_doc(f"doc_{i}", content=f"text about topic_{i}") for i in range(4)]
        r1 = [d.doc_id for d in reranker.rerank("topic_2", docs)]
        r2 = [d.doc_id for d in reranker.rerank("topic_2", docs)]
        assert r1 == r2


# ---------------------------------------------------------------------------
# PassthroughReranker
# ---------------------------------------------------------------------------


class TestPassthroughReranker:
    def test_empty(self):
        assert PassthroughReranker().rerank("q", []) == []

    def test_truncates_to_top_k(self):
        reranker = PassthroughReranker(top_k=3)
        docs = [_make_doc(f"doc_{i}") for i in range(10)]
        result = reranker.rerank("q", docs)
        assert len(result) == 3

    def test_preserves_order(self):
        reranker = PassthroughReranker(top_k=5)
        ids = [f"doc_{i}" for i in range(5)]
        docs = [_make_doc(doc_id) for doc_id in ids]
        result = reranker.rerank("q", docs)
        assert [d.doc_id for d in result] == ids


# ---------------------------------------------------------------------------
# RetrievalProfileConfig
# ---------------------------------------------------------------------------


class TestRetrievalProfileConfig:
    def test_to_dict_roundtrip(self):
        cfg = RetrievalProfileConfig(mode="hybrid_reranked", lexical_k=50, vector_k=50, rerank_k=10)
        d = cfg.to_dict()
        restored = RetrievalProfileConfig.from_dict(d)
        assert restored.mode == "hybrid_reranked"
        assert restored.rerank_k == 10

    def test_defaults_from_dict(self):
        cfg = RetrievalProfileConfig.from_dict({"mode": "hybrid"})
        assert cfg.lexical_k == 50
        assert cfg.vector_k == 50
        assert cfg.rerank_k == 10


# ---------------------------------------------------------------------------
# make_profile
# ---------------------------------------------------------------------------


class TestMakeProfile:
    def test_valid_modes(self):
        for mode in [PROFILE_VECTOR_ONLY, PROFILE_HYBRID, PROFILE_HYBRID_RERANKED]:
            cfg = make_profile(mode)
            assert cfg.mode == mode

    def test_invalid_mode_raises(self):
        with pytest.raises(ValueError):
            make_profile("unknown_mode")

    def test_custom_k_values(self):
        cfg = make_profile(PROFILE_HYBRID, lexical_k=20, vector_k=30, rerank_k=5)
        assert cfg.lexical_k == 20
        assert cfg.vector_k == 30
        assert cfg.rerank_k == 5


# ---------------------------------------------------------------------------
# RetrievalPipeline
# ---------------------------------------------------------------------------


class TestRetrievalPipeline:
    def _make_lexical_docs(self, n=5):
        return [_make_doc(f"lex_{i}", 1.0 - i * 0.1, content=f"lexical content {i}") for i in range(n)]

    def _make_vector_docs(self, n=5):
        return [_make_doc(f"vec_{i}", 1.0 - i * 0.1, content=f"vector content {i}") for i in range(n)]

    def test_vector_only_uses_vector_retriever(self):
        vector_docs = self._make_vector_docs(3)
        pipeline = RetrievalPipeline(
            config=make_profile(PROFILE_VECTOR_ONLY),
            vector_retriever=StubVectorRetriever(vector_docs),
        )
        result = pipeline.retrieve("query")
        ids = {d.doc_id for d in result}
        assert ids == {"vec_0", "vec_1", "vec_2"}

    def test_vector_only_no_retriever_returns_empty(self):
        pipeline = RetrievalPipeline(
            config=make_profile(PROFILE_VECTOR_ONLY),
            vector_retriever=None,
        )
        assert pipeline.retrieve("query") == []

    def test_hybrid_merges_both(self):
        lex_docs = self._make_lexical_docs(3)
        vec_docs = self._make_vector_docs(3)
        pipeline = RetrievalPipeline(
            config=make_profile(PROFILE_HYBRID),
            lexical_retriever=StubLexicalRetriever(lex_docs),
            vector_retriever=StubVectorRetriever(vec_docs),
        )
        result = pipeline.retrieve("query")
        ids = {d.doc_id for d in result}
        assert any(i.startswith("lex_") for i in ids)
        assert any(i.startswith("vec_") for i in ids)

    def test_hybrid_reranked_applies_reranker(self):
        lex_docs = [_make_doc("lex_0", content="governance policy enforcement")]
        vec_docs = [_make_doc("vec_0", content="unrelated weather report")]
        pipeline = RetrievalPipeline(
            config=make_profile(PROFILE_HYBRID_RERANKED, rerank_k=1),
            lexical_retriever=StubLexicalRetriever(lex_docs),
            vector_retriever=StubVectorRetriever(vec_docs),
        )
        result = pipeline.retrieve("governance policy")
        assert len(result) <= 1

    def test_unknown_mode_raises(self):
        pipeline = RetrievalPipeline(
            config=RetrievalProfileConfig(mode="invalid"),
        )
        with pytest.raises(ValueError):
            pipeline.retrieve("query")

    def test_to_retrieval_fn_returns_doc_ids(self):
        vector_docs = self._make_vector_docs(3)
        pipeline = RetrievalPipeline(
            config=make_profile(PROFILE_VECTOR_ONLY),
            vector_retriever=StubVectorRetriever(vector_docs),
        )
        fn = pipeline.to_retrieval_fn()
        result = fn("query")
        assert isinstance(result, list)
        assert all(isinstance(r, str) for r in result)

    def test_hybrid_only_lexical_no_vector(self):
        lex_docs = self._make_lexical_docs(3)
        pipeline = RetrievalPipeline(
            config=make_profile(PROFILE_HYBRID),
            lexical_retriever=StubLexicalRetriever(lex_docs),
            vector_retriever=None,
        )
        result = pipeline.retrieve("query")
        assert len(result) == 3
