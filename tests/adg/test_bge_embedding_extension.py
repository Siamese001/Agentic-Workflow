"""Creative and comprehensive tests for the BGE embedding extension addendum.

Covers:
  - ReplayFailureRecord type (addendum §2.4)
  - PromptOutcomeEmbeddingRecord type (addendum §2.5)
  - RetrievalCaseRecord type (addendum §2.6)
  - ReplayFailureEmbedder
  - PromptOutcomeEmbedder
  - RetrievalCaseEmbedder
  - SemanticIndexRegistry (8-index unified facade)

Test philosophy:
  1. Hash determinism — same inputs always produce the same hash
  2. Influence class invariant — always C0_INFORMATIONAL
  3. Immutability — frozen dataclasses block attribute mutation
  4. Embedding text invariants — IDs excluded, canonical ## separator
  5. Buffer eviction mechanics — LRU, meta cleanup
  6. Analytical methods — stats, weak cases, quality signals
  7. Registry facade — all 8 indexes, buffer snapshot, export
  8. Thread safety — concurrent ingest on all new embedders
  9. Integration — ingest → analyze → evict → verify
"""

from __future__ import annotations

import threading

import pytest

# ============================================================
# Constants
# ============================================================

_TS = 1_700_200_000
_RK = "rk-" + "a" * 60
_DD = "dd-" + "b" * 60
_PH = "ph-" + "c" * 60
_TID = "tr-001"


# ============================================================
# Builder helpers
# ============================================================

def _rfr(
    failure_id: str = "fail-001",
    summary: str = "L3 hash mismatch on replay",
    nd_type: str = "HASH_MISMATCH",
    mismatch: str = "determinism digest differed between runs",
    subsystems: tuple = ("L3_orchestration", "L0_routing"),
    remediation: str = "re-seed determinism context",
    replay_key: str = _RK,
    dd: str = _DD,
    trace_id: str = _TID,
    ts: int = _TS,
):
    from system_learning.types.semantic_memory_types import ReplayFailureRecord
    return ReplayFailureRecord(
        failure_id=failure_id,
        failure_summary=summary,
        nondeterminism_type=nd_type,
        mismatch_explanation=mismatch,
        affected_subsystems=subsystems,
        attempted_remediation=remediation,
        replay_key=replay_key,
        determinism_digest=dd,
        trace_id=trace_id,
        timestamp_utc=ts,
    )


def _poem(
    record_id: str = "poem-001",
    s0: str = "system prompt: govern routing",
    d0: str = "domain knowledge: enterprise SaaS",
    i0: str = "instruction: classify intent",
    c0: str = "context: retrieved 5 chunks",
    u0: str = "user: find my order status",
    task: str = "classify customer intent",
    answer: str = "ORDER_STATUS with confidence 0.92",
    safety: str = "ALLOWED",
    grounding: str = "3 of 5 chunks matched",
    prompt_hash: str = "prh-" + "d" * 59,
    template_id: str = "tmpl-v3",
    route: str = "L2_STANDARD",
    model: str = "gpt-4o-mini",
    policy_hash: str = _PH,
    trace_id: str = _TID,
    ts: int = _TS,
):
    from system_learning.types.semantic_memory_types import PromptOutcomeEmbeddingRecord
    return PromptOutcomeEmbeddingRecord(
        record_id=record_id,
        slot_s0_summary=s0,
        slot_d0_summary=d0,
        slot_i0_summary=i0,
        slot_c0_summary=c0,
        slot_u0_summary=u0,
        task_description=task,
        answer_summary=answer,
        safety_outcome=safety,
        retrieval_grounding_summary=grounding,
        prompt_hash=prompt_hash,
        template_id=template_id,
        route=route,
        model=model,
        policy_hash=policy_hash,
        trace_id=trace_id,
        timestamp_utc=ts,
    )


def _rcr(
    case_id: str = "rc-001",
    query: str = "what is the refund policy?",
    chunks: tuple = ("refund policy text", "return window details"),
    support_reasoning: str = "both chunks directly answer the query",
    quality: str = "high quality, complete answer",
    query_id: str = "qid-001",
    chunk_ids: tuple = ("cid-001", "cid-002"),
    support_score: float = 0.85,
    completeness_score: float = 0.90,
    escalation_flag: bool = False,
    healer_invoked: bool = False,
    replay_pass: bool = True,
    trace_id: str = _TID,
    ts: int = _TS,
):
    from system_learning.types.semantic_memory_types import RetrievalCaseRecord
    return RetrievalCaseRecord(
        case_id=case_id,
        query_summary=query,
        chunk_summaries=chunks,
        support_reasoning=support_reasoning,
        answer_quality_summary=quality,
        query_id=query_id,
        chunk_ids=chunk_ids,
        support_score=support_score,
        completeness_score=completeness_score,
        escalation_flag=escalation_flag,
        healer_invoked=healer_invoked,
        replay_pass=replay_pass,
        trace_id=trace_id,
        timestamp_utc=ts,
    )


def _registry(**kwargs):
    from system_learning.engines.semantic_index_registry import SemanticIndexRegistry
    return SemanticIndexRegistry(**kwargs)


# ============================================================
# 1. ReplayFailureRecord — type invariants
# ============================================================

class TestReplayFailureRecord:

    def test_hash_computed_on_construction(self):
        r = _rfr()
        assert len(r.failure_hash) == 64
        assert r.failure_hash.isalnum()

    def test_hash_deterministic(self):
        assert _rfr().failure_hash == _rfr().failure_hash

    def test_different_nd_type_gives_different_hash(self):
        r1 = _rfr(nd_type="HASH_MISMATCH")
        r2 = _rfr(nd_type="ORDERING_INSTABILITY")
        assert r1.failure_hash != r2.failure_hash

    def test_influence_class_c0(self):
        assert _rfr().influence_class == "C0_INFORMATIONAL"

    def test_frozen_immutable(self):
        r = _rfr()
        with pytest.raises((AttributeError, TypeError)):
            r.nondeterminism_type = "MUTATED"  # type: ignore[misc]

    def test_empty_failure_id_raises(self):
        from system_learning.types.semantic_memory_types import ReplayFailureRecord
        with pytest.raises(ValueError, match="failure_id"):
            ReplayFailureRecord(
                failure_id="", failure_summary="x",
                nondeterminism_type="T", mismatch_explanation="m",
                affected_subsystems=(), attempted_remediation="r",
                replay_key=_RK, determinism_digest=_DD,
                trace_id="tr", timestamp_utc=_TS,
            )

    def test_empty_nondeterminism_type_raises(self):
        from system_learning.types.semantic_memory_types import ReplayFailureRecord
        with pytest.raises(ValueError, match="nondeterminism_type"):
            ReplayFailureRecord(
                failure_id="f", failure_summary="x",
                nondeterminism_type="", mismatch_explanation="m",
                affected_subsystems=(), attempted_remediation="r",
                replay_key=_RK, determinism_digest=_DD,
                trace_id="tr", timestamp_utc=_TS,
            )

    def test_empty_replay_key_raises(self):
        from system_learning.types.semantic_memory_types import ReplayFailureRecord
        with pytest.raises(ValueError, match="replay_key"):
            ReplayFailureRecord(
                failure_id="f", failure_summary="x",
                nondeterminism_type="T", mismatch_explanation="m",
                affected_subsystems=(), attempted_remediation="r",
                replay_key="", determinism_digest=_DD,
                trace_id="tr", timestamp_utc=_TS,
            )

    def test_embedding_text_excludes_ids(self):
        r = _rfr(replay_key=_RK, dd=_DD, trace_id="tr-secret")
        text = r.to_embedding_text()
        assert _RK not in text
        assert _DD not in text
        assert "tr-secret" not in text

    def test_embedding_text_contains_all_semantic_fields(self):
        r = _rfr(
            summary="L3 hash mismatch",
            nd_type="HASH_MISMATCH",
            mismatch="digest diff",
            subsystems=("L3", "L0"),
            remediation="re-seed ctx",
        )
        text = r.to_embedding_text()
        assert "L3 hash mismatch" in text
        assert "HASH_MISMATCH" in text
        assert "digest diff" in text
        assert "L0" in text
        assert "re-seed ctx" in text

    def test_embedding_text_has_5_segments(self):
        parts = _rfr().to_embedding_text().split(" ## ")
        assert len(parts) == 5

    def test_affected_subsystems_sorted_in_embedding(self):
        r = _rfr(subsystems=("ZZZ", "AAA", "MMM"))
        text = r.to_embedding_text()
        assert text.index("AAA") < text.index("MMM") < text.index("ZZZ")


# ============================================================
# 2. PromptOutcomeEmbeddingRecord — type invariants
# ============================================================

class TestPromptOutcomeEmbeddingRecord:

    def test_hash_computed(self):
        r = _poem()
        assert len(r.record_hash) == 64

    def test_hash_deterministic(self):
        assert _poem().record_hash == _poem().record_hash

    def test_different_task_gives_different_hash(self):
        r1 = _poem(task="classify intent")
        r2 = _poem(task="summarize document")
        assert r1.record_hash != r2.record_hash

    def test_influence_class_c0(self):
        assert _poem().influence_class == "C0_INFORMATIONAL"

    def test_frozen_immutable(self):
        r = _poem()
        with pytest.raises((AttributeError, TypeError)):
            r.safety_outcome = "BLOCKED"  # type: ignore[misc]

    def test_empty_record_id_raises(self):
        from system_learning.types.semantic_memory_types import PromptOutcomeEmbeddingRecord
        with pytest.raises(ValueError, match="record_id"):
            PromptOutcomeEmbeddingRecord(
                record_id="", slot_s0_summary="s", slot_d0_summary="d",
                slot_i0_summary="i", slot_c0_summary="c", slot_u0_summary="u",
                task_description="t", answer_summary="a",
                safety_outcome="ALLOWED", retrieval_grounding_summary="g",
                prompt_hash="ph", template_id="ti", route="r", model="m",
                policy_hash="plh", trace_id="tr", timestamp_utc=_TS,
            )

    def test_invalid_safety_outcome_raises(self):
        from system_learning.types.semantic_memory_types import PromptOutcomeEmbeddingRecord
        with pytest.raises(ValueError, match="safety_outcome"):
            PromptOutcomeEmbeddingRecord(
                record_id="r", slot_s0_summary="s", slot_d0_summary="d",
                slot_i0_summary="i", slot_c0_summary="c", slot_u0_summary="u",
                task_description="t", answer_summary="a",
                safety_outcome="UNKNOWN_BAD",
                retrieval_grounding_summary="g",
                prompt_hash="ph", template_id="ti", route="r", model="m",
                policy_hash="plh", trace_id="tr", timestamp_utc=_TS,
            )

    def test_all_five_safety_outcomes_accepted(self):
        for outcome in ("ALLOWED", "BLOCKED", "ESCALATED", "HEALED", "UNKNOWN"):
            r = _poem(safety=outcome, record_id=f"r-{outcome}")
            assert r.safety_outcome == outcome

    def test_embedding_text_excludes_ids(self):
        r = _poem(prompt_hash="secret_ph", template_id="secret_tmpl",
                  trace_id="secret_tr", policy_hash="secret_pol")
        text = r.to_embedding_text()
        assert "secret_ph" not in text
        assert "secret_tmpl" not in text
        assert "secret_tr" not in text
        assert "secret_pol" not in text

    def test_embedding_text_contains_all_slot_summaries(self):
        r = _poem(s0="SYS", d0="DOM", i0="INS", c0="CTX", u0="USR",
                  task="TASK", answer="ANS", grounding="GRND")
        text = r.to_embedding_text()
        for token in ("SYS", "DOM", "INS", "CTX", "USR", "TASK", "ANS", "GRND"):
            assert token in text

    def test_embedding_text_has_9_segments(self):
        parts = _poem().to_embedding_text().split(" ## ")
        assert len(parts) == 9

    def test_embedding_text_starts_with_s0(self):
        r = _poem(s0="system_anchor")
        assert r.to_embedding_text().startswith("s0:system_anchor")


# ============================================================
# 3. RetrievalCaseRecord — type invariants
# ============================================================

class TestRetrievalCaseRecord:

    def test_hash_computed(self):
        r = _rcr()
        assert len(r.case_hash) == 64

    def test_hash_deterministic(self):
        assert _rcr().case_hash == _rcr().case_hash

    def test_different_support_scores_give_different_hashes(self):
        r1 = _rcr(support_score=0.8)
        r2 = _rcr(support_score=0.2)
        assert r1.case_hash != r2.case_hash

    def test_influence_class_c0(self):
        assert _rcr().influence_class == "C0_INFORMATIONAL"

    def test_frozen_immutable(self):
        r = _rcr()
        with pytest.raises((AttributeError, TypeError)):
            r.support_score = 0.0  # type: ignore[misc]

    def test_empty_case_id_raises(self):
        from system_learning.types.semantic_memory_types import RetrievalCaseRecord
        with pytest.raises(ValueError, match="case_id"):
            RetrievalCaseRecord(
                case_id="", query_summary="q", chunk_summaries=(),
                support_reasoning="s", answer_quality_summary="a",
                query_id="qi", chunk_ids=(),
                support_score=0.5, completeness_score=0.5,
                escalation_flag=False, healer_invoked=False,
                replay_pass=True, trace_id="tr", timestamp_utc=_TS,
            )

    def test_support_score_out_of_range_raises(self):
        from system_learning.types.semantic_memory_types import RetrievalCaseRecord
        with pytest.raises(ValueError, match="support_score"):
            RetrievalCaseRecord(
                case_id="c", query_summary="q", chunk_summaries=(),
                support_reasoning="s", answer_quality_summary="a",
                query_id="qi", chunk_ids=(),
                support_score=1.5, completeness_score=0.5,
                escalation_flag=False, healer_invoked=False,
                replay_pass=True, trace_id="tr", timestamp_utc=_TS,
            )

    def test_completeness_score_out_of_range_raises(self):
        from system_learning.types.semantic_memory_types import RetrievalCaseRecord
        with pytest.raises(ValueError, match="completeness_score"):
            RetrievalCaseRecord(
                case_id="c", query_summary="q", chunk_summaries=(),
                support_reasoning="s", answer_quality_summary="a",
                query_id="qi", chunk_ids=(),
                support_score=0.5, completeness_score=-0.1,
                escalation_flag=False, healer_invoked=False,
                replay_pass=True, trace_id="tr", timestamp_utc=_TS,
            )

    def test_scores_at_boundary_accepted(self):
        for ss, cs in ((0.0, 0.0), (1.0, 1.0), (0.5, 0.5)):
            r = _rcr(support_score=ss, completeness_score=cs, case_id=f"c{ss}{cs}")
            assert r.support_score == ss

    def test_embedding_text_excludes_ids(self):
        r = _rcr(query_id="secret_qid", chunk_ids=("secret_cid",))
        text = r.to_embedding_text()
        assert "secret_qid" not in text
        assert "secret_cid" not in text

    def test_embedding_text_has_4_segments(self):
        parts = _rcr().to_embedding_text().split(" ## ")
        assert len(parts) == 4

    def test_chunk_summaries_sorted_in_embedding(self):
        r = _rcr(chunks=("ZZZ chunk", "AAA chunk", "MMM chunk"))
        text = r.to_embedding_text()
        assert text.index("AAA") < text.index("MMM") < text.index("ZZZ")

    def test_scores_rounded_in_canonical_dict(self):
        r = _rcr(support_score=0.123456789, completeness_score=0.987654321)
        d = r._canonical_dict()
        assert d["support_score"] == round(0.123456789, 6)
        assert d["completeness_score"] == round(0.987654321, 6)


# ============================================================
# 4. ReplayFailureEmbedder
# ============================================================

class TestReplayFailureEmbedder:

    def _e(self, max_buffer=100):
        from system_learning.engines.replay_failure_embedder import ReplayFailureEmbedder
        return ReplayFailureEmbedder(max_buffer=max_buffer)

    def test_ingest_returns_corpus_record(self):
        from system_learning.engines.embedding_corpus_extraction import CorpusRecord
        e = self._e()
        r = e.ingest(_rfr())
        assert isinstance(r, CorpusRecord)

    def test_namespace_is_replay_failures(self):
        e = self._e()
        r = e.ingest(_rfr())
        assert r.namespace == "replay_failures"

    def test_buffer_increments(self):
        e = self._e()
        e.ingest(_rfr())
        assert e.buffer_size() == 1

    def test_buffer_evicts_oldest_at_capacity(self):
        e = self._e(max_buffer=2)
        e.ingest(_rfr(failure_id="f0", trace_id="t0", summary="s0"))
        e.ingest(_rfr(failure_id="f1", trace_id="t1", summary="s1"))
        e.ingest(_rfr(failure_id="f2", trace_id="t2", summary="s2"))
        assert e.buffer_size() == 2
        tids = {r.trace_id for r in e.export_corpus_records()}
        assert "t0" not in tids

    def test_nondeterminism_type_stats_correct(self):
        e = self._e()
        for _ in range(3):
            e.ingest(_rfr(nd_type="HASH_MISMATCH",
                          failure_id=f"f-hm-{_}", trace_id=f"t-hm-{_}",
                          summary=f"s-hm-{_}"))
        for _ in range(2):
            e.ingest(_rfr(nd_type="ORDERING_INSTABILITY",
                          failure_id=f"f-oi-{_}", trace_id=f"t-oi-{_}",
                          summary=f"s-oi-{_}"))
        stats = e.nondeterminism_type_stats()
        assert stats["HASH_MISMATCH"] == 3
        assert stats["ORDERING_INSTABILITY"] == 2

    def test_nondeterminism_stats_empty_buffer(self):
        e = self._e()
        assert e.nondeterminism_type_stats() == {}

    def test_nondeterminism_stats_sorted_alphabetically(self):
        e = self._e()
        for nd, fid, tid, sm in [
            ("ZZZ", "fz", "tz", "sz"),
            ("AAA", "fa", "ta", "sa"),
            ("MMM", "fm", "tm", "sm"),
        ]:
            e.ingest(_rfr(nd_type=nd, failure_id=fid, trace_id=tid, summary=sm))
        keys = list(e.nondeterminism_type_stats().keys())
        assert keys == sorted(keys)

    def test_evict_by_replay_key_removes_correct_records(self):
        e = self._e()
        rk2 = "rk2-" + "x" * 59
        for i in range(3):
            e.ingest(_rfr(failure_id=f"f-a{i}", trace_id=f"ta{i}",
                          summary=f"sa{i}", replay_key=_RK))
        for i in range(2):
            e.ingest(_rfr(failure_id=f"f-b{i}", trace_id=f"tb{i}",
                          summary=f"sb{i}", replay_key=rk2))
        n = e.evict_by_replay_key(_RK)
        assert n == 3
        assert e.buffer_size() == 2

    def test_evict_empty_replay_key_raises(self):
        e = self._e()
        with pytest.raises(ValueError, match="replay_key"):
            e.evict_by_replay_key("")

    def test_evict_idempotent(self):
        e = self._e()
        e.ingest(_rfr())
        n1 = e.evict_by_replay_key(_RK)
        n2 = e.evict_by_replay_key(_RK)
        assert n1 == 1
        assert n2 == 0

    def test_record_from_replay_event_convenience_constructor(self):
        from system_learning.engines.replay_failure_embedder import ReplayFailureEmbedder
        r = ReplayFailureEmbedder.record_from_replay_event(
            failure_id="fe-001",
            failure_summary="hash mismatch",
            nondeterminism_type="HASH_MISMATCH",
            mismatch_explanation="digest differed",
            affected_subsystems=["L3", "L0"],
            attempted_remediation="reseed",
            replay_key=_RK,
            determinism_digest=_DD,
            trace_id="tr-x",
            timestamp_utc=_TS,
        )
        assert r.nondeterminism_type == "HASH_MISMATCH"
        assert r.affected_subsystems == ("L0", "L3")  # sorted

    def test_record_from_replay_event_empty_failure_id_raises(self):
        from system_learning.engines.replay_failure_embedder import ReplayFailureEmbedder
        with pytest.raises(ValueError, match="failure_id"):
            ReplayFailureEmbedder.record_from_replay_event(
                failure_id="", failure_summary="x", nondeterminism_type="T",
                mismatch_explanation="m", affected_subsystems=[],
                attempted_remediation="r", replay_key=_RK,
                determinism_digest=_DD, trace_id="tr", timestamp_utc=_TS,
            )

    def test_export_sorted_by_content_hash(self):
        e = self._e()
        for i in range(5):
            e.ingest(_rfr(failure_id=f"f{i}", trace_id=f"tr{i}", summary=f"s{i}"))
        records = e.export_corpus_records()
        keys = [(r.content_hash, r.trace_id) for r in records]
        assert keys == sorted(keys)

    def test_concurrent_ingest_thread_safe(self):
        e = self._e(max_buffer=10_000)
        errors = []
        def worker(tid):
            try:
                for j in range(20):
                    e.ingest(_rfr(failure_id=f"f-{tid}-{j}",
                                  trace_id=f"t-{tid}-{j}",
                                  summary=f"s-{tid}-{j}"))
            except Exception as exc:
                errors.append(exc)
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for t in threads: t.start()
        for t in threads: t.join()
        assert errors == []
        assert e.buffer_size() == 100


# ============================================================
# 5. PromptOutcomeEmbedder
# ============================================================

class TestPromptOutcomeEmbedder:

    def _e(self, max_buffer=100):
        from system_learning.engines.prompt_outcome_embedder import PromptOutcomeEmbedder
        return PromptOutcomeEmbedder(max_buffer=max_buffer)

    def test_ingest_returns_corpus_record(self):
        from system_learning.engines.embedding_corpus_extraction import CorpusRecord
        e = self._e()
        assert isinstance(e.ingest(_poem()), CorpusRecord)

    def test_namespace_is_prompt_outcomes(self):
        e = self._e()
        r = e.ingest(_poem())
        assert r.namespace == "prompt_outcomes"

    def test_buffer_increments(self):
        e = self._e()
        e.ingest(_poem())
        assert e.buffer_size() == 1

    def test_safety_outcome_stats_all_keys_present(self):
        e = self._e()
        e.ingest(_poem(safety="ALLOWED", record_id="r1"))
        stats = e.safety_outcome_stats()
        for key in ("ALLOWED", "BLOCKED", "ESCALATED", "HEALED", "UNKNOWN"):
            assert key in stats

    def test_safety_outcome_stats_counts_correct(self):
        e = self._e()
        for i in range(4):
            e.ingest(_poem(safety="ALLOWED", record_id=f"a{i}", trace_id=f"ta{i}",
                           task=f"task-a{i}"))
        for i in range(2):
            e.ingest(_poem(safety="BLOCKED", record_id=f"b{i}", trace_id=f"tb{i}",
                           task=f"task-b{i}"))
        stats = e.safety_outcome_stats()
        assert stats["ALLOWED"] == 4
        assert stats["BLOCKED"] == 2
        assert stats["ESCALATED"] == 0

    def test_safety_outcome_stats_sum_equals_buffer(self):
        e = self._e()
        for i, s in enumerate(["ALLOWED", "BLOCKED", "ESCALATED", "HEALED", "UNKNOWN"]):
            e.ingest(_poem(safety=s, record_id=f"r{i}", trace_id=f"t{i}",
                           task=f"task{i}"))
        assert sum(e.safety_outcome_stats().values()) == e.buffer_size()

    def test_evict_by_template_id_removes_records(self):
        e = self._e()
        for i in range(5):
            e.ingest(_poem(record_id=f"r-v3-{i}", trace_id=f"t-v3-{i}",
                           task=f"task-v3-{i}", template_id="tmpl-v3"))
        for i in range(3):
            e.ingest(_poem(record_id=f"r-v4-{i}", trace_id=f"t-v4-{i}",
                           task=f"task-v4-{i}", template_id="tmpl-v4"))
        n = e.evict_by_template_id("tmpl-v3")
        assert n == 5
        assert e.buffer_size() == 3

    def test_evict_empty_template_id_raises(self):
        e = self._e()
        with pytest.raises(ValueError, match="template_id"):
            e.evict_by_template_id("")

    def test_evict_updates_safety_outcome_stats(self):
        e = self._e()
        e.ingest(_poem(safety="BLOCKED", record_id="b1", trace_id="tb1",
                       task="t-b", template_id="tmpl-old"))
        e.ingest(_poem(safety="ALLOWED", record_id="a1", trace_id="ta1",
                       task="t-a", template_id="tmpl-new"))
        e.evict_by_template_id("tmpl-old")
        stats = e.safety_outcome_stats()
        assert stats["BLOCKED"] == 0
        assert stats["ALLOWED"] == 1

    def test_record_from_execution_convenience_constructor(self):
        from system_learning.engines.prompt_outcome_embedder import PromptOutcomeEmbedder
        r = PromptOutcomeEmbedder.record_from_execution(
            record_id="exec-001",
            slot_s0_summary="sys", slot_d0_summary="dom",
            slot_i0_summary="ins", slot_c0_summary="ctx",
            slot_u0_summary="usr", task_description="t",
            answer_summary="a", safety_outcome="ALLOWED",
            retrieval_grounding_summary="g",
            prompt_hash="ph", template_id="ti",
            route="r", model="m", policy_hash="plh",
            trace_id="tr", timestamp_utc=_TS,
        )
        assert r.record_id == "exec-001"
        assert r.safety_outcome == "ALLOWED"

    def test_record_from_execution_invalid_safety_raises(self):
        from system_learning.engines.prompt_outcome_embedder import PromptOutcomeEmbedder
        with pytest.raises(ValueError, match="safety_outcome"):
            PromptOutcomeEmbedder.record_from_execution(
                record_id="x", slot_s0_summary="s", slot_d0_summary="d",
                slot_i0_summary="i", slot_c0_summary="c", slot_u0_summary="u",
                task_description="t", answer_summary="a",
                safety_outcome="INVALID",
                retrieval_grounding_summary="g",
                prompt_hash="ph", template_id="ti",
                route="r", model="m", policy_hash="plh",
                trace_id="tr", timestamp_utc=_TS,
            )

    def test_buffer_evicts_oldest_at_capacity(self):
        e = self._e(max_buffer=2)
        e.ingest(_poem(record_id="r0", trace_id="t0", task="task0"))
        e.ingest(_poem(record_id="r1", trace_id="t1", task="task1"))
        e.ingest(_poem(record_id="r2", trace_id="t2", task="task2"))
        assert e.buffer_size() == 2
        tids = {r.trace_id for r in e.export_corpus_records()}
        assert "t0" not in tids

    def test_concurrent_ingest_thread_safe(self):
        e = self._e(max_buffer=10_000)
        errors = []
        def worker(tid):
            try:
                for j in range(25):
                    e.ingest(_poem(record_id=f"r-{tid}-{j}",
                                   trace_id=f"t-{tid}-{j}",
                                   task=f"task-{tid}-{j}"))
            except Exception as exc:
                errors.append(exc)
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
        for t in threads: t.start()
        for t in threads: t.join()
        assert errors == []
        assert e.buffer_size() == 100


# ============================================================
# 6. RetrievalCaseEmbedder
# ============================================================

class TestRetrievalCaseEmbedder:

    def _e(self, max_buffer=100):
        from system_learning.engines.retrieval_case_embedder import RetrievalCaseEmbedder
        return RetrievalCaseEmbedder(max_buffer=max_buffer)

    def test_ingest_returns_corpus_record(self):
        from system_learning.engines.embedding_corpus_extraction import CorpusRecord
        e = self._e()
        assert isinstance(e.ingest(_rcr()), CorpusRecord)

    def test_namespace_is_retrieval_cases(self):
        e = self._e()
        assert e.ingest(_rcr()).namespace == "retrieval_cases"

    def test_buffer_increments(self):
        e = self._e()
        e.ingest(_rcr())
        assert e.buffer_size() == 1

    def test_quality_signal_summary_empty_buffer(self):
        e = self._e()
        summary = e.quality_signal_summary()
        assert summary["count"] == 0
        assert summary["avg_support_score"] == 0.0

    def test_quality_signal_summary_correct_averages(self):
        e = self._e()
        e.ingest(_rcr(case_id="c0", support_score=0.8, completeness_score=0.9,
                      query="q0", chunk_ids=("c0",)))
        e.ingest(_rcr(case_id="c1", support_score=0.4, completeness_score=0.6,
                      query="q1", chunk_ids=("c1",)))
        s = e.quality_signal_summary()
        assert s["count"] == 2
        assert abs(s["avg_support_score"] - 0.6) < 1e-5
        assert abs(s["avg_completeness_score"] - 0.75) < 1e-5

    def test_quality_signal_escalation_rate(self):
        e = self._e()
        e.ingest(_rcr(case_id="c0", escalation_flag=True, query="q0",
                      chunk_ids=("x0",)))
        e.ingest(_rcr(case_id="c1", escalation_flag=False, query="q1",
                      chunk_ids=("x1",)))
        s = e.quality_signal_summary()
        assert abs(s["escalation_rate"] - 0.5) < 1e-5

    def test_quality_signal_replay_pass_rate(self):
        e = self._e()
        for i in range(3):
            e.ingest(_rcr(case_id=f"c{i}", replay_pass=True,
                          query=f"q{i}", chunk_ids=(f"x{i}",)))
        e.ingest(_rcr(case_id="c-fail", replay_pass=False,
                      query="q-f", chunk_ids=("x-f",)))
        s = e.quality_signal_summary()
        assert abs(s["replay_pass_rate"] - 0.75) < 1e-5

    def test_retrieve_weak_cases_below_support_threshold(self):
        e = self._e()
        e.ingest(_rcr(case_id="weak", support_score=0.2, completeness_score=0.9,
                      query="qw", chunk_ids=("cw",)))
        e.ingest(_rcr(case_id="strong", support_score=0.9, completeness_score=0.9,
                      query="qs", chunk_ids=("cs",)))
        weak = e.retrieve_weak_cases(support_threshold=0.5)
        assert len(weak) == 1
        assert weak[0]["case_id"] == "weak"

    def test_retrieve_weak_cases_below_completeness_threshold(self):
        e = self._e()
        e.ingest(_rcr(case_id="w-comp", support_score=0.9, completeness_score=0.3,
                      query="qwc", chunk_ids=("cwc",)))
        e.ingest(_rcr(case_id="s-comp", support_score=0.9, completeness_score=0.9,
                      query="qsc", chunk_ids=("csc",)))
        weak = e.retrieve_weak_cases(completeness_threshold=0.5)
        assert len(weak) == 1
        assert weak[0]["case_id"] == "w-comp"

    def test_retrieve_weak_cases_limit_respected(self):
        e = self._e(max_buffer=200)
        for i in range(20):
            e.ingest(_rcr(case_id=f"w{i}", support_score=0.1,
                          query=f"q{i}", chunk_ids=(f"x{i}",)))
        weak = e.retrieve_weak_cases(support_threshold=0.5, limit=5)
        assert len(weak) == 5

    def test_retrieve_weak_cases_limit_capped_at_100(self):
        e = self._e(max_buffer=200)
        for i in range(150):
            e.ingest(_rcr(case_id=f"w{i}", support_score=0.1,
                          query=f"q{i}", chunk_ids=(f"x{i}",)))
        weak = e.retrieve_weak_cases(support_threshold=0.5, limit=999)
        assert len(weak) <= 100

    def test_retrieve_weak_cases_invalid_threshold_raises(self):
        e = self._e()
        with pytest.raises(ValueError, match="support_threshold"):
            e.retrieve_weak_cases(support_threshold=1.5)
        with pytest.raises(ValueError, match="completeness_threshold"):
            e.retrieve_weak_cases(completeness_threshold=-0.1)

    def test_retrieve_weak_cases_sorted_by_support_score(self):
        e = self._e()
        for i, ss in enumerate([0.4, 0.1, 0.3]):
            e.ingest(_rcr(case_id=f"w{i}", support_score=ss, completeness_score=0.9,
                          query=f"q{i}", chunk_ids=(f"x{i}",)))
        weak = e.retrieve_weak_cases(support_threshold=0.5)
        scores = [m["support_score"] for m in weak]
        assert scores == sorted(scores)

    def test_retrieve_weak_cases_returns_copies_not_refs(self):
        e = self._e()
        e.ingest(_rcr(case_id="c0", support_score=0.2,
                      query="q0", chunk_ids=("x0",)))
        weak = e.retrieve_weak_cases(support_threshold=0.5)
        weak[0]["case_id"] = "MUTATED"
        # Internal state must be unaffected
        weak2 = e.retrieve_weak_cases(support_threshold=0.5)
        assert weak2[0]["case_id"] == "c0"

    def test_record_from_rag_evaluation_convenience(self):
        from system_learning.engines.retrieval_case_embedder import RetrievalCaseEmbedder
        r = RetrievalCaseEmbedder.record_from_rag_evaluation(
            case_id="eval-001",
            query_summary="what is X?",
            chunk_summaries=["B chunk", "A chunk"],
            support_reasoning="both match",
            answer_quality_summary="complete",
            query_id="qid-x",
            chunk_ids=["cid-b", "cid-a"],
            support_score=0.85,
            completeness_score=0.9,
            escalation_flag=False,
            healer_invoked=False,
            replay_pass=True,
            trace_id="tr-e",
            timestamp_utc=_TS,
        )
        assert r.case_id == "eval-001"
        assert r.chunk_summaries == ("A chunk", "B chunk")  # sorted
        assert r.chunk_ids == ("cid-a", "cid-b")  # sorted

    def test_record_from_rag_evaluation_invalid_score_raises(self):
        from system_learning.engines.retrieval_case_embedder import RetrievalCaseEmbedder
        with pytest.raises(ValueError, match="support_score"):
            RetrievalCaseEmbedder.record_from_rag_evaluation(
                case_id="e", query_summary="q", chunk_summaries=[],
                support_reasoning="s", answer_quality_summary="a",
                query_id="qi", chunk_ids=[],
                support_score=2.0, completeness_score=0.5,
                escalation_flag=False, healer_invoked=False,
                replay_pass=True, trace_id="tr", timestamp_utc=_TS,
            )

    def test_buffer_evicts_oldest_at_capacity(self):
        e = self._e(max_buffer=2)
        e.ingest(_rcr(case_id="c0", query="q0", chunk_ids=("x0",)))
        e.ingest(_rcr(case_id="c1", query="q1", chunk_ids=("x1",)))
        e.ingest(_rcr(case_id="c2", query="q2", chunk_ids=("x2",)))
        assert e.buffer_size() == 2

    def test_concurrent_ingest_thread_safe(self):
        e = self._e(max_buffer=10_000)
        errors = []
        def worker(tid):
            try:
                for j in range(30):
                    e.ingest(_rcr(case_id=f"c-{tid}-{j}",
                                  trace_id=f"t-{tid}-{j}",
                                  query=f"q-{tid}-{j}",
                                  chunk_ids=(f"x-{tid}-{j}",)))
            except Exception as exc:
                errors.append(exc)
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
        for t in threads: t.start()
        for t in threads: t.join()
        assert errors == []
        assert e.buffer_size() == 120


# ============================================================
# 7. SemanticIndexRegistry
# ============================================================

class TestSemanticIndexRegistry:

    def test_construction_with_defaults(self):
        r = _registry()
        snap = r.buffer_snapshot()
        assert snap.total == 0

    def test_ingest_incident(self):
        from system_learning.types.semantic_memory_types import IncidentBundle
        r = _registry()
        bundle = IncidentBundle(
            trace_id="tr-i", trace_summary="L3 routing failure",
            violations=("V1", "V2"), route_path="L0->L2->L3",
            tool_capability="route", state_diff_summary="threshold changed",
            healer_id="h1", outcome="failure", policy_hash=_PH,
            timestamp_utc=_TS,
        )
        result = r.ingest_incident(bundle)
        from system_learning.engines.semantic_index_registry import INDEX_INCIDENT
        assert result.index_name == INDEX_INCIDENT
        assert r.buffer_snapshot().incident_index == 1

    def test_ingest_graph_neighborhood(self):
        from system_learning.types.semantic_memory_types import GraphNeighborhood
        from system_learning.engines.semantic_index_registry import INDEX_GRAPH
        r = _registry()
        n = GraphNeighborhood(
            node_id="n1", node_type="Engine", layer="L3",
            inbound_relations=("GOVERNS",), outbound_relations=("ROUTES_TO",),
            governance_edges=("POLICY_EDGE",), mutation_edges=("MUT_1",),
            ownership_territory="apps_rg", risk_label="HIGH",
        )
        res = r.ingest_graph_neighborhood(n)
        assert res.index_name == INDEX_GRAPH
        assert r.buffer_snapshot().graph_index == 1

    def test_ingest_mutation(self):
        from system_learning.types.semantic_memory_types import MutationDiffRecord
        from system_learning.engines.semantic_index_registry import INDEX_MUTATION
        r = _registry()
        m = MutationDiffRecord(
            mutation_id="m1", target_resource="config/thresholds.json",
            operations=("op:add:/threshold",),
            state_diff_summary="threshold 0.8->0.9",
            rollback_context="revert to 0.8",
            commit_outcome="committed",
            trace_id="tr-m", policy_hash=_PH, timestamp_utc=_TS,
        )
        res = r.ingest_mutation(m)
        assert res.index_name == INDEX_MUTATION
        assert r.buffer_snapshot().mutation_index == 1

    def test_ingest_prompt_outcome(self):
        from system_learning.engines.semantic_index_registry import INDEX_PROMPT
        r = _registry()
        res = r.ingest_prompt_outcome(_poem())
        assert res.index_name == INDEX_PROMPT
        assert r.buffer_snapshot().prompt_index == 1

    def test_ingest_retrieval_case(self):
        from system_learning.engines.semantic_index_registry import INDEX_RETRIEVAL
        r = _registry()
        res = r.ingest_retrieval_case(_rcr())
        assert res.index_name == INDEX_RETRIEVAL
        assert r.buffer_snapshot().retrieval_index == 1

    def test_ingest_replay_failure(self):
        from system_learning.engines.semantic_index_registry import INDEX_REPLAY
        r = _registry()
        res = r.ingest_replay_failure(_rfr())
        assert res.index_name == INDEX_REPLAY
        assert r.buffer_snapshot().replay_index == 1

    def test_ingest_preference(self):
        from system_learning.types.semantic_memory_types import PathDPreferencePair
        from system_learning.engines.semantic_index_registry import INDEX_PREFERENCE
        r = _registry()
        p = PathDPreferencePair(
            decision_id="d1", original_plan="do X",
            human_patch="do Y instead", decision="modified",
            reason="X was risky", resulting_outcome="success",
            agent="PlannerAgent", trace_id="tr-p", timestamp_utc=_TS,
        )
        res = r.ingest_preference(p)
        assert res.index_name == INDEX_PREFERENCE
        assert r.buffer_snapshot().preference_index == 1

    def test_ingest_guardrail_case(self):
        from system_learning.types.semantic_memory_types import PolicyGuardrailCase
        from system_learning.engines.semantic_index_registry import INDEX_GUARDRAIL
        r = _registry()
        c = PolicyGuardrailCase(
            case_id="gc-001", blocked_payload_summary="SQL inject",
            remediation_text="sanitize", policy_hash=_PH,
            policy_root="root_sql", verdict="true_positive",
            strictness_level="HIGH", trace_id="tr-gc", timestamp_utc=_TS,
        )
        res = r.ingest_guardrail_case(c)
        assert res.index_name == INDEX_GUARDRAIL
        assert r.buffer_snapshot().guardrail_index == 1

    def test_buffer_snapshot_total_tracks_all_indexes(self):
        r = _registry()
        r.ingest_prompt_outcome(_poem())
        r.ingest_replay_failure(_rfr())
        r.ingest_retrieval_case(_rcr())
        snap = r.buffer_snapshot()
        assert snap.total == 3

    def test_export_all_corpus_records_returns_all_index_keys(self):
        from system_learning.engines.semantic_index_registry import ALL_INDEXES
        r = _registry()
        r.ingest_prompt_outcome(_poem())
        dump = r.export_all_corpus_records()
        assert set(dump.keys()) == ALL_INDEXES

    def test_export_records_are_sorted(self):
        r = _registry()
        for i in range(5):
            r.ingest_prompt_outcome(_poem(record_id=f"r{i}", trace_id=f"t{i}",
                                          task=f"task{i}"))
        dump = r.export_all_corpus_records()
        records = dump["prompt_index"]
        keys = [(rec.content_hash, rec.trace_id) for rec in records]
        assert keys == sorted(keys)

    def test_retrieval_quality_summary_delegates_to_retrieval_embedder(self):
        r = _registry()
        r.ingest_retrieval_case(_rcr(support_score=0.6, completeness_score=0.7,
                                     case_id="c0", query="q0", chunk_ids=("x0",)))
        s = r.retrieval_quality_summary()
        assert s["count"] == 1
        assert abs(s["avg_support_score"] - 0.6) < 1e-4

    def test_prompt_safety_outcome_stats_delegates(self):
        r = _registry()
        r.ingest_prompt_outcome(_poem(safety="BLOCKED", record_id="b1",
                                      trace_id="tb1", task="task-b"))
        stats = r.prompt_safety_outcome_stats()
        assert stats["BLOCKED"] == 1
        assert stats["ALLOWED"] == 0

    def test_replay_nondeterminism_stats_delegates(self):
        r = _registry()
        r.ingest_replay_failure(_rfr(nd_type="TIMING_DEPENDENCY"))
        stats = r.replay_nondeterminism_stats()
        assert stats.get("TIMING_DEPENDENCY", 0) == 1

    def test_guardrail_verdict_stats_delegates(self):
        from system_learning.types.semantic_memory_types import PolicyGuardrailCase
        r = _registry()
        r.ingest_guardrail_case(PolicyGuardrailCase(
            case_id="gv1", blocked_payload_summary="p",
            remediation_text="r", policy_hash=_PH,
            policy_root="root", verdict="false_positive",
            strictness_level="LOW", trace_id="tr-gv1", timestamp_utc=_TS,
        ))
        stats = r.guardrail_verdict_stats()
        assert stats["false_positive"] == 1

    def test_custom_buffer_sizes_respected(self):
        r = _registry(incident_buffer=5, prompt_buffer=3)
        for i in range(6):
            from system_learning.types.semantic_memory_types import IncidentBundle
            b = IncidentBundle(
                trace_id=f"tr{i}", trace_summary=f"s{i}",
                violations=(f"V{i}",), route_path=f"L0->L{i}",
                tool_capability="route", state_diff_summary=f"diff{i}",
                healer_id=f"h{i}", outcome="failure", policy_hash=_PH,
                timestamp_utc=_TS + i,
            )
            r.ingest_incident(b)
        assert r.buffer_snapshot().incident_index == 5  # capped at 5

    def test_indexes_independent_no_cross_contamination(self):
        r = _registry()
        r.ingest_prompt_outcome(_poem())
        r.ingest_replay_failure(_rfr())
        snap = r.buffer_snapshot()
        assert snap.prompt_index == 1
        assert snap.replay_index == 1
        assert snap.incident_index == 0
        assert snap.retrieval_index == 0


# ============================================================
# 8. Integration — full addendum pipeline
# ============================================================

class TestAddendumIntegration:

    def test_replay_ingest_then_evict_nondeterminism_stats_consistent(self):
        from system_learning.engines.replay_failure_embedder import ReplayFailureEmbedder
        e = ReplayFailureEmbedder()
        rk2 = "rk2-" + "y" * 59
        for i in range(5):
            e.ingest(_rfr(nd_type="HASH_MISMATCH", failure_id=f"f-hm{i}",
                          trace_id=f"t-hm{i}", summary=f"s-hm{i}",
                          replay_key=_RK))
        for i in range(3):
            e.ingest(_rfr(nd_type="ORDERING_INSTABILITY", failure_id=f"f-oi{i}",
                          trace_id=f"t-oi{i}", summary=f"s-oi{i}",
                          replay_key=rk2))
        assert e.nondeterminism_type_stats()["HASH_MISMATCH"] == 5
        e.evict_by_replay_key(_RK)
        assert e.nondeterminism_type_stats().get("HASH_MISMATCH", 0) == 0
        assert e.nondeterminism_type_stats()["ORDERING_INSTABILITY"] == 3

    def test_prompt_ingest_evict_stats_consistent(self):
        from system_learning.engines.prompt_outcome_embedder import PromptOutcomeEmbedder
        e = PromptOutcomeEmbedder()
        for i in range(4):
            e.ingest(_poem(safety="BLOCKED", record_id=f"b{i}", trace_id=f"tb{i}",
                           task=f"t-b{i}", template_id="tmpl-old"))
        for i in range(2):
            e.ingest(_poem(safety="ALLOWED", record_id=f"a{i}", trace_id=f"ta{i}",
                           task=f"t-a{i}", template_id="tmpl-new"))
        assert e.safety_outcome_stats()["BLOCKED"] == 4
        e.evict_by_template_id("tmpl-old")
        assert e.safety_outcome_stats()["BLOCKED"] == 0
        assert e.safety_outcome_stats()["ALLOWED"] == 2

    def test_retrieval_weak_case_pipeline(self):
        from system_learning.engines.retrieval_case_embedder import RetrievalCaseEmbedder
        e = RetrievalCaseEmbedder()
        for i in range(5):
            e.ingest(_rcr(case_id=f"weak-{i}", support_score=0.2 + i * 0.05,
                          completeness_score=0.3, query=f"q-w{i}",
                          chunk_ids=(f"xw{i}",)))
        for i in range(5):
            e.ingest(_rcr(case_id=f"strong-{i}", support_score=0.9,
                          completeness_score=0.95, query=f"q-s{i}",
                          chunk_ids=(f"xs{i}",)))
        weak = e.retrieve_weak_cases(support_threshold=0.5, completeness_threshold=0.5)
        assert all(m["case_id"].startswith("weak") for m in weak)
        sig = e.quality_signal_summary()
        assert sig["count"] == 10

    def test_registry_all_indexes_ingest_export_round_trip(self):
        from system_learning.types.semantic_memory_types import (
            IncidentBundle, MutationDiffRecord, PathDPreferencePair,
            PolicyGuardrailCase, GraphNeighborhood,
        )
        r = _registry()
        r.ingest_incident(IncidentBundle(
            trace_id="tr-int", trace_summary="s", violations=("V1",),
            route_path="L0->L3", tool_capability="route",
            state_diff_summary="d", healer_id="h1", outcome="success",
            policy_hash=_PH, timestamp_utc=_TS,
        ))
        r.ingest_graph_neighborhood(GraphNeighborhood(
            node_id="n1", node_type="Engine", layer="L3",
            inbound_relations=("A",), outbound_relations=("B",),
            governance_edges=("G",), mutation_edges=("M",),
            ownership_territory="apps_rg", risk_label="LOW",
        ))
        r.ingest_mutation(MutationDiffRecord(
            mutation_id="m1", target_resource="cfg",
            operations=("op:add",), state_diff_summary="diff",
            rollback_context="rb", commit_outcome="committed",
            trace_id="tr-m", policy_hash=_PH, timestamp_utc=_TS,
        ))
        r.ingest_prompt_outcome(_poem())
        r.ingest_retrieval_case(_rcr())
        r.ingest_replay_failure(_rfr())
        r.ingest_preference(PathDPreferencePair(
            decision_id="d1", original_plan="plan A",
            human_patch="plan B", decision="modified",
            reason="safer", resulting_outcome="ok",
            agent="A", trace_id="tr-pref", timestamp_utc=_TS,
        ))
        r.ingest_guardrail_case(PolicyGuardrailCase(
            case_id="gc1", blocked_payload_summary="p",
            remediation_text="fix", policy_hash=_PH,
            policy_root="root", verdict="true_positive",
            strictness_level="HIGH", trace_id="tr-gc", timestamp_utc=_TS,
        ))
        snap = r.buffer_snapshot()
        assert snap.total == 8
        dump = r.export_all_corpus_records()
        assert all(len(v) == 1 for v in dump.values())

    def test_multiindex_ingest_result_fields(self):
        r = _registry()
        res = r.ingest_prompt_outcome(_poem(trace_id="tr-field-test"))
        from system_learning.engines.semantic_index_registry import INDEX_PROMPT
        assert res.index_name == INDEX_PROMPT
        assert len(res.content_hash) == 64
        assert res.trace_id == "tr-field-test"
