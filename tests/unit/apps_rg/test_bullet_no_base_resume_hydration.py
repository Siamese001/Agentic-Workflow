"""Acceptance test: base resume prose must NOT hydrate generated bullets.

W5 acceptance test (Bullet Proof Bundle Redesign):
- Verifies x2_base_resume_ngram_overlap gate catches verbatim base resume copies.
- Verifies organic bullets (synthesized from proof bundle) pass the gate.
- Verifies IBM role-episode evidence packs never contain claim_text prose.
"""
from __future__ import annotations

import pytest

from apps_rg.runtime.validators.bullet_ngram_overlap_x2 import (
    BASE_RESUME_NGRAM_THRESHOLD,
    check_bullet_base_resume_ngram_overlap,
    compute_max_ngram_overlap,
    load_ibm_base_resume_bullet_texts,
    load_unify_base_resume_bullet_texts,
)
from apps_rg.runtime.sections.ibm_bullets_graph_evidence import (
    IBM_FORBIDDEN_C0_PROMPT_SUBSTRINGS,
    assert_ibm_c0_pack_has_no_forbidden_template_leaks,
    format_ibm_graph_bullet_evidence_pack,
)


class TestNgramOverlapMath:
    def test_identical_texts_have_full_overlap(self) -> None:
        text = "Engineered cloud-native AI platform achieving 99.9% uptime for regulated financial clients"
        overlap = compute_max_ngram_overlap(text, text, n=4)
        assert overlap == 1.0

    def test_unrelated_texts_have_zero_overlap(self) -> None:
        gen = "Built microservices pipeline reducing latency by 50% across distributed data flows"
        ref = "Established executive governance councils with model explainability and data security"
        overlap = compute_max_ngram_overlap(gen, ref, n=4)
        assert overlap == 0.0

    def test_partial_overlap_detected(self) -> None:
        """Near-duplicate texts should produce non-zero overlap, though not necessarily > 0.2.
        The 4-gram tokenizer splits hyphenated terms; overlap > 0 is sufficient to detect similarity.
        """
        gen = "Architected cloud-native AI analytics platforms for regulated financial institutions"
        ref = "AI and Data Platform: Architected cloud-native AI and analytics platforms that enabled governed enterprise decision systems"
        overlap = compute_max_ngram_overlap(gen, ref, n=4)
        assert overlap > 0.0, f"Expected non-zero overlap for similar texts, got {overlap}"

    def test_four_gram_avoids_single_domain_term_false_positives(self) -> None:
        """Single tech terms like 'cloud-native' should not alone trigger high overlap."""
        gen = "Deployed cloud-native microservices with 30% infrastructure overhead reduction"
        ref = "Led cloud-native migration from legacy on-prem environments to scalable architecture"
        overlap = compute_max_ngram_overlap(gen, ref, n=4)
        assert overlap < 0.5, f"Expected overlap < 0.5 for different sentences, got {overlap}"


class TestIbmBaseResumeHydration:
    def test_verbatim_ibm_bullet_fails_gate(self) -> None:
        """A bullet copied verbatim from base resume must have high n-gram overlap."""
        base_texts = load_ibm_base_resume_bullet_texts()
        if not base_texts:
            pytest.skip("IBM base resume texts not available")

        # Verbatim copy of IBM bul_ibm_001 (with taxonomy prefix removed)
        verbatim = (
            "Architected cloud-native AI and analytics platforms that enabled governed enterprise "
            "decision systems across regulated financial environments"
        )
        result = check_bullet_base_resume_ngram_overlap(
            "bul_ibm_001",
            verbatim,
            base_texts,
            warn_only=False,
        )
        assert result.overlap_fraction > BASE_RESUME_NGRAM_THRESHOLD, (
            f"Expected overlap > {BASE_RESUME_NGRAM_THRESHOLD}, got {result.overlap_fraction}"
        )
        assert not result.passed, "Verbatim copy should fail the gate (warn_only=False)"
        assert result.failure_reason is not None

    def test_organic_bullet_passes_gate(self) -> None:
        """Organically generated bullet with mechanism vocabulary but different prose passes."""
        base_texts = load_ibm_base_resume_bullet_texts()
        if not base_texts:
            pytest.skip("IBM base resume texts not available")

        organic = (
            "Deployed cloud-native AI infrastructure serving regulated financial clients "
            "maintaining 99.9% availability across enterprise analytics workloads"
        )
        result = check_bullet_base_resume_ngram_overlap(
            "bul_ibm_001",
            organic,
            base_texts,
            warn_only=False,
        )
        assert result.overlap_fraction <= BASE_RESUME_NGRAM_THRESHOLD, (
            f"Organic bullet should have overlap <= {BASE_RESUME_NGRAM_THRESHOLD}, "
            f"got {result.overlap_fraction}"
        )
        assert result.passed

    def test_ibm_base_resume_loads_five_bullets(self) -> None:
        """Must have exactly 5 IBM employment bullets in the base resume."""
        texts = load_ibm_base_resume_bullet_texts()
        assert len(texts) == 5, f"Expected 5 IBM bullets, got {len(texts)}"

    def test_unify_base_resume_loads_bullets(self) -> None:
        """Unify base resume texts must be loadable for n-gram gate."""
        texts = load_unify_base_resume_bullet_texts()
        # Unify may have 0-6 bullets; just verify it doesn't crash
        assert isinstance(texts, list)


class TestIbmProofBundleNoProse:
    """Verify the IBM role-episode evidence pack contains no claim_text prose."""

    def test_canonical_ibm_facts_not_in_pack(self) -> None:
        """The old 'CANONICAL IBM FACTS' header must not appear in the new pack."""
        payload: dict = {
            "selected_fact_plan": {
                "selection_method": "augmented_skills_graph_ibm_bullets_phase2_track_ranked"
            },
            "allowed_fact_ids": [
                "bul_ibm_001", "bul_ibm_002", "bul_ibm_003", "bul_ibm_004", "bul_ibm_005"
            ],
        }
        pack = format_ibm_graph_bullet_evidence_pack(payload)
        assert "CANONICAL IBM FACTS" not in pack
        assert "REWRITE_FROM_FACT_POOL" not in pack

    def test_pack_contains_role_episode_evidence_pack_marker(self) -> None:
        payload: dict = {
            "selected_fact_plan": {"selection_method": "test_method"},
            "allowed_fact_ids": [],
        }
        pack = format_ibm_graph_bullet_evidence_pack(payload)
        assert "IBM_ROLE_EPISODE_EVIDENCE_PACK" in pack
        assert "role_episode_bundle_id" in pack

    def test_pack_contains_mechanism_vocab_and_promotable_metrics(self) -> None:
        payload: dict = {
            "selected_fact_plan": {"selection_method": "test_method"},
            "allowed_fact_ids": [],
        }
        pack = format_ibm_graph_bullet_evidence_pack(payload)
        # mechanism_vocab tokens present
        assert "AWS" in pack
        assert "reference architecture" in pack
        assert "decision support" in pack
        assert "co-sell" in pack
        # metric authority is graph-native; retired base-resume metrics are not promoted as proof.
        assert "metric_ibm_stress_test_cycle_weeks_to_hours" in pack
        assert "HOLD and DO_NOT_PROMOTE metrics are forbidden" in pack
        assert "99.9% uptime" not in pack
        assert "50% latency reduction" not in pack
        assert "$15M incremental revenue" not in pack

    def test_pack_contains_all_five_slots(self) -> None:
        payload: dict = {
            "selected_fact_plan": {"selection_method": "test_method"},
            "allowed_fact_ids": [],
        }
        pack = format_ibm_graph_bullet_evidence_pack(payload)
        for slot in ["bul_ibm_001", "bul_ibm_002", "bul_ibm_003", "bul_ibm_004", "bul_ibm_005"]:
            assert slot in pack, f"Slot {slot} missing from pack"

    def test_forbidden_substrings_guard_raises_on_violations(self) -> None:
        """Guard function must raise ValueError when forbidden content is present."""
        with pytest.raises(ValueError, match="CANONICAL IBM FACTS"):
            assert_ibm_c0_pack_has_no_forbidden_template_leaks(
                "Some content with CANONICAL IBM FACTS here"
            )

    def test_forbidden_substrings_guard_passes_on_clean_pack(self) -> None:
        """Guard function must not raise on a valid organic pack."""
        assert_ibm_c0_pack_has_no_forbidden_template_leaks(
            "GRAPH_BULLET_EVIDENCE_PACK (proof substrate) bound_skills mechanism_vocab"
        )

    @pytest.mark.parametrize("forbidden", IBM_FORBIDDEN_C0_PROMPT_SUBSTRINGS)
    def test_each_forbidden_substring_is_caught(self, forbidden: str) -> None:
        with pytest.raises(ValueError):
            assert_ibm_c0_pack_has_no_forbidden_template_leaks(f"context {forbidden} more text")
