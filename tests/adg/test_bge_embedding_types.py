"""Type-invariant tests for BGE embedding extension addendum types.

Covers:
  - ReplayFailureRecord (addendum §2.4)
  - PromptOutcomeEmbeddingRecord (addendum §2.5)
  - RetrievalCaseRecord (addendum §2.6)
"""

from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_bge_embedding_types")
_emit_applies_guardrail("p0", "test_bge_embedding_types", "p0_governance")
_emit_reads_policy_state("p0", "test_bge_embedding_types", "policy_binding")
_emit_snapshots_state("p0", "test_bge_embedding_types", "state_snapshot")
emit_replay_key("p0", "test_bge_embedding_types")
emit_determinism_digest("p0", "test_bge_embedding_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
                failure_id="",
                failure_summary="x",
                nondeterminism_type="T",
                mismatch_explanation="m",
                affected_subsystems=(),
                attempted_remediation="r",
                replay_key=_RK,
                determinism_digest=_DD,
                trace_id="tr",
                timestamp_utc=_TS,
            )

    def test_empty_nondeterminism_type_raises(self):
        from system_learning.types.semantic_memory_types import ReplayFailureRecord

        with pytest.raises(ValueError, match="nondeterminism_type"):
            ReplayFailureRecord(
                failure_id="f",
                failure_summary="x",
                nondeterminism_type="",
                mismatch_explanation="m",
                affected_subsystems=(),
                attempted_remediation="r",
                replay_key=_RK,
                determinism_digest=_DD,
                trace_id="tr",
                timestamp_utc=_TS,
            )

    def test_empty_replay_key_raises(self):
        from system_learning.types.semantic_memory_types import ReplayFailureRecord

        with pytest.raises(ValueError, match="replay_key"):
            ReplayFailureRecord(
                failure_id="f",
                failure_summary="x",
                nondeterminism_type="T",
                mismatch_explanation="m",
                affected_subsystems=(),
                attempted_remediation="r",
                replay_key="",
                determinism_digest=_DD,
                trace_id="tr",
                timestamp_utc=_TS,
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
                record_id="",
                slot_s0_summary="s",
                slot_d0_summary="d",
                slot_i0_summary="i",
                slot_c0_summary="c",
                slot_u0_summary="u",
                task_description="t",
                answer_summary="a",
                safety_outcome="ALLOWED",
                retrieval_grounding_summary="g",
                prompt_hash="ph",
                template_id="ti",
                route="r",
                model="m",
                policy_hash="plh",
                trace_id="tr",
                timestamp_utc=_TS,
            )

    def test_invalid_safety_outcome_raises(self):
        from system_learning.types.semantic_memory_types import PromptOutcomeEmbeddingRecord

        with pytest.raises(ValueError, match="safety_outcome"):
            PromptOutcomeEmbeddingRecord(
                record_id="r",
                slot_s0_summary="s",
                slot_d0_summary="d",
                slot_i0_summary="i",
                slot_c0_summary="c",
                slot_u0_summary="u",
                task_description="t",
                answer_summary="a",
                safety_outcome="UNKNOWN_BAD",
                retrieval_grounding_summary="g",
                prompt_hash="ph",
                template_id="ti",
                route="r",
                model="m",
                policy_hash="plh",
                trace_id="tr",
                timestamp_utc=_TS,
            )

    def test_all_five_safety_outcomes_accepted(self):
        for outcome in ("ALLOWED", "BLOCKED", "ESCALATED", "HEALED", "UNKNOWN"):
            r = _poem(safety=outcome, record_id=f"r-{outcome}")
            assert r.safety_outcome == outcome

    def test_embedding_text_excludes_ids(self):
        r = _poem(
            prompt_hash="secret_ph", template_id="secret_tmpl", trace_id="secret_tr", policy_hash="secret_pol"
        )
        text = r.to_embedding_text()
        assert "secret_ph" not in text
        assert "secret_tmpl" not in text
        assert "secret_tr" not in text
        assert "secret_pol" not in text

    def test_embedding_text_contains_all_slot_summaries(self):
        r = _poem(
            s0="SYS", d0="DOM", i0="INS", c0="CTX", u0="USR", task="TASK", answer="ANS", grounding="GRND"
        )
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
                case_id="",
                query_summary="q",
                chunk_summaries=(),
                support_reasoning="s",
                answer_quality_summary="a",
                query_id="qi",
                chunk_ids=(),
                support_score=0.5,
                completeness_score=0.5,
                escalation_flag=False,
                healer_invoked=False,
                replay_pass=True,
                trace_id="tr",
                timestamp_utc=_TS,
            )

    def test_support_score_out_of_range_raises(self):
        from system_learning.types.semantic_memory_types import RetrievalCaseRecord

        with pytest.raises(ValueError, match="support_score"):
            RetrievalCaseRecord(
                case_id="c",
                query_summary="q",
                chunk_summaries=(),
                support_reasoning="s",
                answer_quality_summary="a",
                query_id="qi",
                chunk_ids=(),
                support_score=1.5,
                completeness_score=0.5,
                escalation_flag=False,
                healer_invoked=False,
                replay_pass=True,
                trace_id="tr",
                timestamp_utc=_TS,
            )

    def test_completeness_score_out_of_range_raises(self):
        from system_learning.types.semantic_memory_types import RetrievalCaseRecord

        with pytest.raises(ValueError, match="completeness_score"):
            RetrievalCaseRecord(
                case_id="c",
                query_summary="q",
                chunk_summaries=(),
                support_reasoning="s",
                answer_quality_summary="a",
                query_id="qi",
                chunk_ids=(),
                support_score=0.5,
                completeness_score=-0.1,
                escalation_flag=False,
                healer_invoked=False,
                replay_pass=True,
                trace_id="tr",
                timestamp_utc=_TS,
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
