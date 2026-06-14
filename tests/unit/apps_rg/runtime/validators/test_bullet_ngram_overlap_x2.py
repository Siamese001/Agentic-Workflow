"""Wave 4.2 — unit tests for bullet_ngram_overlap_x2.

Covers the deterministic n-gram anti-leakage helpers: tokenization, n-gram
extraction, single- and multi-reference overlap fractions, and the WARN-mode
gate runners (base-resume / E0 example overlap).
"""

from __future__ import annotations

import pytest

from apps_rg.runtime.validators.bullet_ngram_overlap_x2 import (
    BASE_RESUME_NGRAM_THRESHOLD,
    GATE_ID_BASE_RESUME,
    GATE_ID_E0_EXAMPLE,
    NGRAM_SIZE,
    check_bullet_base_resume_ngram_overlap,
    check_bullet_e0_example_ngram_overlap,
    compute_max_ngram_overlap,
    compute_max_ngram_overlap_multi_reference,
    extract_ngrams,
    run_bullet_ngram_overlap_gates,
)


class TestExtractNgrams:
    def test_below_n_returns_empty(self) -> None:
        assert extract_ngrams(["a", "b"], 4) == set()

    def test_exact_n_single_ngram(self) -> None:
        assert extract_ngrams(["a", "b", "c", "d"], 4) == {("a", "b", "c", "d")}

    def test_sliding_window(self) -> None:
        grams = extract_ngrams(["a", "b", "c"], 2)
        assert grams == {("a", "b"), ("b", "c")}


class TestComputeMaxNgramOverlap:
    def test_identical_text_full_overlap(self) -> None:
        text = "the quick brown fox jumps"
        assert compute_max_ngram_overlap(text, text, n=4) == 1.0

    def test_disjoint_text_zero_overlap(self) -> None:
        assert (
            compute_max_ngram_overlap(
                "alpha beta gamma delta epsilon",
                "one two three four five six",
                n=4,
            )
            == 0.0
        )

    def test_no_ngrams_returns_zero(self) -> None:
        # generated text too short to form a 4-gram
        assert compute_max_ngram_overlap("short text", "anything here at all", n=4) == 0.0

    def test_partial_overlap_fraction(self) -> None:
        gen = "a b c d e"  # 4-grams: (a,b,c,d),(b,c,d,e) -> 2
        ref = "a b c d x"  # contains (a,b,c,d) only
        assert compute_max_ngram_overlap(gen, ref, n=4) == 0.5

    def test_empty_inputs(self) -> None:
        assert compute_max_ngram_overlap("", "", n=4) == 0.0


class TestMultiReference:
    def test_empty_references_zero(self) -> None:
        assert compute_max_ngram_overlap_multi_reference("a b c d e", [], n=4) == 0.0

    def test_combined_references(self) -> None:
        gen = "one two three four five"
        refs = ["xx yy", "one two three four"]
        assert compute_max_ngram_overlap_multi_reference(gen, refs, n=4) > 0.0


class TestGateRunnersWarnMode:
    def test_base_resume_warn_passes_even_on_overlap(self) -> None:
        res = check_bullet_base_resume_ngram_overlap(
            "bul_ibm_001",
            "a b c d e",
            ["a b c d e"],
            warn_only=True,
        )
        assert res.gate_id == GATE_ID_BASE_RESUME
        assert res.passed is True  # warn mode never blocks
        assert res.warn_only is True
        assert res.overlap_fraction == 1.0
        assert res.failure_reason is not None  # still records the violation

    def test_base_resume_hard_fail_blocks(self) -> None:
        res = check_bullet_base_resume_ngram_overlap(
            "bul_ibm_001",
            "a b c d e",
            ["a b c d e"],
            warn_only=False,
        )
        assert res.passed is False
        assert res.threshold == BASE_RESUME_NGRAM_THRESHOLD

    def test_e0_clean_bullet_passes_with_no_reason(self) -> None:
        res = check_bullet_e0_example_ngram_overlap(
            "bul_unify_001",
            "completely unrelated unique words here",
            ["sample example text reference corpus"],
            warn_only=False,
        )
        assert res.gate_id == GATE_ID_E0_EXAMPLE
        assert res.passed is True
        assert res.failure_reason is None


class TestRunBulletNgramOverlapGates:
    def test_filters_by_section_prefix(self) -> None:
        bullets = [
            {"bullet_id": "bul_ibm_001", "bullet_text": "a b c d e"},
            {"bullet_id": "bul_unify_001", "bullet_text": "x y z w v"},  # wrong prefix
        ]
        base_pass, base_results, e0_pass, e0_results = run_bullet_ngram_overlap_gates(
            bullets,
            section_id="ibm_bullets",
            base_resume_texts=["a b c d e"],
            e0_texts=["nothing matches here at all"],
            warn_only=True,
        )
        # only the bul_ibm_ bullet is considered
        assert len(base_results) == 1
        assert base_results[0].bullet_id == "bul_ibm_001"
        assert base_pass is True  # warn mode
        assert e0_pass is True

    def test_skips_non_dict_and_empty_text(self) -> None:
        bullets = [
            "not-a-dict",
            {"bullet_id": "bul_ibm_002", "bullet_text": "   "},
        ]
        base_pass, base_results, e0_pass, e0_results = run_bullet_ngram_overlap_gates(
            bullets,  # type: ignore[arg-type]
            section_id="ibm_bullets",
            base_resume_texts=["whatever reference text here"],
            e0_texts=["e0 reference text here too"],
            warn_only=True,
        )
        assert base_results == []
        assert e0_results == []
        assert base_pass is True
        assert e0_pass is True

    def test_constants(self) -> None:
        assert NGRAM_SIZE == 4
        assert 0.0 < BASE_RESUME_NGRAM_THRESHOLD < 1.0
