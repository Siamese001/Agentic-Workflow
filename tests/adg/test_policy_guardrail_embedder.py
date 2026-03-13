"""Creative and comprehensive tests for PolicyGuardrailEmbedder.

Test philosophy
---------------
1. **Invariant probing** — frozen dataclass identity, hash stability, C0_INFORMATIONAL
2. **Buffer mechanics** — eviction at capacity, LRU ordering, meta consistency after evict
3. **Verdict filtering** — retrieve_by_verdict, retrieve_false_positives, verdict_stats
4. **Analytical methods** — top_strictness_levels counting, ranking, tie-breaking
5. **Eviction by policy_hash** — selective removal, meta integrity, count accuracy
6. **Corpus export** — deterministic sort, snapshot independence, JSONL round-trip
7. **case_from_l5_block** — convenience constructor, invalid verdicts rejected
8. **Thread safety** — concurrent ingest from multiple threads
9. **Embedding text invariants** — canonical separators, field order stability
10. **Idempotency** — same case ingested twice = two separate CorpusRecords (content-hash dedup
    is caller's responsibility, not the embedder's)
11. **Boundary** — max_buffer=1, single-element buffer, empty buffer edge cases
12. **Integration** — ingest → evict → verdict_stats → top_strictness round-trip
"""

from __future__ import annotations

import threading
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TS = 1_700_100_000
_POLICY_A = "a" * 64
_POLICY_B = "b" * 64


def _make_case(
    case_id: str = "case-001",
    payload: str = "inject SQL",
    remediation: str = "sanitize input",
    policy_hash: str = _POLICY_A,
    policy_root: str = "root_sql_injection",
    verdict: str = "true_positive",
    strictness: str = "HIGH",
    trace_id: str = "tr-001",
    ts: int = _TS,
) -> "PolicyGuardrailCase":
    from system_learning.types.semantic_memory_types import PolicyGuardrailCase

    return PolicyGuardrailCase(
        case_id=case_id,
        blocked_payload_summary=payload,
        remediation_text=remediation,
        policy_hash=policy_hash,
        policy_root=policy_root,
        verdict=verdict,  # type: ignore[arg-type]
        strictness_level=strictness,
        trace_id=trace_id,
        timestamp_utc=ts,
    )


def _make_embedder(max_buffer: int = 100) -> "PolicyGuardrailEmbedder":
    from system_learning.engines.policy_guardrail_embedder import PolicyGuardrailEmbedder

    return PolicyGuardrailEmbedder(max_buffer=max_buffer)


# ===========================================================================
# 1. Invariant probing — PolicyGuardrailCase
# ===========================================================================


class TestPolicyGuardrailCaseInvariants:

    def test_case_hash_computed_on_construction(self):
        c = _make_case()
        assert len(c.case_hash) == 64
        assert c.case_hash.isalnum()

    def test_case_hash_deterministic(self):
        c1 = _make_case()
        c2 = _make_case()
        assert c1.case_hash == c2.case_hash

    def test_different_payloads_give_different_hashes(self):
        c1 = _make_case(payload="inject SQL")
        c2 = _make_case(payload="path traversal ../etc/passwd")
        assert c1.case_hash != c2.case_hash

    def test_different_verdicts_give_different_hashes(self):
        c1 = _make_case(verdict="true_positive")
        c2 = _make_case(verdict="false_positive", case_id="case-002")
        assert c1.case_hash != c2.case_hash

    def test_influence_class_always_c0(self):
        c = _make_case()
        assert c.influence_class == "C0_INFORMATIONAL"

    def test_frozen_immutability(self):
        c = _make_case()
        with pytest.raises((AttributeError, TypeError)):
            c.verdict = "false_positive"  # type: ignore[misc]

    def test_empty_case_id_raises(self):
        from system_learning.types.semantic_memory_types import PolicyGuardrailCase

        with pytest.raises(ValueError, match="case_id"):
            PolicyGuardrailCase(
                case_id="",
                blocked_payload_summary="x",
                remediation_text="y",
                policy_hash=_POLICY_A,
                policy_root="r",
                verdict="true_positive",
                strictness_level="HIGH",
                trace_id="tr",
                timestamp_utc=_TS,
            )

    def test_invalid_verdict_raises(self):
        from system_learning.types.semantic_memory_types import PolicyGuardrailCase

        with pytest.raises(ValueError, match="verdict"):
            PolicyGuardrailCase(
                case_id="c",
                blocked_payload_summary="x",
                remediation_text="y",
                policy_hash=_POLICY_A,
                policy_root="r",
                verdict="maybe",  # type: ignore[arg-type]
                strictness_level="HIGH",
                trace_id="tr",
                timestamp_utc=_TS,
            )

    def test_all_three_verdicts_accepted(self):
        for v in ("true_positive", "false_positive", "false_negative"):
            c = _make_case(verdict=v, case_id=f"case-{v}")
            assert c.verdict == v

    def test_to_embedding_text_contains_all_fields(self):
        c = _make_case(
            payload="sql inject",
            remediation="sanitize",
            policy_hash="abc123",
            policy_root="root_sql",
            verdict="true_positive",
            strictness="HIGH",
        )
        text = c.to_embedding_text()
        assert "sql inject" in text
        assert "sanitize" in text
        assert "abc123" in text
        assert "root_sql" in text
        assert "true_positive" in text
        assert "HIGH" in text

    def test_to_embedding_text_uses_canonical_separator(self):
        c = _make_case()
        text = c.to_embedding_text()
        assert " ## " in text

    def test_to_embedding_text_deterministic(self):
        c1 = _make_case()
        c2 = _make_case()
        assert c1.to_embedding_text() == c2.to_embedding_text()


# ===========================================================================
# 2. Embedder construction
# ===========================================================================


class TestPolicyGuardrailEmbedderConstruction:

    def test_default_construction_succeeds(self):
        e = _make_embedder()
        assert e.buffer_size() == 0

    def test_max_buffer_zero_raises(self):
        from system_learning.engines.policy_guardrail_embedder import PolicyGuardrailEmbedder

        with pytest.raises(ValueError, match="max_buffer"):
            PolicyGuardrailEmbedder(max_buffer=0)

    def test_max_buffer_negative_raises(self):
        from system_learning.engines.policy_guardrail_embedder import PolicyGuardrailEmbedder

        with pytest.raises(ValueError, match="max_buffer"):
            PolicyGuardrailEmbedder(max_buffer=-10)

    def test_max_buffer_one_accepted(self):
        e = _make_embedder(max_buffer=1)
        assert e.buffer_size() == 0


# ===========================================================================
# 3. Ingest mechanics
# ===========================================================================


class TestIngest:

    def test_ingest_returns_corpus_record(self):
        from system_learning.engines.embedding_corpus_extraction import CorpusRecord

        e = _make_embedder()
        record = e.ingest(_make_case())
        assert isinstance(record, CorpusRecord)

    def test_ingest_increments_buffer_size(self):
        e = _make_embedder()
        assert e.buffer_size() == 0
        e.ingest(_make_case())
        assert e.buffer_size() == 1

    def test_ingest_corpus_record_has_correct_namespace(self):
        e = _make_embedder()
        r = e.ingest(_make_case())
        assert r.namespace == "policy_guardrail_cases"

    def test_ingest_corpus_record_text_matches_embedding_text(self):
        e = _make_embedder()
        case = _make_case()
        r = e.ingest(case)
        assert r.text == case.to_embedding_text()

    def test_ingest_corpus_record_trace_id_matches_case(self):
        e = _make_embedder()
        case = _make_case(trace_id="tr-xyz")
        r = e.ingest(case)
        assert r.trace_id == "tr-xyz"

    def test_ingest_content_hash_is_sha256_of_text(self):
        import hashlib

        e = _make_embedder()
        case = _make_case()
        r = e.ingest(case)
        expected = hashlib.sha256(case.to_embedding_text().encode("utf-8")).hexdigest()
        assert r.content_hash == expected

    def test_ingest_same_case_twice_creates_two_records(self):
        """Embedder does not deduplicate — caller is responsible."""
        e = _make_embedder()
        case = _make_case()
        e.ingest(case)
        e.ingest(case)
        assert e.buffer_size() == 2

    def test_ingest_batch_returns_same_order(self):
        e = _make_embedder()
        cases = [_make_case(case_id=f"case-{i}", trace_id=f"tr-{i}") for i in range(5)]
        records = e.ingest_batch(cases)
        assert len(records) == 5
        for i, r in enumerate(records):
            assert r.trace_id == f"tr-{i}"

    def test_ingest_batch_empty_list(self):
        e = _make_embedder()
        records = e.ingest_batch([])
        assert records == []


# ===========================================================================
# 4. Buffer eviction at capacity
# ===========================================================================


class TestBufferEviction:

    def test_buffer_evicts_oldest_at_capacity(self):
        e = _make_embedder(max_buffer=3)
        cases = [_make_case(case_id=f"c{i}", trace_id=f"tr-{i}") for i in range(4)]
        records = [e.ingest(c) for c in cases]
        # tr-0 should have been evicted
        assert e.buffer_size() == 3
        export = e.export_corpus_records()
        trace_ids = {r.trace_id for r in export}
        assert "tr-0" not in trace_ids
        assert "tr-3" in trace_ids

    def test_buffer_meta_cleaned_on_eviction(self):
        e = _make_embedder(max_buffer=2)
        c0 = _make_case(case_id="c0", trace_id="tr-0")
        c1 = _make_case(case_id="c1", trace_id="tr-1", payload="different content")
        c2 = _make_case(case_id="c2", trace_id="tr-2", payload="yet another content")
        r0 = e.ingest(c0)
        e.ingest(c1)
        e.ingest(c2)
        # r0 should have been evicted; its content_hash must not be in meta
        # Access internal meta through verdict_stats to verify counts don't include evicted
        assert e.buffer_size() == 2
        # If meta still held c0, verdict_stats would count 3 entries
        stats = e.verdict_stats()
        assert sum(stats.values()) == 2

    def test_max_buffer_one_always_keeps_latest(self):
        e = _make_embedder(max_buffer=1)
        cases = [_make_case(case_id=f"c{i}", trace_id=f"tr-{i}", payload=f"payload {i}") for i in range(5)]
        for c in cases:
            e.ingest(c)
        assert e.buffer_size() == 1
        export = e.export_corpus_records()
        assert export[0].trace_id == "tr-4"


# ===========================================================================
# 5. export_corpus_records
# ===========================================================================


class TestExportCorpusRecords:

    def test_export_sorted_by_content_hash_trace_id(self):
        e = _make_embedder()
        for i in range(10):
            e.ingest(_make_case(case_id=f"c{i}", trace_id=f"tr-{i:02d}", payload=f"payload {i}"))
        records = e.export_corpus_records()
        keys = [(r.content_hash, r.trace_id) for r in records]
        assert keys == sorted(keys)

    def test_export_is_snapshot_not_live_view(self):
        e = _make_embedder()
        e.ingest(_make_case(case_id="c0", payload="initial"))
        snapshot = e.export_corpus_records()
        e.ingest(_make_case(case_id="c1", trace_id="tr-new", payload="added later"))
        # Snapshot should still have only 1 record
        assert len(snapshot) == 1

    def test_export_empty_buffer_returns_empty_list(self):
        e = _make_embedder()
        assert e.export_corpus_records() == []

    def test_export_all_namespaces_are_policy_guardrail_cases(self):
        e = _make_embedder()
        for i in range(5):
            e.ingest(_make_case(case_id=f"c{i}", trace_id=f"tr-{i}", payload=f"p {i}"))
        for r in e.export_corpus_records():
            assert r.namespace == "policy_guardrail_cases"


# ===========================================================================
# 6. verdict_stats
# ===========================================================================


class TestVerdictStats:

    def test_empty_buffer_returns_all_zeros(self):
        e = _make_embedder()
        stats = e.verdict_stats()
        assert stats == {"true_positive": 0, "false_positive": 0, "false_negative": 0}

    def test_counts_all_verdicts_correctly(self):
        e = _make_embedder()
        e.ingest(_make_case(case_id="c1", verdict="true_positive", trace_id="t1", payload="p1"))
        e.ingest(_make_case(case_id="c2", verdict="true_positive", trace_id="t2", payload="p2"))
        e.ingest(_make_case(case_id="c3", verdict="false_positive", trace_id="t3", payload="p3"))
        e.ingest(_make_case(case_id="c4", verdict="false_negative", trace_id="t4", payload="p4"))
        stats = e.verdict_stats()
        assert stats["true_positive"] == 2
        assert stats["false_positive"] == 1
        assert stats["false_negative"] == 1

    def test_verdict_stats_always_returns_all_three_keys(self):
        e = _make_embedder()
        e.ingest(_make_case(verdict="true_positive"))
        stats = e.verdict_stats()
        assert set(stats.keys()) == {"true_positive", "false_positive", "false_negative"}

    def test_verdict_stats_updates_after_eviction(self):
        e = _make_embedder(max_buffer=2)
        e.ingest(_make_case(case_id="c0", verdict="false_positive", trace_id="t0", payload="a"))
        e.ingest(_make_case(case_id="c1", verdict="true_positive", trace_id="t1", payload="b"))
        e.ingest(_make_case(case_id="c2", verdict="true_positive", trace_id="t2", payload="c"))
        # c0 (false_positive) was evicted
        stats = e.verdict_stats()
        assert stats["false_positive"] == 0
        assert stats["true_positive"] == 2

    def test_verdict_stats_sum_equals_buffer_size(self):
        e = _make_embedder()
        verdicts = ["true_positive", "false_positive", "false_negative",
                    "true_positive", "true_positive"]
        for i, v in enumerate(verdicts):
            e.ingest(_make_case(case_id=f"c{i}", verdict=v, trace_id=f"t{i}", payload=f"p{i}"))
        stats = e.verdict_stats()
        assert sum(stats.values()) == e.buffer_size()


# ===========================================================================
# 7. retrieve_by_verdict
# ===========================================================================


class TestRetrieveByVerdict:

    def _populate(self, embedder, counts: dict[str, int]) -> None:
        idx = 0
        for verdict, n in counts.items():
            for _ in range(n):
                embedder.ingest(_make_case(
                    case_id=f"c-{verdict}-{idx}",
                    verdict=verdict,
                    trace_id=f"t-{idx}",
                    payload=f"payload-{verdict}-{idx}",
                ))
                idx += 1

    def test_retrieve_by_verdict_returns_only_matching(self):
        e = _make_embedder()
        self._populate(e, {"true_positive": 3, "false_positive": 2})
        results = e.retrieve_by_verdict("false_positive")
        assert len(results) == 2
        assert all(m["verdict"] == "false_positive" for m in results)

    def test_retrieve_by_verdict_sorted_by_case_id(self):
        e = _make_embedder()
        for i in (5, 2, 9, 1):
            e.ingest(_make_case(
                case_id=f"c-{i:03d}", verdict="false_negative",
                trace_id=f"t-{i}", payload=f"p{i}",
            ))
        results = e.retrieve_by_verdict("false_negative")
        ids = [m["case_id"] for m in results]
        assert ids == sorted(ids)

    def test_retrieve_by_verdict_limit_respected(self):
        e = _make_embedder()
        for i in range(10):
            e.ingest(_make_case(case_id=f"c{i}", verdict="true_positive",
                                trace_id=f"t{i}", payload=f"p{i}"))
        results = e.retrieve_by_verdict("true_positive", limit=4)
        assert len(results) == 4

    def test_retrieve_by_verdict_limit_capped_at_100(self):
        e = _make_embedder(max_buffer=200)
        for i in range(150):
            e.ingest(_make_case(case_id=f"c{i}", trace_id=f"t{i}", payload=f"p{i}"))
        results = e.retrieve_by_verdict("true_positive", limit=999)
        assert len(results) <= 100

    def test_retrieve_by_verdict_empty_when_none_match(self):
        e = _make_embedder()
        e.ingest(_make_case(verdict="true_positive"))
        results = e.retrieve_by_verdict("false_negative")
        assert results == []

    def test_retrieve_by_verdict_invalid_raises(self):
        e = _make_embedder()
        with pytest.raises(ValueError, match="verdict"):
            e.retrieve_by_verdict("UNKNOWN_VERDICT")

    def test_retrieve_by_verdict_returns_copies_not_references(self):
        """Mutating returned dicts must not corrupt internal meta."""
        e = _make_embedder()
        e.ingest(_make_case(verdict="false_positive"))
        results = e.retrieve_by_verdict("false_positive")
        results[0]["verdict"] = "MUTATED"
        # Internal state must not be affected
        stats = e.verdict_stats()
        assert stats["false_positive"] == 1


# ===========================================================================
# 8. retrieve_false_positives
# ===========================================================================


class TestRetrieveFalsePositives:

    def test_returns_only_false_positives(self):
        e = _make_embedder()
        for i in range(3):
            e.ingest(_make_case(case_id=f"fp{i}", verdict="false_positive",
                                trace_id=f"tfp{i}", payload=f"fp-{i}"))
        e.ingest(_make_case(case_id="tp1", verdict="true_positive", trace_id="ttp", payload="tp"))
        results = e.retrieve_false_positives()
        assert len(results) == 3
        assert all(m["verdict"] == "false_positive" for m in results)

    def test_empty_when_no_false_positives(self):
        e = _make_embedder()
        e.ingest(_make_case(verdict="true_positive"))
        assert e.retrieve_false_positives() == []

    def test_limit_forwarded_to_retrieve_by_verdict(self):
        e = _make_embedder()
        for i in range(10):
            e.ingest(_make_case(case_id=f"fp{i}", verdict="false_positive",
                                trace_id=f"t{i}", payload=f"p{i}"))
        results = e.retrieve_false_positives(limit=3)
        assert len(results) == 3


# ===========================================================================
# 9. evict_by_policy_hash
# ===========================================================================


class TestEvictByPolicyHash:

    def test_evict_removes_matching_records(self):
        e = _make_embedder()
        for i in range(5):
            e.ingest(_make_case(case_id=f"a{i}", trace_id=f"ta{i}",
                                policy_hash=_POLICY_A, payload=f"pa{i}"))
        for i in range(3):
            e.ingest(_make_case(case_id=f"b{i}", trace_id=f"tb{i}",
                                policy_hash=_POLICY_B, payload=f"pb{i}"))
        n = e.evict_by_policy_hash(_POLICY_A)
        assert n == 5
        assert e.buffer_size() == 3

    def test_evict_leaves_other_policies_intact(self):
        e = _make_embedder()
        for i in range(3):
            e.ingest(_make_case(case_id=f"b{i}", trace_id=f"tb{i}",
                                policy_hash=_POLICY_B, payload=f"pb{i}"))
        e.evict_by_policy_hash(_POLICY_A)
        assert e.buffer_size() == 3

    def test_evict_unknown_policy_returns_zero(self):
        e = _make_embedder()
        e.ingest(_make_case(policy_hash=_POLICY_A))
        n = e.evict_by_policy_hash(_POLICY_B)
        assert n == 0

    def test_evict_empty_policy_hash_raises(self):
        e = _make_embedder()
        with pytest.raises(ValueError, match="policy_hash"):
            e.evict_by_policy_hash("")

    def test_evict_removes_meta_entries(self):
        e = _make_embedder()
        for i in range(4):
            e.ingest(_make_case(case_id=f"c{i}", trace_id=f"t{i}",
                                policy_hash=_POLICY_A, payload=f"p{i}"))
        e.evict_by_policy_hash(_POLICY_A)
        stats = e.verdict_stats()
        assert sum(stats.values()) == 0

    def test_evict_twice_idempotent(self):
        e = _make_embedder()
        for i in range(3):
            e.ingest(_make_case(case_id=f"c{i}", trace_id=f"t{i}",
                                policy_hash=_POLICY_A, payload=f"p{i}"))
        n1 = e.evict_by_policy_hash(_POLICY_A)
        n2 = e.evict_by_policy_hash(_POLICY_A)
        assert n1 == 3
        assert n2 == 0
        assert e.buffer_size() == 0

    def test_evict_allows_subsequent_ingest(self):
        e = _make_embedder()
        for i in range(3):
            e.ingest(_make_case(case_id=f"c{i}", trace_id=f"t{i}",
                                policy_hash=_POLICY_A, payload=f"p{i}"))
        e.evict_by_policy_hash(_POLICY_A)
        e.ingest(_make_case(case_id="new", trace_id="tnew", policy_hash=_POLICY_B, payload="new"))
        assert e.buffer_size() == 1

    def test_evict_updates_verdict_stats(self):
        e = _make_embedder()
        e.ingest(_make_case(case_id="fp1", verdict="false_positive", trace_id="t1",
                            policy_hash=_POLICY_A, payload="fp pay"))
        e.ingest(_make_case(case_id="tp1", verdict="true_positive", trace_id="t2",
                            policy_hash=_POLICY_B, payload="tp pay"))
        e.evict_by_policy_hash(_POLICY_A)
        stats = e.verdict_stats()
        assert stats["false_positive"] == 0
        assert stats["true_positive"] == 1


# ===========================================================================
# 10. top_strictness_levels
# ===========================================================================


class TestTopStrictnessLevels:

    def _ingest_strictness_mix(self, embedder, mix: dict[str, int]) -> None:
        idx = 0
        for level, count in mix.items():
            for _ in range(count):
                embedder.ingest(_make_case(
                    case_id=f"s-{level}-{idx}",
                    trace_id=f"t-{idx}",
                    payload=f"p-{level}-{idx}",
                    strictness=level,
                ))
                idx += 1

    def test_returns_correct_counts(self):
        e = _make_embedder()
        self._ingest_strictness_mix(e, {"HIGH": 5, "MEDIUM": 3, "LOW": 1})
        top = e.top_strictness_levels(top_n=3)
        assert top[0] == ("HIGH", 5)
        assert top[1] == ("MEDIUM", 3)
        assert top[2] == ("LOW", 1)

    def test_sorted_desc_by_count(self):
        e = _make_embedder()
        self._ingest_strictness_mix(e, {"A": 2, "B": 10, "C": 5})
        top = e.top_strictness_levels(top_n=3)
        counts = [c for (_, c) in top]
        assert counts == sorted(counts, reverse=True)

    def test_tie_breaking_alphabetical(self):
        e = _make_embedder()
        self._ingest_strictness_mix(e, {"ZEBRA": 3, "ALPHA": 3, "MIDDLE": 3})
        top = e.top_strictness_levels(top_n=3)
        levels = [lvl for (lvl, _) in top]
        assert levels == sorted(levels)

    def test_top_n_limits_results(self):
        e = _make_embedder()
        self._ingest_strictness_mix(e, {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1})
        top = e.top_strictness_levels(top_n=2)
        assert len(top) == 2

    def test_top_n_capped_at_20(self):
        e = _make_embedder(max_buffer=1000)
        for i in range(25):
            e.ingest(_make_case(
                case_id=f"c{i}", trace_id=f"t{i}",
                payload=f"p{i}", strictness=f"LEVEL_{i:02d}",
            ))
        top = e.top_strictness_levels(top_n=999)
        assert len(top) <= 20

    def test_empty_buffer_returns_empty_list(self):
        e = _make_embedder()
        assert e.top_strictness_levels() == []

    def test_single_level(self):
        e = _make_embedder()
        for i in range(7):
            e.ingest(_make_case(case_id=f"c{i}", trace_id=f"t{i}",
                                payload=f"p{i}", strictness="CRITICAL"))
        top = e.top_strictness_levels()
        assert top == [("CRITICAL", 7)]

    def test_updates_after_evict_by_policy_hash(self):
        e = _make_embedder()
        for i in range(5):
            e.ingest(_make_case(case_id=f"ha{i}", trace_id=f"ta{i}",
                                payload=f"pa{i}", strictness="HIGH", policy_hash=_POLICY_A))
        for i in range(3):
            e.ingest(_make_case(case_id=f"mb{i}", trace_id=f"tb{i}",
                                payload=f"pb{i}", strictness="MEDIUM", policy_hash=_POLICY_B))
        e.evict_by_policy_hash(_POLICY_A)
        top = e.top_strictness_levels()
        assert top == [("MEDIUM", 3)]


# ===========================================================================
# 11. case_from_l5_block
# ===========================================================================


class TestCaseFromL5Block:

    def test_constructs_valid_case(self):
        from system_learning.engines.policy_guardrail_embedder import PolicyGuardrailEmbedder

        case = PolicyGuardrailEmbedder.case_from_l5_block(
            case_id="block-001",
            blocked_payload_summary="sql injection attempt",
            remediation_text="sanitize query params",
            policy_hash=_POLICY_A,
            policy_root="root_sql",
            verdict="true_positive",
            strictness_level="HIGH",
            trace_id="tr-block-001",
            timestamp_utc=_TS,
        )
        assert case.case_id == "block-001"
        assert case.verdict == "true_positive"
        assert case.influence_class == "C0_INFORMATIONAL"

    def test_invalid_verdict_raises(self):
        from system_learning.engines.policy_guardrail_embedder import PolicyGuardrailEmbedder

        with pytest.raises(ValueError, match="verdict"):
            PolicyGuardrailEmbedder.case_from_l5_block(
                case_id="block-002",
                blocked_payload_summary="x",
                remediation_text="y",
                policy_hash=_POLICY_A,
                policy_root="r",
                verdict="unknown",
                strictness_level="LOW",
                trace_id="tr-x",
                timestamp_utc=_TS,
            )

    def test_all_three_verdicts_accepted(self):
        from system_learning.engines.policy_guardrail_embedder import PolicyGuardrailEmbedder

        for v in ("true_positive", "false_positive", "false_negative"):
            case = PolicyGuardrailEmbedder.case_from_l5_block(
                case_id=f"block-{v}",
                blocked_payload_summary="x",
                remediation_text="y",
                policy_hash=_POLICY_A,
                policy_root="r",
                verdict=v,
                strictness_level="MED",
                trace_id=f"tr-{v}",
                timestamp_utc=_TS,
            )
            assert case.verdict == v

    def test_case_can_be_ingested(self):
        from system_learning.engines.policy_guardrail_embedder import PolicyGuardrailEmbedder

        e = _make_embedder()
        case = PolicyGuardrailEmbedder.case_from_l5_block(
            case_id="ingest-001",
            blocked_payload_summary="payload",
            remediation_text="fix",
            policy_hash=_POLICY_A,
            policy_root="root",
            verdict="true_positive",
            strictness_level="HIGH",
            trace_id="tr-ingest",
            timestamp_utc=_TS,
        )
        r = e.ingest(case)
        assert e.buffer_size() == 1
        assert r.trace_id == "tr-ingest"


# ===========================================================================
# 12. Thread safety — concurrent ingest
# ===========================================================================


class TestThreadSafety:

    def test_concurrent_ingest_consistent_buffer_size(self):
        e = _make_embedder(max_buffer=10_000)
        n_threads = 10
        n_per_thread = 50
        errors: list[Exception] = []

        def worker(thread_id: int) -> None:
            try:
                for j in range(n_per_thread):
                    e.ingest(_make_case(
                        case_id=f"t{thread_id}-c{j}",
                        trace_id=f"tr-{thread_id}-{j}",
                        payload=f"payload-{thread_id}-{j}",
                    ))
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Thread errors: {errors}"
        assert e.buffer_size() == n_threads * n_per_thread

    def test_concurrent_ingest_and_evict_no_crash(self):
        e = _make_embedder(max_buffer=10_000)
        errors: list[Exception] = []

        def ingest_worker() -> None:
            try:
                for j in range(30):
                    e.ingest(_make_case(
                        case_id=f"ci-{j}",
                        trace_id=f"tri-{j}",
                        payload=f"p-{j}",
                        policy_hash=_POLICY_A,
                    ))
            except Exception as exc:
                errors.append(exc)

        def evict_worker() -> None:
            try:
                for _ in range(5):
                    e.evict_by_policy_hash(_POLICY_A)
            except Exception as exc:
                errors.append(exc)

        threads = (
            [threading.Thread(target=ingest_worker) for _ in range(4)]
            + [threading.Thread(target=evict_worker) for _ in range(2)]
        )
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Thread errors: {errors}"

    def test_concurrent_verdict_stats_no_crash(self):
        e = _make_embedder(max_buffer=10_000)
        for i in range(100):
            e.ingest(_make_case(case_id=f"c{i}", trace_id=f"t{i}", payload=f"p{i}"))
        errors: list[Exception] = []

        def reader() -> None:
            try:
                for _ in range(20):
                    e.verdict_stats()
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=reader) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == []


# ===========================================================================
# 13. Embedding text invariants
# ===========================================================================


class TestEmbeddingTextInvariants:

    def test_embedding_text_has_6_segments(self):
        c = _make_case()
        parts = c.to_embedding_text().split(" ## ")
        assert len(parts) == 6

    def test_embedding_text_starts_with_payload(self):
        c = _make_case(payload="xss attack")
        text = c.to_embedding_text()
        assert text.startswith("payload:xss attack")

    def test_embedding_text_ends_with_strictness(self):
        c = _make_case(strictness="EXTREME")
        text = c.to_embedding_text()
        assert text.endswith("strictness:EXTREME")

    def test_embedding_text_policy_hash_field(self):
        c = _make_case(policy_hash="deadbeef1234")
        assert "policy:deadbeef1234" in c.to_embedding_text()

    def test_embedding_text_policy_root_field(self):
        c = _make_case(policy_root="root_xss")
        assert "root:root_xss" in c.to_embedding_text()

    def test_embedding_text_verdict_field(self):
        c = _make_case(verdict="false_negative", case_id="fn-1")
        assert "verdict:false_negative" in c.to_embedding_text()

    def test_two_distinct_payloads_produce_distinct_texts(self):
        c1 = _make_case(payload="payload A")
        c2 = _make_case(payload="payload B")
        assert c1.to_embedding_text() != c2.to_embedding_text()


# ===========================================================================
# 14. Integration — full round-trip
# ===========================================================================


class TestIntegration:

    def test_ingest_evict_then_verdict_stats_consistent(self):
        e = _make_embedder()
        # Ingest mix under two policies
        for i in range(4):
            e.ingest(_make_case(case_id=f"a{i}", verdict="true_positive",
                                trace_id=f"ta{i}", payload=f"pa{i}", policy_hash=_POLICY_A))
        for i in range(3):
            e.ingest(_make_case(case_id=f"b{i}", verdict="false_positive",
                                trace_id=f"tb{i}", payload=f"pb{i}", policy_hash=_POLICY_B))
        assert e.verdict_stats() == {
            "true_positive": 4, "false_positive": 3, "false_negative": 0
        }
        # Evict policy A → only B's false_positives remain
        e.evict_by_policy_hash(_POLICY_A)
        assert e.verdict_stats() == {
            "true_positive": 0, "false_positive": 3, "false_negative": 0
        }

    def test_top_strictness_after_partial_eviction(self):
        e = _make_embedder()
        for i in range(6):
            e.ingest(_make_case(case_id=f"ha{i}", trace_id=f"ta{i}", payload=f"pa{i}",
                                strictness="HIGH", policy_hash=_POLICY_A))
        for i in range(4):
            e.ingest(_make_case(case_id=f"mb{i}", trace_id=f"tb{i}", payload=f"pb{i}",
                                strictness="MEDIUM", policy_hash=_POLICY_B))
        e.evict_by_policy_hash(_POLICY_A)
        top = e.top_strictness_levels(top_n=5)
        assert top == [("MEDIUM", 4)]

    def test_case_from_l5_block_full_pipeline(self):
        from system_learning.engines.policy_guardrail_embedder import PolicyGuardrailEmbedder

        e = _make_embedder()
        for i in range(5):
            case = PolicyGuardrailEmbedder.case_from_l5_block(
                case_id=f"block-{i}",
                blocked_payload_summary=f"attack vector {i}",
                remediation_text=f"mitigation {i}",
                policy_hash=_POLICY_A,
                policy_root="root_injection",
                verdict="true_positive" if i % 2 == 0 else "false_positive",
                strictness_level="HIGH",
                trace_id=f"tr-{i}",
                timestamp_utc=_TS + i,
            )
            e.ingest(case)

        assert e.buffer_size() == 5
        fp = e.retrieve_false_positives()
        assert len(fp) == 2
        stats = e.verdict_stats()
        assert stats["true_positive"] == 3
        assert stats["false_positive"] == 2
        top = e.top_strictness_levels()
        assert top == [("HIGH", 5)]

    def test_ingest_batch_then_export_sorted(self):
        e = _make_embedder()
        cases = [
            _make_case(case_id=f"c{i}", trace_id=f"tr-{i:03d}", payload=f"payload {i}")
            for i in range(10)
        ]
        e.ingest_batch(cases)
        records = e.export_corpus_records()
        keys = [(r.content_hash, r.trace_id) for r in records]
        assert keys == sorted(keys)

    def test_retrieve_by_verdict_after_eviction_empty(self):
        e = _make_embedder()
        for i in range(5):
            e.ingest(_make_case(case_id=f"fp{i}", verdict="false_positive",
                                trace_id=f"t{i}", payload=f"p{i}", policy_hash=_POLICY_A))
        e.evict_by_policy_hash(_POLICY_A)
        results = e.retrieve_by_verdict("false_positive")
        assert results == []

    def test_buffer_size_tracks_evictions_correctly(self):
        e = _make_embedder()
        for i in range(10):
            e.ingest(_make_case(case_id=f"a{i}", trace_id=f"ta{i}", payload=f"pa{i}",
                                policy_hash=_POLICY_A))
        for i in range(5):
            e.ingest(_make_case(case_id=f"b{i}", trace_id=f"tb{i}", payload=f"pb{i}",
                                policy_hash=_POLICY_B))
        assert e.buffer_size() == 15
        e.evict_by_policy_hash(_POLICY_A)
        assert e.buffer_size() == 5
        e.evict_by_policy_hash(_POLICY_B)
        assert e.buffer_size() == 0
