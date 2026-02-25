"""
W4-C Shadow Drift Analyzer Tests

Tests for deterministic drift analysis and informational-only L4 state writing.
"""

import os
import pytest
from typing import Any, Dict, List

from system_learning.engines.shadow_drift_analyzer import ShadowDriftAnalyzer, DriftSummary
from system_learning.engines.retrieval_profile import RetrievalProfile
from system_learning.engines.retrieval_profile_manager import get_retrieval_profile_manager


@pytest.mark.unit_min_deps
class TestShadowDriftW4C:
    """Test W4-C Shadow Drift Analyzer functionality."""

    def test_shadow_drift_determinism(self):
        """Test that drift analysis produces identical digests for identical inputs."""
        # Create fixed shadow telemetry input
        shadow_records = [
            {
                "shadow_embedder_id": "test-shadow-embedder",
                "primary_embedding_norm": 1.000000,
                "shadow_embedding_norm": 1.000000,
                "primary_shadow_cosine": 0.950000,
            },
            {
                "shadow_embedder_id": "test-shadow-embedder",
                "primary_embedding_norm": 1.000000,
                "shadow_embedding_norm": 1.000000,
                "primary_shadow_cosine": 0.920000,
            },
            {
                "shadow_embedder_id": "test-shadow-embedder",
                "primary_embedding_norm": 1.000000,
                "shadow_embedding_norm": 1.000000,
                "primary_shadow_cosine": 0.880000,
            },
        ]
        
        analyzer = ShadowDriftAnalyzer()
        now_utc = 1234567890
        profile_id = "test-profile"
        
        # Run analysis twice independently
        summary1 = analyzer.analyze_batch(
            shadow_records=shadow_records,
            profile_id=profile_id,
            now_utc=now_utc,
        )
        
        summary2 = analyzer.analyze_batch(
            shadow_records=shadow_records,
            profile_id=profile_id,
            now_utc=now_utc,
        )
        
        # Verify deterministic digest
        assert summary1.deterministic_digest == summary2.deterministic_digest, \
            "Drift analysis must be deterministic"
        
        # Emit digest for test verification
        summary1.emit_digest()
        
        # Verify expected values
        assert summary1.profile_id == profile_id
        assert summary1.batch_size == 3
        assert summary1.mean_cosine == round((0.95 + 0.92 + 0.88) / 3, 6)
        # 95th percentile with linear interpolation: index = 0.95 * (3-1) = 1.9
        # value = 0.92 + 0.9 * (0.95 - 0.92) = 0.92 + 0.027 = 0.947
        assert summary1.p95_cosine == round(0.92 + 0.9 * (0.95 - 0.92), 6)
        assert summary1.drift_flag == False  # p95_cosine >= 0.92
        assert summary1.drift_score == round(1.0 - summary1.p95_cosine, 6)

    def test_shadow_drift_threshold_detection(self):
        """Test drift flag threshold logic."""
        analyzer = ShadowDriftAnalyzer()
        now_utc = 1234567890
        profile_id = "test-profile"
        
        # Test high cosine (no drift)
        high_cosine_records = [
            {"shadow_embedder_id": "test", "primary_shadow_cosine": 0.95},
            {"shadow_embedder_id": "test", "primary_shadow_cosine": 0.93},
            {"shadow_embedder_id": "test", "primary_shadow_cosine": 0.94},
        ]
        
        summary_high = analyzer.analyze_batch(
            shadow_records=high_cosine_records,
            profile_id=profile_id,
            now_utc=now_utc,
        )
        
        assert summary_high.drift_flag == False
        assert summary_high.drift_score < 0.08  # 1 - 0.95 = 0.05, 1 - 0.93 = 0.07
        
        # Test low cosine (drift detected)
        low_cosine_records = [
            {"shadow_embedder_id": "test", "primary_shadow_cosine": 0.85},
            {"shadow_embedder_id": "test", "primary_shadow_cosine": 0.87},
            {"shadow_embedder_id": "test", "primary_shadow_cosine": 0.86},
        ]
        
        summary_low = analyzer.analyze_batch(
            shadow_records=low_cosine_records,
            profile_id=profile_id,
            now_utc=now_utc,
        )
        
        assert summary_low.drift_flag == True
        assert summary_low.drift_score > 0.13  # 1 - 0.87 = 0.13, 1 - 0.85 = 0.15

    def test_shadow_drift_non_influential(self):
        """Test that drift analyzer does not influence retrieval behavior."""
        # This test verifies that the drift analyzer is purely informational
        # by checking that it doesn't modify input data
        
        analyzer = ShadowDriftAnalyzer()
        now_utc = 1234567890
        profile_id = "test-profile"
        
        # Create input records
        original_records = [
            {"shadow_embedder_id": "test", "primary_shadow_cosine": 0.90},
            {"shadow_embedder_id": "test", "primary_shadow_cosine": 0.85},
        ]
        
        # Make a copy for comparison
        import copy
        records_copy = copy.deepcopy(original_records)
        
        # Run analysis
        summary = analyzer.analyze_batch(
            shadow_records=original_records,
            profile_id=profile_id,
            now_utc=now_utc,
        )
        
        # Verify input records are unchanged
        assert original_records == records_copy, \
            "Drift analyzer must not modify input records"
        
        # Verify summary is computed correctly
        assert summary.profile_id == profile_id
        assert summary.batch_size == 2
        assert summary.drift_flag == True  # p95 = 0.90 < 0.92

    def test_shadow_drift_empty_batch(self):
        """Test drift analysis with empty batch."""
        analyzer = ShadowDriftAnalyzer()
        
        summary = analyzer.analyze_batch(
            shadow_records=[],
            profile_id="test-profile",
            now_utc=1234567890,
        )
        
        assert summary.profile_id == "test-profile"
        assert summary.batch_size == 0
        assert summary.mean_cosine == 1.0
        assert summary.p95_cosine == 1.0
        assert summary.drift_flag == False
        assert summary.drift_score == 0.0
        assert summary.deterministic_digest is not None

    def test_shadow_drift_no_cosine_data(self):
        """Test drift analysis with records but no cosine data."""
        analyzer = ShadowDriftAnalyzer()
        
        records_without_cosine = [
            {"shadow_embedder_id": "test", "primary_embedding_norm": 1.0},
            {"shadow_embedder_id": "test", "shadow_embedding_norm": 1.0},
        ]
        
        summary = analyzer.analyze_batch(
            shadow_records=records_without_cosine,
            profile_id="test-profile",
            now_utc=1234567890,
        )
        
        assert summary.profile_id == "test-profile"
        assert summary.batch_size == 2
        assert summary.mean_cosine == 1.0
        assert summary.p95_cosine == 1.0
        assert summary.drift_flag == False
        assert summary.drift_score == 0.0


@pytest.mark.unit_min_deps
class TestW4CNegativeControl:
    """Negative control tests for W4-C Shadow Drift Analyzer."""

    @pytest.mark.xfail(reason="W4C tamper guard", strict=False)
    def test_shadow_drift_determinism_violation_negative_control(self):
        """Negative control: tamper with drift analysis determinism."""
        # Set tamper flag to change rounding precision
        os.environ["W4C_NEGCTRL_TAMPER"] = "1"
        
        # Monkey patch the rounding function to use different precision
        import system_learning.engines.shadow_drift_analyzer as analyzer_module
        original_round = round
        
        def tampered_round(x, ndigits=None):
            """Tampered rounding that uses 3 decimal places instead of 6."""
            if ndigits is not None and ndigits >= 6:
                # Use 3 decimal places when 6+ is requested
                ndigits = 3
            return original_round(x, ndigits)
        
        try:
            # Apply tampering
            analyzer_module.round = tampered_round
            
            # Create fixed shadow telemetry input
            shadow_records = [
                {
                    "shadow_embedder_id": "test-shadow-embedder",
                    "primary_embedding_norm": 1.000000,
                    "shadow_embedding_norm": 1.000000,
                    "primary_shadow_cosine": 0.950123,  # Will be rounded to 3 decimals
                },
                {
                    "shadow_embedder_id": "test-shadow-embedder",
                    "primary_embedding_norm": 1.000000,
                    "shadow_embedding_norm": 1.000000,
                    "primary_shadow_cosine": 0.920456,  # Will be rounded to 3 decimals
                },
            ]
            
            analyzer = ShadowDriftAnalyzer()
            now_utc = 1234567890
            profile_id = "test-profile"
            
            # Run analysis with tampering
            summary_tampered = analyzer.analyze_batch(
                shadow_records=shadow_records,
                profile_id=profile_id,
                now_utc=now_utc,
            )
            
            # Restore original rounding for comparison
            analyzer_module.round = original_round
            summary_normal = analyzer.analyze_batch(
                shadow_records=shadow_records,
                profile_id=profile_id,
                now_utc=now_utc,
            )
            
            # Tampering should cause different results - this should FAIL the test
            if summary_tampered.deterministic_digest != summary_normal.deterministic_digest:
                assert False, f"TAMPERING DETECTED: tampered digest {summary_tampered.deterministic_digest} != normal digest {summary_normal.deterministic_digest}"
            
            # Also check for rounding differences
            if summary_tampered.mean_cosine != summary_normal.mean_cosine:
                assert False, f"TAMPERING DETECTED: tampered mean {summary_tampered.mean_cosine} != normal mean {summary_normal.mean_cosine}"
            
            # If we get here, tampering wasn't effective
            assert False, "Tampering was not effective - values are identical"
            
        finally:
            # Restore original function
            analyzer_module.round = original_round
            # Clean up environment
            os.environ.pop("W4C_NEGCTRL_TAMPER", None)

    def test_shadow_drift_determinism_violation_negative_control_guard_intact(self):
        """Verify negative control guard is intact when not tampering."""
        # Ensure no tampering flag is set
        if "W4C_NEGCTRL_TAMPER" in os.environ:
            del os.environ["W4C_NEGCTRL_TAMPER"]
        
        # Create fixed shadow telemetry input
        shadow_records = [
            {
                "shadow_embedder_id": "test-shadow-embedder",
                "primary_embedding_norm": 1.000000,
                "shadow_embedding_norm": 1.000000,
                "primary_shadow_cosine": 0.950000,
            },
            {
                "shadow_embedder_id": "test-shadow-embedder",
                "primary_embedding_norm": 1.000000,
                "shadow_embedding_norm": 1.000000,
                "primary_shadow_cosine": 0.920000,
            },
        ]
        
        analyzer = ShadowDriftAnalyzer()
        now_utc = 1234567890
        profile_id = "test-profile"
        
        # Run analysis twice without tampering
        summary1 = analyzer.analyze_batch(
            shadow_records=shadow_records,
            profile_id=profile_id,
            now_utc=now_utc,
        )
        
        summary2 = analyzer.analyze_batch(
            shadow_records=shadow_records,
            profile_id=profile_id,
            now_utc=now_utc,
        )
        
        # Should be identical when not tampering
        assert summary1.deterministic_digest == summary2.deterministic_digest, \
            "Digest must be identical when not tampering"
        assert summary1.mean_cosine == summary2.mean_cosine, \
            "Mean cosine must be identical when not tampering"
