"""Creative tests for BGE embedding extension new analytical methods.

New methods under test:

ReplayFailureEmbedder:
  - top_affected_subsystems(top_n)
  - evict_by_nondeterminism_type(nd_type)
  - replay_key_summary()

PromptOutcomeEmbedder:
  - top_templates_by_outcome(outcome, top_n)
  - model_stats()
  - evict_before_timestamp(cutoff_utc)
  - route_distribution()

RetrievalCaseEmbedder:
  - escalation_candidates(limit)
  - corpus_expansion_report()
  - evict_by_query_id(query_id)
  - score_percentile_buckets()

SemanticIndexRegistry:
  - total_buffer_utilization()
  - cross_index_health_report()
  - bulk_evict_by_trace_id(trace_id)
  - index_namespace_map()

Creative angles exercised:
  1. Tie-breaking correctness — identical counts sorted alphabetically
  2. Cap enforcement — top_n / limit never exceeded
  3. Empty buffer edge cases — all methods safe on empty state
  4. Post-eviction consistency — analytical results update correctly
  5. Mutation safety — returned dicts/lists are copies not references
  6. Cross-method invariants — e.g. sum of buckets == buffer_size
  7. Health tier transitions — OK → WARN → CRITICAL boundary conditions
  8. bulk_evict spans multiple indexes atomically
  9. Namespace map completeness — covers all 8 ALL_INDEXES constants
  10. Concurrent read/write — no races on analytical methods
"""

from __future__ import annotations

import threading

import pytest

# ============================================================
# Constants
# ============================================================

_TS = 1_700_300_000
_RK_A = "rka-" + "a" * 59
_RK_B = "rkb-" + "b" * 59
_DD = "dd0-" + "c" * 59
_PH = "ph0-" + "d" * 59


# ============================================================
# Builder helpers
# ============================================================

def _rfr(
    failure_id="f001", summary="hash mismatch", nd_type="HASH_MISMATCH",
    mismatch="digest diff", subsystems=("L3", "L0"),
    remediation="reseed", replay_key=_RK_A, dd=_DD, trace_id="tr-001", ts=_TS,
):
    from system_learning.types.semantic_memory_types import ReplayFailureRecord
    return ReplayFailureRecord(
        failure_id=failure_id, failure_summary=summary,
        nondeterminism_type=nd_type, mismatch_explanation=mismatch,
        affected_subsystems=subsystems, attempted_remediation=remediation,
        replay_key=replay_key, determinism_digest=dd,
        trace_id=trace_id, timestamp_utc=ts,
    )


def _poem(
    record_id="r001", s0="sys", d0="dom", i0="ins", c0="ctx", u0="usr",
    task="classify", answer="ORDER_STATUS", safety="ALLOWED",
    grounding="3/5 matched", prompt_hash="ph_x", template_id="tmpl-v3",
    route="L2_STANDARD", model="gpt-4o-mini", policy_hash=_PH,
    trace_id="tr-p001", ts=_TS,
):
    from system_learning.types.semantic_memory_types import PromptOutcomeEmbeddingRecord
    return PromptOutcomeEmbeddingRecord(
        record_id=record_id, slot_s0_summary=s0, slot_d0_summary=d0,
        slot_i0_summary=i0, slot_c0_summary=c0, slot_u0_summary=u0,
        task_description=task, answer_summary=answer, safety_outcome=safety,
        retrieval_grounding_summary=grounding, prompt_hash=prompt_hash,
        template_id=template_id, route=route, model=model,
        policy_hash=policy_hash, trace_id=trace_id, timestamp_utc=ts,
    )


def _rcr(
    case_id="c001", query="refund policy?",
    chunks=("refund text", "return window"),
    support_reasoning="both match", quality="complete",
    query_id="qid-001", chunk_ids=("cid-001",),
    support_score=0.85, completeness_score=0.90,
    escalation_flag=False, healer_invoked=False, replay_pass=True,
    trace_id="tr-rc001", ts=_TS,
):
    from system_learning.types.semantic_memory_types import RetrievalCaseRecord
    return RetrievalCaseRecord(
        case_id=case_id, query_summary=query, chunk_summaries=chunks,
        support_reasoning=support_reasoning, answer_quality_summary=quality,
        query_id=query_id, chunk_ids=chunk_ids,
        support_score=support_score, completeness_score=completeness_score,
        escalation_flag=escalation_flag, healer_invoked=healer_invoked,
        replay_pass=replay_pass, trace_id=trace_id, timestamp_utc=ts,
    )


def _rfe():
    from system_learning.engines.replay_failure_embedder import ReplayFailureEmbedder
    return ReplayFailureEmbedder(max_buffer=10_000)


def _poe():
    from system_learning.engines.prompt_outcome_embedder import PromptOutcomeEmbedder
    return PromptOutcomeEmbedder(max_buffer=10_000)


def _rce():
    from system_learning.engines.retrieval_case_embedder import RetrievalCaseEmbedder
    return RetrievalCaseEmbedder(max_buffer=10_000)


def _reg(**kw):
    from system_learning.engines.semantic_index_registry import SemanticIndexRegistry
    return SemanticIndexRegistry(**kw)


# ============================================================
# 1. ReplayFailureEmbedder — top_affected_subsystems
# ============================================================

class TestTopAffectedSubsystems:

    def test_empty_buffer_returns_empty(self):
        e = _rfe()
        assert e.top_affected_subsystems() == []

    def test_single_record_counts_each_subsystem(self):
        e = _rfe()
        e.ingest(_rfr(subsystems=("L3", "L0", "L1")))
        result = e.top_affected_subsystems()
        names = [r[0] for r in result]
        assert "L3" in names and "L0" in names and "L1" in names
        assert all(c == 1 for _, c in result)

    def test_most_frequent_subsystem_ranks_first(self):
        e = _rfe()
        for i in range(5):
            e.ingest(_rfr(failure_id=f"fa{i}", trace_id=f"ta{i}",
                          summary=f"sa{i}", subsystems=("L3", "L2")))
        for i in range(2):
            e.ingest(_rfr(failure_id=f"fb{i}", trace_id=f"tb{i}",
                          summary=f"sb{i}", subsystems=("L0",)))
        result = e.top_affected_subsystems()
        assert result[0][0] in ("L3", "L2")
        assert result[0][1] == 5

    def test_tie_broken_alphabetically(self):
        e = _rfe()
        e.ingest(_rfr(failure_id="f1", trace_id="t1", summary="s1",
                      subsystems=("ZZZ", "AAA")))
        e.ingest(_rfr(failure_id="f2", trace_id="t2", summary="s2",
                      subsystems=("ZZZ", "AAA")))
        result = e.top_affected_subsystems()
        counts = dict(result)
        assert counts["AAA"] == counts["ZZZ"] == 2
        first_names = [n for n, _ in result[:2]]
        assert first_names == sorted(first_names)

    def test_top_n_capped_at_50(self):
        e = _rfe()
        for i in range(60):
            e.ingest(_rfr(failure_id=f"f{i}", trace_id=f"t{i}",
                          summary=f"s{i}", subsystems=(f"SYS_{i:03d}",)))
        assert len(e.top_affected_subsystems(top_n=999)) <= 50

    def test_top_n_limits_output(self):
        e = _rfe()
        for i in range(10):
            e.ingest(_rfr(failure_id=f"f{i}", trace_id=f"t{i}",
                          summary=f"s{i}", subsystems=(f"SYS_{i}",)))
        assert len(e.top_affected_subsystems(top_n=3)) == 3

    def test_eviction_updates_subsystem_counts(self):
        e = _rfe()
        for i in range(4):
            e.ingest(_rfr(failure_id=f"fa{i}", trace_id=f"ta{i}",
                          summary=f"sa{i}", subsystems=("L3",), replay_key=_RK_A))
        for i in range(2):
            e.ingest(_rfr(failure_id=f"fb{i}", trace_id=f"tb{i}",
                          summary=f"sb{i}", subsystems=("L0",), replay_key=_RK_B))
        e.evict_by_replay_key(_RK_A)
        result = e.top_affected_subsystems()
        counts = dict(result)
        assert counts.get("L3", 0) == 0
        assert counts.get("L0", 0) == 2

    def test_multiple_subsystems_per_record_all_counted(self):
        e = _rfe()
        e.ingest(_rfr(subsystems=("A", "B", "C", "D", "E")))
        result = e.top_affected_subsystems()
        assert len(result) == 5
        assert all(c == 1 for _, c in result)

    def test_concurrent_read_does_not_crash(self):
        e = _rfe()
        for i in range(50):
            e.ingest(_rfr(failure_id=f"f{i}", trace_id=f"t{i}",
                          summary=f"s{i}", subsystems=(f"S{i % 5}",)))
        errors = []
        def reader():
            try:
                for _ in range(10):
                    e.top_affected_subsystems()
            except Exception as exc:
                errors.append(exc)
        threads = [threading.Thread(target=reader) for _ in range(4)]
        for t in threads: t.start()
        for t in threads: t.join()
        assert errors == []


# ============================================================
# 2. ReplayFailureEmbedder — evict_by_nondeterminism_type
# ============================================================

class TestEvictByNondeterminismType:

    def test_evicts_correct_records(self):
        e = _rfe()
        for i in range(3):
            e.ingest(_rfr(failure_id=f"fh{i}", trace_id=f"th{i}",
                          summary=f"sh{i}", nd_type="HASH_MISMATCH"))
        for i in range(2):
            e.ingest(_rfr(failure_id=f"fo{i}", trace_id=f"to{i}",
                          summary=f"so{i}", nd_type="ORDERING_INSTABILITY"))
        n = e.evict_by_nondeterminism_type("HASH_MISMATCH")
        assert n == 3
        assert e.buffer_size() == 2

    def test_stats_updated_after_eviction(self):
        e = _rfe()
        for i in range(3):
            e.ingest(_rfr(failure_id=f"fh{i}", trace_id=f"th{i}",
                          summary=f"sh{i}", nd_type="HASH_MISMATCH"))
        e.evict_by_nondeterminism_type("HASH_MISMATCH")
        assert e.nondeterminism_type_stats().get("HASH_MISMATCH", 0) == 0

    def test_meta_cleaned_after_eviction(self):
        e = _rfe()
        e.ingest(_rfr(nd_type="TIMING_DEPENDENCY"))
        e.evict_by_nondeterminism_type("TIMING_DEPENDENCY")
        assert e.buffer_size() == 0
        assert len(e._meta) == 0  # noqa: SLF001

    def test_idempotent(self):
        e = _rfe()
        e.ingest(_rfr(nd_type="HASH_MISMATCH"))
        n1 = e.evict_by_nondeterminism_type("HASH_MISMATCH")
        n2 = e.evict_by_nondeterminism_type("HASH_MISMATCH")
        assert n1 == 1
        assert n2 == 0

    def test_empty_type_raises(self):
        e = _rfe()
        with pytest.raises(ValueError, match="nondeterminism_type"):
            e.evict_by_nondeterminism_type("")

    def test_nonexistent_type_returns_zero(self):
        e = _rfe()
        e.ingest(_rfr(nd_type="HASH_MISMATCH"))
        assert e.evict_by_nondeterminism_type("UNICORN_TYPE") == 0
        assert e.buffer_size() == 1

    def test_does_not_evict_different_type(self):
        e = _rfe()
        e.ingest(_rfr(failure_id="f1", trace_id="t1", summary="s1",
                      nd_type="HASH_MISMATCH"))
        e.ingest(_rfr(failure_id="f2", trace_id="t2", summary="s2",
                      nd_type="ORDERING_INSTABILITY"))
        e.evict_by_nondeterminism_type("HASH_MISMATCH")
        stats = e.nondeterminism_type_stats()
        assert stats.get("ORDERING_INSTABILITY", 0) == 1


# ============================================================
# 3. ReplayFailureEmbedder — replay_key_summary
# ============================================================

class TestReplayKeySummary:

    def test_empty_buffer_returns_empty(self):
        e = _rfe()
        assert e.replay_key_summary() == []

    def test_highest_count_first(self):
        e = _rfe()
        for i in range(5):
            e.ingest(_rfr(failure_id=f"fa{i}", trace_id=f"ta{i}",
                          summary=f"sa{i}", replay_key=_RK_A))
        for i in range(2):
            e.ingest(_rfr(failure_id=f"fb{i}", trace_id=f"tb{i}",
                          summary=f"sb{i}", replay_key=_RK_B))
        summary = e.replay_key_summary()
        assert summary[0] == (_RK_A, 5)
        assert summary[1] == (_RK_B, 2)

    def test_tie_broken_alphabetically_by_key(self):
        e = _rfe()
        rk_z = "zzz-" + "z" * 59
        rk_a = "aaa-" + "a" * 59
        for i in range(2):
            e.ingest(_rfr(failure_id=f"fz{i}", trace_id=f"tz{i}",
                          summary=f"sz{i}", replay_key=rk_z))
        for i in range(2):
            e.ingest(_rfr(failure_id=f"fa{i}", trace_id=f"ta{i}",
                          summary=f"sa{i}", replay_key=rk_a))
        summary = e.replay_key_summary()
        assert summary[0][0] == rk_a
        assert summary[1][0] == rk_z

    def test_sum_of_counts_equals_buffer_size(self):
        e = _rfe()
        for i in range(3):
            e.ingest(_rfr(failure_id=f"fa{i}", trace_id=f"ta{i}",
                          summary=f"sa{i}", replay_key=_RK_A))
        for i in range(4):
            e.ingest(_rfr(failure_id=f"fb{i}", trace_id=f"tb{i}",
                          summary=f"sb{i}", replay_key=_RK_B))
        total = sum(c for _, c in e.replay_key_summary())
        assert total == e.buffer_size()

    def test_after_eviction_key_disappears(self):
        e = _rfe()
        e.ingest(_rfr(replay_key=_RK_A))
        e.evict_by_replay_key(_RK_A)
        keys = [k for k, _ in e.replay_key_summary()]
        assert _RK_A not in keys

    def test_returns_list_of_tuples(self):
        e = _rfe()
        e.ingest(_rfr())
        summary = e.replay_key_summary()
        assert isinstance(summary, list)
        assert isinstance(summary[0], tuple)
        assert len(summary[0]) == 2


# ============================================================
# 4. PromptOutcomeEmbedder — top_templates_by_outcome
# ============================================================

class TestTopTemplatesByOutcome:

    def test_empty_buffer_returns_empty(self):
        e = _poe()
        assert e.top_templates_by_outcome("ALLOWED") == []

    def test_invalid_outcome_raises(self):
        e = _poe()
        with pytest.raises(ValueError, match="outcome"):
            e.top_templates_by_outcome("INVALID_OUTCOME")

    def test_filters_by_outcome(self):
        e = _poe()
        for i in range(3):
            e.ingest(_poem(record_id=f"a{i}", trace_id=f"ta{i}",
                           task=f"t-a{i}", safety="ALLOWED",
                           template_id="tmpl-allow"))
        for i in range(2):
            e.ingest(_poem(record_id=f"b{i}", trace_id=f"tb{i}",
                           task=f"t-b{i}", safety="BLOCKED",
                           template_id="tmpl-block"))
        allowed = e.top_templates_by_outcome("ALLOWED")
        blocked = e.top_templates_by_outcome("BLOCKED")
        assert dict(allowed).get("tmpl-allow") == 3
        assert dict(allowed).get("tmpl-block", 0) == 0
        assert dict(blocked).get("tmpl-block") == 2

    def test_highest_count_first(self):
        e = _poe()
        for i in range(5):
            e.ingest(_poem(record_id=f"r-v3-{i}", trace_id=f"t-v3-{i}",
                           task=f"tv3{i}", safety="BLOCKED",
                           template_id="tmpl-v3"))
        for i in range(2):
            e.ingest(_poem(record_id=f"r-v4-{i}", trace_id=f"t-v4-{i}",
                           task=f"tv4{i}", safety="BLOCKED",
                           template_id="tmpl-v4"))
        result = e.top_templates_by_outcome("BLOCKED")
        assert result[0] == ("tmpl-v3", 5)

    def test_tie_broken_alphabetically(self):
        e = _poe()
        for tid in ("tmpl-zzz", "tmpl-aaa"):
            for i in range(2):
                e.ingest(_poem(record_id=f"r-{tid}-{i}",
                               trace_id=f"t-{tid}-{i}",
                               task=f"task-{tid}-{i}",
                               safety="ESCALATED", template_id=tid))
        result = e.top_templates_by_outcome("ESCALATED")
        assert result[0][0] == "tmpl-aaa"

    def test_top_n_capped_at_50(self):
        e = _poe()
        for i in range(55):
            e.ingest(_poem(record_id=f"r{i}", trace_id=f"t{i}",
                           task=f"task{i}", safety="ALLOWED",
                           template_id=f"tmpl-{i:03d}"))
        assert len(e.top_templates_by_outcome("ALLOWED", top_n=999)) <= 50

    def test_top_n_limits_output(self):
        e = _poe()
        for i in range(10):
            e.ingest(_poem(record_id=f"r{i}", trace_id=f"t{i}",
                           task=f"task{i}", safety="ALLOWED",
                           template_id=f"tmpl-{i}"))
        assert len(e.top_templates_by_outcome("ALLOWED", top_n=3)) == 3

    def test_after_eviction_counts_updated(self):
        e = _poe()
        for i in range(3):
            e.ingest(_poem(record_id=f"rv3{i}", trace_id=f"tv3{i}",
                           task=f"tv3task{i}", safety="BLOCKED",
                           template_id="tmpl-v3"))
        e.evict_by_template_id("tmpl-v3")
        assert e.top_templates_by_outcome("BLOCKED") == []


# ============================================================
# 5. PromptOutcomeEmbedder — model_stats
# ============================================================

class TestModelStats:

    def test_empty_buffer_returns_empty_dict(self):
        e = _poe()
        assert e.model_stats() == {}

    def test_correct_breakdown_per_model(self):
        e = _poe()
        for i in range(3):
            e.ingest(_poem(record_id=f"ra{i}", trace_id=f"ta{i}",
                           task=f"ta{i}", safety="ALLOWED", model="gpt-4o"))
        for i in range(2):
            e.ingest(_poem(record_id=f"rb{i}", trace_id=f"tb{i}",
                           task=f"tb{i}", safety="BLOCKED", model="gpt-4o"))
        e.ingest(_poem(record_id="rc0", trace_id="tc0", task="tc0",
                       safety="ALLOWED", model="gpt-3.5-turbo"))
        stats = e.model_stats()
        assert stats["gpt-4o"]["ALLOWED"] == 3
        assert stats["gpt-4o"]["BLOCKED"] == 2
        assert stats["gpt-3.5-turbo"]["ALLOWED"] == 1

    def test_sorted_by_model_name(self):
        e = _poe()
        for model in ("zzz-model", "aaa-model", "mmm-model"):
            e.ingest(_poem(record_id=f"r-{model}", trace_id=f"t-{model}",
                           task=f"task-{model}", model=model))
        keys = list(e.model_stats().keys())
        assert keys == sorted(keys)

    def test_multiple_outcomes_same_model(self):
        e = _poe()
        for outcome in ("ALLOWED", "BLOCKED", "ESCALATED", "HEALED", "UNKNOWN"):
            e.ingest(_poem(record_id=f"r-{outcome}", trace_id=f"t-{outcome}",
                           task=f"task-{outcome}", safety=outcome, model="uni-model"))
        stats = e.model_stats()
        assert len(stats["uni-model"]) == 5

    def test_returns_only_observed_outcomes(self):
        e = _poe()
        e.ingest(_poem(record_id="r1", trace_id="t1", task="t1",
                       safety="ALLOWED", model="sparse-model"))
        stats = e.model_stats()
        assert "ALLOWED" in stats["sparse-model"]
        assert "BLOCKED" not in stats["sparse-model"]

    def test_after_eviction_model_disappears(self):
        e = _poe()
        e.ingest(_poem(record_id="rv", trace_id="tv", task="tv",
                       safety="ALLOWED", model="old-model",
                       template_id="tmpl-old"))
        e.evict_by_template_id("tmpl-old")
        assert "old-model" not in e.model_stats()


# ============================================================
# 6. PromptOutcomeEmbedder — evict_before_timestamp
# ============================================================

class TestEvictBeforeTimestamp:

    def test_evicts_records_with_ts_prefix_below_cutoff(self):
        e = _poe()
        e.ingest(_poem(record_id="r-old", task="old", trace_id="@TS:1000"))
        e.ingest(_poem(record_id="r-new", task="new", trace_id="@TS:2000"))
        n = e.evict_before_timestamp(1500)
        assert n == 1
        assert e.buffer_size() == 1

    def test_keeps_records_at_or_above_cutoff(self):
        e = _poe()
        e.ingest(_poem(record_id="r-exact", task="exact",
                       trace_id="@TS:1500"))
        n = e.evict_before_timestamp(1500)
        assert n == 0
        assert e.buffer_size() == 1

    def test_records_without_ts_prefix_kept(self):
        e = _poe()
        e.ingest(_poem(record_id="r-notimestamp", task="no-ts",
                       trace_id="plain-trace-id"))
        n = e.evict_before_timestamp(9_999_999)
        assert n == 0
        assert e.buffer_size() == 1

    def test_zero_cutoff_raises(self):
        e = _poe()
        with pytest.raises(ValueError, match="cutoff_utc"):
            e.evict_before_timestamp(0)

    def test_negative_cutoff_raises(self):
        e = _poe()
        with pytest.raises(ValueError, match="cutoff_utc"):
            e.evict_before_timestamp(-1)

    def test_malformed_ts_prefix_kept(self):
        e = _poe()
        e.ingest(_poem(record_id="r-bad", task="bad", trace_id="@TS:not_an_int"))
        n = e.evict_before_timestamp(999_999)
        assert n == 0

    def test_meta_cleaned_after_eviction(self):
        e = _poe()
        e.ingest(_poem(record_id="r-old", task="old", trace_id="@TS:100"))
        e.evict_before_timestamp(500)
        assert e.buffer_size() == 0
        assert len(e._meta) == 0  # noqa: SLF001

    def test_idempotent(self):
        e = _poe()
        e.ingest(_poem(record_id="r-old", task="old", trace_id="@TS:100"))
        n1 = e.evict_before_timestamp(500)
        n2 = e.evict_before_timestamp(500)
        assert n1 == 1
        assert n2 == 0


# ============================================================
# 7. PromptOutcomeEmbedder — route_distribution
# ============================================================

class TestRouteDistribution:

    def test_empty_buffer_returns_empty(self):
        e = _poe()
        assert e.route_distribution() == {}

    def test_counts_by_route(self):
        e = _poe()
        for i in range(3):
            e.ingest(_poem(record_id=f"rs{i}", trace_id=f"ts{i}",
                           task=f"ts{i}", route="L2_STANDARD"))
        for i in range(2):
            e.ingest(_poem(record_id=f"rp{i}", trace_id=f"tp{i}",
                           task=f"tp{i}", route="L2_PREMIUM"))
        dist = e.route_distribution()
        assert dist["L2_STANDARD"] == 3
        assert dist["L2_PREMIUM"] == 2

    def test_sorted_alphabetically(self):
        e = _poe()
        for route in ("ZZZ", "AAA", "MMM"):
            e.ingest(_poem(record_id=f"r-{route}", trace_id=f"t-{route}",
                           task=f"task-{route}", route=route))
        keys = list(e.route_distribution().keys())
        assert keys == sorted(keys)

    def test_sum_equals_buffer_size(self):
        e = _poe()
        for i, route in enumerate(["R1", "R2", "R1", "R3"]):
            e.ingest(_poem(record_id=f"r{i}", trace_id=f"t{i}",
                           task=f"t{i}", route=route))
        dist = e.route_distribution()
        assert sum(dist.values()) == e.buffer_size()

    def test_after_eviction_route_removed(self):
        e = _poe()
        e.ingest(_poem(record_id="r-stale", trace_id="t-stale",
                       task="stale", route="STALE_ROUTE",
                       template_id="tmpl-stale"))
        e.evict_by_template_id("tmpl-stale")
        assert "STALE_ROUTE" not in e.route_distribution()


# ============================================================
# 8. RetrievalCaseEmbedder — escalation_candidates
# ============================================================

class TestEscalationCandidates:

    def test_empty_buffer_returns_empty(self):
        e = _rce()
        assert e.escalation_candidates() == []

    def test_only_escalated_cases_returned(self):
        e = _rce()
        e.ingest(_rcr(case_id="esc", query="q-esc",
                      chunk_ids=("x0",), escalation_flag=True))
        e.ingest(_rcr(case_id="non", query="q-non",
                      chunk_ids=("x1",), escalation_flag=False))
        cands = e.escalation_candidates()
        assert len(cands) == 1
        assert cands[0]["case_id"] == "esc"

    def test_sorted_by_completeness_score_asc(self):
        e = _rce()
        for i, cs in enumerate([0.9, 0.3, 0.6]):
            e.ingest(_rcr(case_id=f"esc-{i}", query=f"q{i}",
                          chunk_ids=(f"x{i}",), escalation_flag=True,
                          completeness_score=cs))
        cands = e.escalation_candidates()
        scores = [m["completeness_score"] for m in cands]
        assert scores == sorted(scores)

    def test_limit_respected(self):
        e = _rce()
        for i in range(20):
            e.ingest(_rcr(case_id=f"e{i}", query=f"q{i}",
                          chunk_ids=(f"x{i}",), escalation_flag=True))
        assert len(e.escalation_candidates(limit=5)) == 5

    def test_limit_capped_at_100(self):
        e = _rce()
        for i in range(120):
            e.ingest(_rcr(case_id=f"e{i}", query=f"q{i}",
                          chunk_ids=(f"x{i}",), escalation_flag=True))
        assert len(e.escalation_candidates(limit=9999)) <= 100

    def test_returns_copies_not_references(self):
        e = _rce()
        e.ingest(_rcr(case_id="esc-ref", query="q-ref",
                      chunk_ids=("x0",), escalation_flag=True))
        cands = e.escalation_candidates()
        cands[0]["case_id"] = "MUTATED"
        cands2 = e.escalation_candidates()
        assert cands2[0]["case_id"] == "esc-ref"

    def test_tie_broken_by_case_id(self):
        e = _rce()
        for cid in ("zzz-esc", "aaa-esc"):
            e.ingest(_rcr(case_id=cid, query=f"q-{cid}",
                          chunk_ids=(f"x-{cid}",),
                          escalation_flag=True, completeness_score=0.5))
        cands = e.escalation_candidates()
        assert cands[0]["case_id"] == "aaa-esc"


# ============================================================
# 9. RetrievalCaseEmbedder — corpus_expansion_report
# ============================================================

class TestCorpusExpansionReport:

    def test_empty_buffer_healthy(self):
        e = _rce()
        r = e.corpus_expansion_report()
        assert r["quality_tier"] == "HEALTHY"
        assert r["total"] == 0
        assert r["pure_escalation_count"] == 0

    def test_pure_escalation_count_correct(self):
        e = _rce()
        e.ingest(_rcr(case_id="pe", query="q-pe", chunk_ids=("x0",),
                      escalation_flag=True, healer_invoked=False))
        e.ingest(_rcr(case_id="he", query="q-he", chunk_ids=("x1",),
                      escalation_flag=True, healer_invoked=True))
        e.ingest(_rcr(case_id="ne", query="q-ne", chunk_ids=("x2",),
                      escalation_flag=False, healer_invoked=False))
        r = e.corpus_expansion_report()
        assert r["pure_escalation_count"] == 1

    def test_weak_support_count_correct(self):
        e = _rce()
        for i in range(4):
            e.ingest(_rcr(case_id=f"w{i}", query=f"q{i}",
                          chunk_ids=(f"x{i}",), support_score=0.3))
        for i in range(2):
            e.ingest(_rcr(case_id=f"s{i}", query=f"qs{i}",
                          chunk_ids=(f"xs{i}",), support_score=0.9))
        r = e.corpus_expansion_report()
        assert r["weak_support_count"] == 4

    def test_replay_failure_count_correct(self):
        e = _rce()
        for i in range(3):
            e.ingest(_rcr(case_id=f"rf{i}", query=f"qr{i}",
                          chunk_ids=(f"xr{i}",), replay_pass=False))
        r = e.corpus_expansion_report()
        assert r["replay_failure_count"] == 3

    def test_tier_healthy_when_degradation_rate_below_20pct(self):
        e = _rce()
        for i in range(9):
            e.ingest(_rcr(case_id=f"s{i}", query=f"qs{i}",
                          chunk_ids=(f"xs{i}",),
                          support_score=0.9, replay_pass=True))
        e.ingest(_rcr(case_id="w0", query="qw0", chunk_ids=("xw0",),
                      support_score=0.3))
        r = e.corpus_expansion_report()
        assert r["quality_tier"] == "HEALTHY"

    def test_tier_degraded_when_between_20_and_50pct(self):
        e = _rce()
        for i in range(7):
            e.ingest(_rcr(case_id=f"s{i}", query=f"qs{i}",
                          chunk_ids=(f"xs{i}",), support_score=0.9))
        for i in range(3):
            e.ingest(_rcr(case_id=f"w{i}", query=f"qw{i}",
                          chunk_ids=(f"xw{i}",), support_score=0.2))
        r = e.corpus_expansion_report()
        assert r["quality_tier"] == "DEGRADED"

    def test_tier_critical_when_above_50pct(self):
        e = _rce()
        for i in range(4):
            e.ingest(_rcr(case_id=f"s{i}", query=f"qs{i}",
                          chunk_ids=(f"xs{i}",), support_score=0.9))
        for i in range(6):
            e.ingest(_rcr(case_id=f"w{i}", query=f"qw{i}",
                          chunk_ids=(f"xw{i}",), support_score=0.1,
                          replay_pass=False))
        r = e.corpus_expansion_report()
        assert r["quality_tier"] == "CRITICAL"

    def test_total_matches_buffer_size(self):
        e = _rce()
        for i in range(7):
            e.ingest(_rcr(case_id=f"c{i}", query=f"q{i}",
                          chunk_ids=(f"x{i}",)))
        r = e.corpus_expansion_report()
        assert r["total"] == e.buffer_size()


# ============================================================
# 10. RetrievalCaseEmbedder — evict_by_query_id
# ============================================================

class TestEvictByQueryId:

    def test_evicts_correct_records(self):
        e = _rce()
        for i in range(3):
            e.ingest(_rcr(case_id=f"c-q1-{i}", query=f"q-q1-{i}",
                          chunk_ids=(f"x{i}",), query_id="qid-001"))
        for i in range(2):
            e.ingest(_rcr(case_id=f"c-q2-{i}", query=f"q-q2-{i}",
                          chunk_ids=(f"y{i}",), query_id="qid-002"))
        n = e.evict_by_query_id("qid-001")
        assert n == 3
        assert e.buffer_size() == 2

    def test_empty_query_id_raises(self):
        e = _rce()
        with pytest.raises(ValueError, match="query_id"):
            e.evict_by_query_id("")

    def test_idempotent(self):
        e = _rce()
        e.ingest(_rcr(query_id="qid-x"))
        n1 = e.evict_by_query_id("qid-x")
        n2 = e.evict_by_query_id("qid-x")
        assert n1 == 1
        assert n2 == 0

    def test_meta_cleaned(self):
        e = _rce()
        e.ingest(_rcr(query_id="qid-clean"))
        e.evict_by_query_id("qid-clean")
        assert len(e._meta) == 0  # noqa: SLF001

    def test_nonexistent_query_id_returns_zero(self):
        e = _rce()
        e.ingest(_rcr(query_id="qid-real"))
        assert e.evict_by_query_id("qid-nonexistent") == 0

    def test_does_not_evict_different_query_id(self):
        e = _rce()
        e.ingest(_rcr(case_id="keep", query_id="qid-keep"))
        e.ingest(_rcr(case_id="evict", query=f"q-evict",
                      chunk_ids=("y0",), query_id="qid-evict"))
        e.evict_by_query_id("qid-evict")
        weak = e.retrieve_weak_cases(support_threshold=1.0)
        ids = [m["case_id"] for m in weak]
        assert "evict" not in ids


# ============================================================
# 11. RetrievalCaseEmbedder — score_percentile_buckets
# ============================================================

class TestScorePercentileBuckets:

    def test_empty_buffer_all_zeros(self):
        e = _rce()
        buckets = e.score_percentile_buckets()
        for key in ("support_score", "completeness_score"):
            assert buckets[key] == {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}

    def test_q1_bucket_for_low_scores(self):
        e = _rce()
        e.ingest(_rcr(support_score=0.1, completeness_score=0.15))
        b = e.score_percentile_buckets()
        assert b["support_score"]["Q1"] == 1
        assert b["completeness_score"]["Q1"] == 1

    def test_q4_bucket_for_high_scores(self):
        e = _rce()
        e.ingest(_rcr(support_score=0.9, completeness_score=0.8))
        b = e.score_percentile_buckets()
        assert b["support_score"]["Q4"] == 1
        assert b["completeness_score"]["Q4"] == 1

    def test_boundary_values_correct_bucket(self):
        e = _rce()
        e.ingest(_rcr(case_id="c025", query="q025", chunk_ids=("x0",),
                      support_score=0.25, completeness_score=0.5))
        b = e.score_percentile_buckets()
        assert b["support_score"]["Q2"] == 1
        assert b["completeness_score"]["Q3"] == 1

    def test_sum_of_buckets_equals_buffer_size(self):
        e = _rce()
        for i in range(12):
            e.ingest(_rcr(case_id=f"c{i}", query=f"q{i}",
                          chunk_ids=(f"x{i}",),
                          support_score=round((i % 4) * 0.25 + 0.01, 3),
                          completeness_score=round((i % 4) * 0.25 + 0.01, 3)))
        b = e.score_percentile_buckets()
        assert sum(b["support_score"].values()) == e.buffer_size()
        assert sum(b["completeness_score"].values()) == e.buffer_size()

    def test_all_four_buckets_always_present(self):
        e = _rce()
        e.ingest(_rcr())
        b = e.score_percentile_buckets()
        for key in ("support_score", "completeness_score"):
            assert set(b[key].keys()) == {"Q1", "Q2", "Q3", "Q4"}

    def test_returns_independent_copies(self):
        e = _rce()
        e.ingest(_rcr())
        b1 = e.score_percentile_buckets()
        b1["support_score"]["Q1"] = 999
        b2 = e.score_percentile_buckets()
        assert b2["support_score"]["Q1"] != 999


# ============================================================
# 12. SemanticIndexRegistry — total_buffer_utilization
# ============================================================

class TestTotalBufferUtilization:

    def test_all_indexes_present(self):
        from system_learning.engines.semantic_index_registry import ALL_INDEXES
        r = _reg()
        util = r.total_buffer_utilization()
        for idx in ALL_INDEXES:
            assert idx in util

    def test_total_used_and_capacity_present(self):
        r = _reg()
        util = r.total_buffer_utilization()
        assert "total_used" in util
        assert "total_capacity" in util

    def test_utilization_zero_on_empty(self):
        r = _reg()
        util = r.total_buffer_utilization()
        from system_learning.engines.semantic_index_registry import ALL_INDEXES
        for idx in ALL_INDEXES:
            assert util[idx]["used"] == 0
            assert util[idx]["utilization"] == 0.0

    def test_utilization_correct_after_ingest(self):
        r = _reg(prompt_buffer=100)
        for i in range(10):
            r.ingest_prompt_outcome(_poem(record_id=f"r{i}", trace_id=f"t{i}",
                                          task=f"task{i}"))
        from system_learning.engines.semantic_index_registry import INDEX_PROMPT
        util = r.total_buffer_utilization()
        assert util[INDEX_PROMPT]["used"] == 10
        assert util[INDEX_PROMPT]["capacity"] == 100
        assert abs(util[INDEX_PROMPT]["utilization"] - 0.1) < 1e-4

    def test_total_used_is_sum_of_all_used(self):
        r = _reg()
        r.ingest_prompt_outcome(_poem())
        r.ingest_replay_failure(_rfr())
        r.ingest_retrieval_case(_rcr())
        util = r.total_buffer_utilization()
        from system_learning.engines.semantic_index_registry import ALL_INDEXES
        manual_sum = sum(util[idx]["used"] for idx in ALL_INDEXES)
        assert util["total_used"] == manual_sum == 3


# ============================================================
# 13. SemanticIndexRegistry — cross_index_health_report
# ============================================================

class TestCrossIndexHealthReport:

    def test_empty_registry_is_ok(self):
        r = _reg()
        report = r.cross_index_health_report()
        assert report["health"] == "OK"
        assert report["total_records"] == 0

    def test_required_keys_present(self):
        r = _reg()
        report = r.cross_index_health_report()
        for key in (
            "health", "total_records", "total_capacity",
            "retrieval_avg_support_score", "retrieval_avg_completeness_score",
            "retrieval_escalation_rate", "retrieval_quality_tier",
            "prompt_blocked_count", "prompt_escalated_count",
            "replay_top3_nondeterminism",
            "guardrail_false_positive_count", "guardrail_true_positive_count",
        ):
            assert key in report, f"missing key: {key}"

    def test_health_critical_when_retrieval_tier_critical(self):
        r = _reg()
        for i in range(6):
            r.ingest_retrieval_case(_rcr(
                case_id=f"w{i}", query=f"q{i}", chunk_ids=(f"x{i}",),
                support_score=0.1, replay_pass=False,
            ))
        for i in range(4):
            r.ingest_retrieval_case(_rcr(
                case_id=f"s{i}", query=f"qs{i}", chunk_ids=(f"xs{i}",),
                support_score=0.9,
            ))
        report = r.cross_index_health_report()
        assert report["health"] == "CRITICAL"

    def test_health_warn_when_any_index_over_90pct(self):
        r = _reg(prompt_buffer=10)
        for i in range(10):
            r.ingest_prompt_outcome(_poem(record_id=f"r{i}",
                                          trace_id=f"t{i}", task=f"task{i}"))
        report = r.cross_index_health_report()
        assert report["health"] in ("WARN", "CRITICAL")

    def test_prompt_blocked_count_correct(self):
        r = _reg()
        for i in range(3):
            r.ingest_prompt_outcome(_poem(record_id=f"b{i}", trace_id=f"tb{i}",
                                          task=f"t-b{i}", safety="BLOCKED"))
        report = r.cross_index_health_report()
        assert report["prompt_blocked_count"] == 3

    def test_guardrail_false_positive_count_correct(self):
        from system_learning.types.semantic_memory_types import PolicyGuardrailCase
        r = _reg()
        r.ingest_guardrail_case(PolicyGuardrailCase(
            case_id="fp0", blocked_payload_summary="payload A - SQL inject attempt",
            remediation_text="sanitize input", policy_hash=_PH,
            policy_root="root_sql", verdict="false_positive",
            strictness_level="LOW", trace_id="tr-fp0", timestamp_utc=_TS,
        ))
        r.ingest_guardrail_case(PolicyGuardrailCase(
            case_id="fp1", blocked_payload_summary="payload B - XSS attempt",
            remediation_text="escape output", policy_hash=_PH,
            policy_root="root_xss", verdict="false_positive",
            strictness_level="MEDIUM", trace_id="tr-fp1", timestamp_utc=_TS + 1,
        ))
        report = r.cross_index_health_report()
        assert report["guardrail_false_positive_count"] == 2

    def test_replay_top3_nondeterminism_correct(self):
        r = _reg()
        for i in range(5):
            r.ingest_replay_failure(_rfr(failure_id=f"fh{i}",
                                         trace_id=f"th{i}",
                                         summary=f"sh{i}",
                                         nd_type="HASH_MISMATCH"))
        for i in range(3):
            r.ingest_replay_failure(_rfr(failure_id=f"fo{i}",
                                         trace_id=f"to{i}",
                                         summary=f"so{i}",
                                         nd_type="ORDERING_INSTABILITY"))
        report = r.cross_index_health_report()
        top3 = dict(report["replay_top3_nondeterminism"])
        assert top3.get("HASH_MISMATCH", 0) == 5

    def test_total_records_matches_snapshot_total(self):
        r = _reg()
        r.ingest_prompt_outcome(_poem())
        r.ingest_replay_failure(_rfr())
        r.ingest_retrieval_case(_rcr())
        report = r.cross_index_health_report()
        assert report["total_records"] == r.buffer_snapshot().total


# ============================================================
# 14. SemanticIndexRegistry — bulk_evict_by_trace_id
# ============================================================

class TestBulkEvictByTraceId:

    def test_empty_trace_id_raises(self):
        r = _reg()
        with pytest.raises(ValueError, match="trace_id"):
            r.bulk_evict_by_trace_id("")

    def test_returns_dict_with_all_8_indexes(self):
        from system_learning.engines.semantic_index_registry import ALL_INDEXES
        r = _reg()
        result = r.bulk_evict_by_trace_id("tr-nobody")
        assert set(result.keys()) == ALL_INDEXES

    def test_all_zeros_when_trace_not_found(self):
        r = _reg()
        r.ingest_prompt_outcome(_poem(trace_id="tr-real"))
        result = r.bulk_evict_by_trace_id("tr-ghost")
        assert all(v == 0 for v in result.values())
        assert r.buffer_snapshot().total == 1

    def test_evicts_from_correct_index(self):
        from system_learning.engines.semantic_index_registry import INDEX_PROMPT
        r = _reg()
        r.ingest_prompt_outcome(_poem(trace_id="tr-target"))
        r.ingest_prompt_outcome(_poem(record_id="r-keep", trace_id="tr-keep",
                                      task="keep-task"))
        result = r.bulk_evict_by_trace_id("tr-target")
        assert result[INDEX_PROMPT] == 1
        assert r.buffer_snapshot().prompt_index == 1

    def test_evicts_across_multiple_indexes(self):
        from system_learning.engines.semantic_index_registry import (
            INDEX_PROMPT, INDEX_REPLAY, INDEX_RETRIEVAL,
        )
        r = _reg()
        shared_trace = "tr-shared"
        r.ingest_prompt_outcome(_poem(trace_id=shared_trace))
        r.ingest_replay_failure(_rfr(trace_id=shared_trace))
        r.ingest_retrieval_case(_rcr(trace_id=shared_trace))
        result = r.bulk_evict_by_trace_id(shared_trace)
        assert result[INDEX_PROMPT] == 1
        assert result[INDEX_REPLAY] == 1
        assert result[INDEX_RETRIEVAL] == 1
        assert r.buffer_snapshot().total == 0

    def test_does_not_evict_different_trace(self):
        r = _reg()
        r.ingest_prompt_outcome(_poem(trace_id="tr-safe"))
        r.ingest_prompt_outcome(_poem(record_id="r-target", trace_id="tr-target",
                                      task="target-task"))
        r.bulk_evict_by_trace_id("tr-target")
        assert r.buffer_snapshot().prompt_index == 1

    def test_idempotent(self):
        r = _reg()
        r.ingest_prompt_outcome(_poem(trace_id="tr-once"))
        from system_learning.engines.semantic_index_registry import INDEX_PROMPT
        r1 = r.bulk_evict_by_trace_id("tr-once")
        r2 = r.bulk_evict_by_trace_id("tr-once")
        assert r1[INDEX_PROMPT] == 1
        assert r2[INDEX_PROMPT] == 0

    def test_concurrent_bulk_evict_thread_safe(self):
        r = _reg(prompt_buffer=10_000)
        for i in range(100):
            r.ingest_prompt_outcome(_poem(record_id=f"r{i}",
                                          trace_id=f"tr-{i}",
                                          task=f"task{i}"))
        errors = []
        def worker(i):
            try:
                r.bulk_evict_by_trace_id(f"tr-{i}")
            except Exception as exc:
                errors.append(exc)
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(100)]
        for t in threads: t.start()
        for t in threads: t.join()
        assert errors == []
        assert r.buffer_snapshot().prompt_index == 0


# ============================================================
# 15. SemanticIndexRegistry — index_namespace_map
# ============================================================

class TestIndexNamespaceMap:

    def test_returns_all_8_indexes(self):
        from system_learning.engines.semantic_index_registry import ALL_INDEXES
        nm = _reg().index_namespace_map()
        assert set(nm.keys()) == ALL_INDEXES

    def test_namespaces_are_nonempty_strings(self):
        nm = _reg().index_namespace_map()
        for k, v in nm.items():
            assert isinstance(v, str) and len(v) > 0, f"empty namespace for {k}"

    def test_namespace_values_unique(self):
        nm = _reg().index_namespace_map()
        namespaces = list(nm.values())
        assert len(namespaces) == len(set(namespaces))

    def test_known_namespaces_correct(self):
        from system_learning.engines.semantic_index_registry import (
            INDEX_REPLAY, INDEX_PROMPT, INDEX_RETRIEVAL,
        )
        nm = _reg().index_namespace_map()
        assert nm[INDEX_REPLAY] == "replay_failures"
        assert nm[INDEX_PROMPT] == "prompt_outcomes"
        assert nm[INDEX_RETRIEVAL] == "retrieval_cases"

    def test_static_method_callable_without_instance(self):
        from system_learning.engines.semantic_index_registry import SemanticIndexRegistry
        nm = SemanticIndexRegistry.index_namespace_map()
        assert isinstance(nm, dict)


# ============================================================
# 16. Integration — multi-method pipelines
# ============================================================

class TestCreativeIntegration:

    def test_replay_full_pipeline_top_subsystems_then_evict_type(self):
        e = _rfe()
        for i in range(4):
            e.ingest(_rfr(failure_id=f"h{i}", trace_id=f"th{i}", summary=f"sh{i}",
                          nd_type="HASH_MISMATCH", subsystems=("L3", "L2")))
        for i in range(2):
            e.ingest(_rfr(failure_id=f"o{i}", trace_id=f"to{i}", summary=f"so{i}",
                          nd_type="ORDERING_INSTABILITY", subsystems=("L1",)))
        top = e.top_affected_subsystems(top_n=3)
        names = [n for n, _ in top]
        assert "L3" in names and "L2" in names
        e.evict_by_nondeterminism_type("HASH_MISMATCH")
        stats = e.nondeterminism_type_stats()
        assert stats.get("HASH_MISMATCH", 0) == 0
        top_after = e.top_affected_subsystems()
        assert dict(top_after).get("L1", 0) == 2

    def test_prompt_model_stats_then_evict_before_ts(self):
        e = _poe()
        e.ingest(_poem(record_id="old1", safety="BLOCKED", model="gpt-4o",
                       trace_id="@TS:500", task="old-task-1"))
        e.ingest(_poem(record_id="old2", safety="ALLOWED", model="gpt-4o",
                       trace_id="@TS:800", task="old-task-2"))
        e.ingest(_poem(record_id="new1", safety="BLOCKED", model="gpt-4o",
                       trace_id="@TS:2000", task="new-task"))
        stats_before = e.model_stats()
        assert stats_before["gpt-4o"]["BLOCKED"] == 2
        e.evict_before_timestamp(1000)
        stats_after = e.model_stats()
        assert stats_after["gpt-4o"]["BLOCKED"] == 1
        assert stats_after["gpt-4o"].get("ALLOWED", 0) == 0

    def test_retrieval_expansion_report_then_evict_bad_queries(self):
        e = _rce()
        for i in range(6):
            e.ingest(_rcr(case_id=f"bad{i}", query=f"q-bad{i}",
                          chunk_ids=(f"xb{i}",),
                          support_score=0.1, replay_pass=False,
                          query_id="qid-bad"))
        for i in range(4):
            e.ingest(_rcr(case_id=f"good{i}", query=f"q-good{i}",
                          chunk_ids=(f"xg{i}",),
                          support_score=0.9, replay_pass=True,
                          query_id="qid-good"))
        report = e.corpus_expansion_report()
        assert report["quality_tier"] == "CRITICAL"
        e.evict_by_query_id("qid-bad")
        report_after = e.corpus_expansion_report()
        assert report_after["quality_tier"] == "HEALTHY"

    def test_registry_health_transitions_ok_to_critical(self):
        r = _reg()
        report_empty = r.cross_index_health_report()
        assert report_empty["health"] == "OK"
        for i in range(8):
            r.ingest_retrieval_case(_rcr(
                case_id=f"w{i}", query=f"q{i}", chunk_ids=(f"x{i}",),
                support_score=0.05, replay_pass=False,
            ))
        for i in range(2):
            r.ingest_retrieval_case(_rcr(
                case_id=f"ok{i}", query=f"qok{i}", chunk_ids=(f"xok{i}",),
                support_score=0.9,
            ))
        report_critical = r.cross_index_health_report()
        assert report_critical["health"] == "CRITICAL"

    def test_registry_bulk_evict_then_health_ok(self):
        r = _reg()
        bad_trace = "tr-bad-trace"
        for i in range(8):
            r.ingest_retrieval_case(_rcr(
                case_id=f"w{i}", query=f"q{i}", chunk_ids=(f"x{i}",),
                support_score=0.05, replay_pass=False,
                trace_id=bad_trace,
            ))
        r.bulk_evict_by_trace_id(bad_trace)
        assert r.buffer_snapshot().total == 0
        report = r.cross_index_health_report()
        assert report["health"] == "OK"

    def test_score_buckets_plus_quality_summary_consistent(self):
        e = _rce()
        for i in range(4):
            e.ingest(_rcr(case_id=f"q1-{i}", query=f"q{i}",
                          chunk_ids=(f"x{i}",), support_score=0.1))
        for i in range(4):
            e.ingest(_rcr(case_id=f"q4-{i}", query=f"qq{i}",
                          chunk_ids=(f"y{i}",), support_score=0.9))
        buckets = e.score_percentile_buckets()
        sig = e.quality_signal_summary()
        assert buckets["support_score"]["Q1"] == 4
        assert buckets["support_score"]["Q4"] == 4
        assert abs(sig["avg_support_score"] - 0.5) < 0.1
