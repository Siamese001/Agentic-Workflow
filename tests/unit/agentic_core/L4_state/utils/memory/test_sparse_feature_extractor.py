"""Unit tests for G1 hybrid fusion sparse feature extractor."""

from __future__ import annotations

import pytest

from agentic_core.L4_state.utils.memory.sparse_feature_extractor import (
    extract_features,
    fused_score,
    jaccard_overlap,
)


class TestExtractFeatures:
    def test_empty_input_returns_empty_list(self) -> None:
        assert extract_features("") == []

    def test_extracts_quarter_tokens(self) -> None:
        features = extract_features("What was revenue in Q3 2025?")
        assert "q3" in features
        assert "2025" in features

    def test_extracts_cardinal_numbers(self) -> None:
        features = extract_features("How many requests in 147 minutes?")
        assert "147" in features

    def test_extracts_iso_dates(self) -> None:
        features = extract_features("Events on 2025-04-23 only")
        assert "2025-04-23" in features

    def test_extracts_all_caps_acronyms(self) -> None:
        features = extract_features("How do I reset MFA for SSL certificates?")
        assert "mfa" in features
        assert "ssl" in features

    def test_extracts_proper_nouns_with_digits(self) -> None:
        features = extract_features("Compare Auth0 to Okta")
        assert "auth0" in features
        assert "okta" in features

    def test_stopwords_dropped(self) -> None:
        features = extract_features("The a an is of to and or for")
        assert features == []

    def test_deterministic_ordering(self) -> None:
        a = extract_features("Q3 2025 MFA Okta")
        b = extract_features("Okta MFA Q3 2025")
        assert a == b

    def test_deduplicates(self) -> None:
        features = extract_features("Okta Okta OKTA okta")
        assert features.count("okta") == 1


class TestJaccardOverlap:
    def test_identical_sets_return_one(self) -> None:
        assert jaccard_overlap(["a", "b"], ["a", "b"]) == pytest.approx(1.0)

    def test_disjoint_sets_return_zero(self) -> None:
        assert jaccard_overlap(["a", "b"], ["c", "d"]) == 0.0

    def test_partial_overlap(self) -> None:
        assert jaccard_overlap(["a", "b"], ["b", "c"]) == pytest.approx(1.0 / 3.0)

    def test_empty_left_returns_zero(self) -> None:
        assert jaccard_overlap([], ["a"]) == 0.0

    def test_empty_right_returns_zero(self) -> None:
        assert jaccard_overlap(["a"], []) == 0.0

    def test_symmetric(self) -> None:
        a = jaccard_overlap(["a", "b", "c"], ["b", "c", "d"])
        b = jaccard_overlap(["b", "c", "d"], ["a", "b", "c"])
        assert a == b


class TestFusedScore:
    def test_default_weights(self) -> None:
        assert fused_score(1.0, 0.0) == pytest.approx(0.7)

    def test_all_one_returns_one(self) -> None:
        assert fused_score(1.0, 1.0) == pytest.approx(1.0)

    def test_custom_weights(self) -> None:
        assert fused_score(0.9, 0.5, dense_weight=0.5, sparse_weight=0.5) == pytest.approx(0.7)


class TestR1bDisambiguationScenarios:
    def test_annual_vs_monthly_refund_policy_separates(self) -> None:
        a_feat = extract_features("What is the refund policy for enterprise ANNUAL plans?")
        b_feat = extract_features("What is the refund policy for monthly SELFSERVE plans?")
        assert jaccard_overlap(a_feat, b_feat) < 0.7

    def test_q3_vs_q4_revenue_separates(self) -> None:
        q3_feat = extract_features("What was revenue in Q3 2025?")
        q4_feat = extract_features("What was revenue in Q4 2025?")
        assert jaccard_overlap(q3_feat, q4_feat) < 1.0
        assert "q3" in q3_feat and "q4" in q4_feat

    def test_okta_vs_auth0_mfa_separates(self) -> None:
        okta_feat = extract_features("How do I reset Okta MFA?")
        auth0_feat = extract_features("How do I reset Auth0 MFA?")
        assert jaccard_overlap(okta_feat, auth0_feat) < 0.7
        assert "okta" in okta_feat
        assert "auth0" in auth0_feat

    def test_identical_queries_fully_overlap(self) -> None:
        q = "What was revenue in Q3 2025 for OKTA?"
        assert jaccard_overlap(extract_features(q), extract_features(q)) == pytest.approx(1.0)


class TestFusedScoreRejectsAnnualVsMonthly:
    def test_high_cosine_low_jaccard_fused_score_below_threshold(self) -> None:
        fused = fused_score(0.96, 0.33)
        assert fused < 0.88, f"expected reject, got fused={fused:.3f}"

    def test_high_cosine_high_jaccard_fused_score_accepts(self) -> None:
        fused = fused_score(0.97, 0.9)
        assert fused >= 0.88, f"expected accept, got fused={fused:.3f}"
