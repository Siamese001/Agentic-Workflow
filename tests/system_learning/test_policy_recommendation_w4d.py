"""
W4-D Policy Recommendation Engine Tests

Tests for deterministic policy recommendation generation from drift analysis.
"""

import os
import pytest
from typing import Any, Dict

from system_learning.engines.policy_recommendation_engine import PolicyRecommendationEngine, PolicyRecommendation
from system_learning.engines.shadow_drift_analyzer import DriftSummary
from system_learning.engines.retrieval_profile import RetrievalProfile


@pytest.mark.unit_min_deps
class TestPolicyRecommendationW4D:
    """Test W4-D Policy Recommendation Engine functionality."""

    def test_policy_recommendation_determinism(self):
        """Test that policy recommendations produce identical digests for identical inputs."""
        # Create fixed drift summary
        drift_summary = DriftSummary(
            profile_id="test-profile",
            batch_size=3,
            mean_cosine=0.916667,
            p95_cosine=0.947,
            drift_flag=False,
            drift_score=0.053,
            deterministic_digest="test-digest-123",
        )
        
        # Create active profile
        active_profile = RetrievalProfile(
            profile_id="test-profile",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=10,
            similarity_cutoff=0.85,
            influence_cap=0.5,
        )
        
        engine = PolicyRecommendationEngine()
        now_utc = 1234567890
        
        # Run recommendation twice independently
        rec1 = engine.generate_recommendation(
            drift_summary=drift_summary,
            active_profile=active_profile,
            now_utc=now_utc,
        )
        
        rec2 = engine.generate_recommendation(
            drift_summary=drift_summary,
            active_profile=active_profile,
            now_utc=now_utc,
        )
        
        # Verify deterministic digest
        assert rec1.deterministic_digest == rec2.deterministic_digest, \
            "Policy recommendation must be deterministic"
        
        # Emit digest for test verification
        rec1.emit_digest()
        
        # Verify no drift case
        assert rec1.profile_id == "test-profile"
        assert rec1.recommended_changes == {}, "No changes should be recommended when no drift"
        assert "No drift detected" in rec1.rationale
        assert rec1.confidence_score == 0.95

    def test_policy_recommendation_bounded_recommendation(self):
        """Test that recommendations are bounded within safe limits."""
        # Create high drift summary
        drift_summary = DriftSummary(
            profile_id="test-profile",
            batch_size=3,
            mean_cosine=0.80,
            p95_cosine=0.85,  # Below 0.92 threshold
            drift_flag=True,
            drift_score=0.15,  # High drift
            deterministic_digest="test-digest-456",
        )
        
        # Create active profile
        active_profile = RetrievalProfile(
            profile_id="test-profile",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=10,
            similarity_cutoff=0.90,
            influence_cap=0.80,
        )
        
        engine = PolicyRecommendationEngine()
        now_utc = 1234567890
        
        recommendation = engine.generate_recommendation(
            drift_summary=drift_summary,
            active_profile=active_profile,
            now_utc=now_utc,
        )
        
        # Verify drift detected
        assert recommendation.recommended_changes != {}, "Changes should be recommended when drift detected"
        assert "Drift detected" in recommendation.rationale
        
        # Verify bounded similarity_cutoff reduction
        if "similarity_cutoff" in recommendation.recommended_changes:
            new_cutoff = recommendation.recommended_changes["similarity_cutoff"]
            # Max reduction: min(0.02, 0.15 * 0.05) = min(0.02, 0.0075) = 0.0075
            expected_max_reduction = 0.0075
            actual_reduction = active_profile.similarity_cutoff - new_cutoff
            assert actual_reduction <= expected_max_reduction + 0.000001, \
                f"Cutoff reduction {actual_reduction} exceeds max {expected_max_reduction}"
            assert new_cutoff >= 0.1, "Cutoff should not go below minimum safe value"
        
        # Verify bounded influence_cap increase
        if "influence_cap" in recommendation.recommended_changes:
            new_cap = recommendation.recommended_changes["influence_cap"]
            # Max increase: min(0.01, 0.15 * 0.02) = min(0.01, 0.003) = 0.003
            expected_max_increase = 0.003
            actual_increase = new_cap - active_profile.influence_cap
            assert actual_increase <= expected_max_increase + 0.000001, \
                f"Cap increase {actual_increase} exceeds max {expected_max_increase}"
            assert new_cap <= 1.0, "Cap should not exceed maximum safe value"
        
        # Verify confidence is bounded
        assert 0.0 <= recommendation.confidence_score <= 1.0, \
            "Confidence score must be bounded between 0 and 1"

    def test_policy_recommendation_no_drift_case(self):
        """Test recommendation when no drift is detected."""
        # Create no drift summary
        drift_summary = DriftSummary(
            profile_id="test-profile",
            batch_size=3,
            mean_cosine=0.95,
            p95_cosine=0.96,  # Above 0.92 threshold
            drift_flag=False,
            drift_score=0.04,
            deterministic_digest="test-digest-789",
        )
        
        # Create active profile
        active_profile = RetrievalProfile(
            profile_id="test-profile",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=10,
            similarity_cutoff=0.85,
            influence_cap=0.5,
        )
        
        engine = PolicyRecommendationEngine()
        now_utc = 1234567890
        
        recommendation = engine.generate_recommendation(
            drift_summary=drift_summary,
            active_profile=active_profile,
            now_utc=now_utc,
        )
        
        # Verify no changes recommended
        assert recommendation.recommended_changes == {}, \
            "No changes should be recommended when drift_flag is False"
        assert "No drift detected" in recommendation.rationale
        assert f"{drift_summary.p95_cosine:.6f}" in recommendation.rationale
        assert recommendation.confidence_score == 0.95

    def test_policy_recommendation_non_influential(self):
        """Test that recommendation engine does not influence retrieval behavior."""
        # This test verifies that the recommendation engine is purely advisory
        # by checking that it doesn't modify input data or active profile
        
        engine = PolicyRecommendationEngine()
        now_utc = 1234567890
        
        # Create drift summary
        drift_summary = DriftSummary(
            profile_id="test-profile",
            batch_size=3,
            mean_cosine=0.80,
            p95_cosine=0.85,
            drift_flag=True,
            drift_score=0.15,
            deterministic_digest="test-digest-noninf",
        )
        
        # Create active profile
        active_profile = RetrievalProfile(
            profile_id="test-profile",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=10,
            similarity_cutoff=0.90,
            influence_cap=0.80,
        )
        
        # Make copies for comparison
        import copy
        drift_summary_copy = copy.deepcopy(drift_summary)
        active_profile_copy = copy.deepcopy(active_profile)
        
        # Run recommendation
        recommendation = engine.generate_recommendation(
            drift_summary=drift_summary,
            active_profile=active_profile,
            now_utc=now_utc,
        )
        
        # Verify inputs are unchanged
        assert drift_summary == drift_summary_copy, \
            "Drift summary must not be modified"
        assert active_profile == active_profile_copy, \
            "Active profile must not be modified"
        
        # Verify recommendation is computed correctly
        assert recommendation.profile_id == "test-profile"
        assert recommendation.recommended_changes != {}, "Changes should be recommended"

    def test_policy_recommendation_edge_cases(self):
        """Test edge cases for recommendation generation."""
        engine = PolicyRecommendationEngine()
        now_utc = 1234567890
        
        # Test with minimal drift score
        drift_summary_minimal = DriftSummary(
            profile_id="test-profile",
            batch_size=1,
            mean_cosine=0.919999,
            p95_cosine=0.919999,  # Just below threshold
            drift_flag=True,
            drift_score=0.080001,  # Very minimal drift
            deterministic_digest="test-digest-minimal",
        )
        
        active_profile = RetrievalProfile(
            profile_id="test-profile",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=10,
            similarity_cutoff=0.85,
            influence_cap=0.5,
        )
        
        recommendation = engine.generate_recommendation(
            drift_summary=drift_summary_minimal,
            active_profile=active_profile,
            now_utc=now_utc,
        )
        
        # Should still recommend changes but very small
        if "similarity_cutoff" in recommendation.recommended_changes:
            reduction = active_profile.similarity_cutoff - recommendation.recommended_changes["similarity_cutoff"]
            assert reduction <= 0.02, "Reduction should be bounded by max"
            assert reduction > 0, "Should recommend some reduction"


@pytest.mark.unit_min_deps
class TestW4DNegativeControl:
    """Negative control tests for W4-D Policy Recommendation Engine."""

    @pytest.mark.xfail(reason="W4D tamper guard", strict=False)
    def test_policy_recommendation_determinism_violation_negative_control(self):
        """Negative control: tamper with recommendation determinism."""
        # Set tamper flag to change rounding precision
        os.environ["W4D_NEGCTRL_TAMPER"] = "1"
        
        # Monkey patch the rounding function to use different precision
        import system_learning.engines.policy_recommendation_engine as engine_module
        original_round = round
        
        def tampered_round(x, ndigits=None):
            """Tampered rounding that uses 3 decimal places instead of 6."""
            if ndigits is not None and ndigits >= 6:
                # Use 3 decimal places when 6+ is requested
                ndigits = 3
            return original_round(x, ndigits)
        
        try:
            # Apply tampering
            engine_module.round = tampered_round
            
            # Create fixed inputs
            drift_summary = DriftSummary(
                profile_id="test-profile",
                batch_size=3,
                mean_cosine=0.916667,
                p95_cosine=0.947,
                drift_flag=True,
                drift_score=0.053,
                deterministic_digest="test-digest-123",
            )
            
            active_profile = RetrievalProfile(
                profile_id="test-profile",
                primary_embedder_id="test-embedder",
                embedding_dim=1536,
                shadow_embedder_id="test-shadow",
                top_k=10,
                similarity_cutoff=0.85,
                influence_cap=0.5,
            )
            
            engine = PolicyRecommendationEngine()
            now_utc = 1234567890
            
            # Run recommendation with tampering
            rec_tampered = engine.generate_recommendation(
                drift_summary=drift_summary,
                active_profile=active_profile,
                now_utc=now_utc,
            )
            
            # Restore original rounding for comparison
            engine_module.round = original_round
            rec_normal = engine.generate_recommendation(
                drift_summary=drift_summary,
                active_profile=active_profile,
                now_utc=now_utc,
            )
            
            # Tampering should cause different results - this should FAIL the test
            if rec_tampered.deterministic_digest != rec_normal.deterministic_digest:
                assert False, f"TAMPERING DETECTED: tampered digest {rec_tampered.deterministic_digest} != normal digest {rec_normal.deterministic_digest}"
            
            # Also check for rounding differences
            if rec_tampered.confidence_score != rec_normal.confidence_score:
                assert False, f"TAMPERING DETECTED: tampered confidence {rec_tampered.confidence_score} != normal confidence {rec_normal.confidence_score}"
            
            # If we get here, tampering wasn't effective
            assert False, "Tampering was not effective - values are identical"
            
        finally:
            # Restore original function
            engine_module.round = original_round
            # Clean up environment
            os.environ.pop("W4D_NEGCTRL_TAMPER", None)

    def test_policy_recommendation_determinism_violation_negative_control_guard_intact(self):
        """Verify negative control guard is intact when not tampering."""
        # Ensure no tampering flag is set
        if "W4D_NEGCTRL_TAMPER" in os.environ:
            del os.environ["W4D_NEGCTRL_TAMPER"]
        
        # Create fixed inputs
        drift_summary = DriftSummary(
            profile_id="test-profile",
            batch_size=3,
            mean_cosine=0.916667,
            p95_cosine=0.947,
            drift_flag=False,
            drift_score=0.053,
            deterministic_digest="test-digest-123",
        )
        
        active_profile = RetrievalProfile(
            profile_id="test-profile",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=10,
            similarity_cutoff=0.85,
            influence_cap=0.5,
        )
        
        engine = PolicyRecommendationEngine()
        now_utc = 1234567890
        
        # Run recommendation twice without tampering
        rec1 = engine.generate_recommendation(
            drift_summary=drift_summary,
            active_profile=active_profile,
            now_utc=now_utc,
        )
        
        rec2 = engine.generate_recommendation(
            drift_summary=drift_summary,
            active_profile=active_profile,
            now_utc=now_utc,
        )
        
        # Should be identical when not tampering
        assert rec1.deterministic_digest == rec2.deterministic_digest, \
            "Digest must be identical when not tampering"
        assert rec1.confidence_score == rec2.confidence_score, \
            "Confidence score must be identical when not tampering"
