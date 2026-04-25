"""Tests for L0_routing.config.routing_calibration module."""

from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing.config import routing_calibration


class TestRoutingCalibration:
    """Test suite for routing calibration threshold loader."""

    def setup_method(self):
        """Reset cache before each test."""
        routing_calibration.reset_cache()

    def test_get_abstain_threshold_default(self):
        """Test get_abstain_threshold returns default when no config."""
        threshold = routing_calibration.get_abstain_threshold()
        assert isinstance(threshold, float)
        assert 0.0 <= threshold <= 1.0
        assert threshold == 0.50  # Fallback value

    def test_get_abstain_threshold_env_override(self):
        """Test get_abstain_threshold respects env override."""
        with patch.dict("os.environ", {"AGENTIC_ABSTAIN_THRESHOLD": "0.75"}):
            threshold = routing_calibration.get_abstain_threshold()
            assert threshold == 0.75

    def test_get_abstain_threshold_env_invalid(self):
        """Test get_abstain_threshold falls back on invalid env value."""
        with patch.dict("os.environ", {"AGENTIC_ABSTAIN_THRESHOLD": "invalid"}):
            threshold = routing_calibration.get_abstain_threshold()
            assert threshold == 0.50  # Fallback

    def test_get_similarity_threshold_default(self):
        """Test get_similarity_threshold returns default when no config."""
        threshold = routing_calibration.get_similarity_threshold()
        assert isinstance(threshold, float)
        assert 0.0 <= threshold <= 1.0
        assert threshold == 0.98  # Fallback value

    def test_get_similarity_threshold_env_override(self):
        """Test get_similarity_threshold respects env override."""
        with patch.dict("os.environ", {"AGENTIC_SIMILARITY_THRESHOLD": "0.95"}):
            threshold = routing_calibration.get_similarity_threshold()
            assert threshold == 0.95

    def test_get_similarity_threshold_with_namespace(self):
        """Test get_similarity_threshold with namespace parameter."""
        threshold = routing_calibration.get_similarity_threshold(namespace="test_namespace")
        assert isinstance(threshold, float)
        assert 0.0 <= threshold <= 1.0

    def test_get_v12_threshold_default(self):
        """Test get_v12_threshold returns default for known thresholds."""
        threshold = routing_calibration.get_v12_threshold("classifier_surface_threshold")
        assert threshold == 0.72

    def test_get_v12_threshold_env_override(self):
        """Test get_v12_threshold respects env override."""
        with patch.dict("os.environ", {"AGENTIC_V12_CLASSIFIER_SURFACE_THRESHOLD": "0.85"}):
            threshold = routing_calibration.get_v12_threshold("classifier_surface_threshold")
            assert threshold == 0.85

    def test_get_v12_threshold_unknown(self):
        """Test get_v12_threshold raises KeyError for unknown threshold."""
        with pytest.raises(KeyError, match="unknown v12 routing threshold"):
            routing_calibration.get_v12_threshold("unknown_threshold")

    def test_get_v12_int_default(self):
        """Test get_v12_int returns default for known int params."""
        value = routing_calibration.get_v12_int("min_spans_for_loop_guard")
        assert value == 5

    def test_get_v12_int_env_override(self):
        """Test get_v12_int respects env override."""
        with patch.dict("os.environ", {"AGENTIC_V12_MIN_SPANS_FOR_LOOP_GUARD": "10"}):
            value = routing_calibration.get_v12_int("min_spans_for_loop_guard")
            assert value == 10

    def test_get_v12_int_unknown(self):
        """Test get_v12_int raises KeyError for unknown param."""
        with pytest.raises(KeyError, match="unknown v12 routing int param"):
            routing_calibration.get_v12_int("unknown_param")

    def test_coerce_threshold_valid_int(self):
        """Test _coerce_threshold accepts valid int."""
        assert routing_calibration._coerce_threshold(75, 0.50) == 0.75

    def test_coerce_threshold_valid_float(self):
        """Test _coerce_threshold accepts valid float."""
        assert routing_calibration._coerce_threshold(0.85, 0.50) == 0.85

    def test_coerce_threshold_valid_string(self):
        """Test _coerce_threshold accepts valid string."""
        assert routing_calibration._coerce_threshold("0.90", 0.50) == 0.90

    def test_coerce_threshold_scientific_notation(self):
        """Test _coerce_threshold accepts scientific notation."""
        assert routing_calibration._coerce_threshold("1e-2", 0.50) == 0.01

    def test_coerce_threshold_bool_rejected(self):
        """Test _coerce_threshold rejects bool (returns fallback)."""
        assert routing_calibration._coerce_threshold(True, 0.50) == 0.50
        assert routing_calibration._coerce_threshold(False, 0.50) == 0.50

    def test_coerce_threshold_nan_rejected(self):
        """Test _coerce_threshold rejects NaN (returns fallback)."""
        import math

        assert routing_calibration._coerce_threshold(float("nan"), 0.50) == 0.50

    def test_coerce_threshold_inf_rejected(self):
        """Test _coerce_threshold rejects infinity (returns fallback)."""
        import math

        assert routing_calibration._coerce_threshold(float("inf"), 0.50) == 0.50
        assert routing_calibration._coerce_threshold(float("-inf"), 0.50) == 0.50

    def test_coerce_threshold_out_of_range_low(self):
        """Test _coerce_threshold rejects values < 0 (returns fallback)."""
        assert routing_calibration._coerce_threshold(-0.5, 0.50) == 0.50

    def test_coerce_threshold_out_of_range_high(self):
        """Test _coerce_threshold rejects values > 1 (returns fallback)."""
        assert routing_calibration._coerce_threshold(1.5, 0.50) == 0.50

    def test_coerce_threshold_empty_string(self):
        """Test _coerce_threshold rejects empty string (returns fallback)."""
        assert routing_calibration._coerce_threshold("", 0.50) == 0.50

    def test_coerce_threshold_invalid_string(self):
        """Test _coerce_threshold rejects invalid string (returns fallback)."""
        assert routing_calibration._coerce_threshold("invalid", 0.50) == 0.50

    def test_coerce_positive_int_valid(self):
        """Test _coerce_positive_int accepts valid int."""
        assert routing_calibration._coerce_positive_int(10, 5) == 10

    def test_coerce_positive_int_valid_float_integer(self):
        """Test _coerce_positive_int accepts float that is integer."""
        assert routing_calibration._coerce_positive_int(10.0, 5) == 10

    def test_coerce_positive_int_valid_string(self):
        """Test _coerce_positive_int accepts valid string."""
        assert routing_calibration._coerce_positive_int("15", 5) == 15

    def test_coerce_positive_int_bool_rejected(self):
        """Test _coerce_positive_int rejects bool (returns fallback)."""
        assert routing_calibration._coerce_positive_int(True, 5) == 5
        assert routing_calibration._coerce_positive_int(False, 5) == 5

    def test_coerce_positive_int_float_fractional_rejected(self):
        """Test _coerce_positive_int rejects float with fractional part."""
        assert routing_calibration._coerce_positive_int(10.5, 5) == 5

    def test_coerce_positive_int_zero_rejected(self):
        """Test _coerce_positive_int rejects zero (returns fallback)."""
        assert routing_calibration._coerce_positive_int(0, 5) == 5

    def test_coerce_positive_int_negative_rejected(self):
        """Test _coerce_positive_int rejects negative (returns fallback)."""
        assert routing_calibration._coerce_positive_int(-5, 5) == 5

    def test_coerce_positive_int_empty_string(self):
        """Test _coerce_positive_int rejects empty string (returns fallback)."""
        assert routing_calibration._coerce_positive_int("", 5) == 5

    def test_coerce_positive_int_invalid_string(self):
        """Test _coerce_positive_int rejects invalid string (returns fallback)."""
        assert routing_calibration._coerce_positive_int("invalid", 5) == 5

    def test_reset_cache(self):
        """Test reset_cache clears the YAML cache."""
        # Load once to populate cache
        routing_calibration._load_yaml()
        # Reset
        routing_calibration.reset_cache()
        # Cache should be cleared (we can't directly test this, but we can call it)
        assert routing_calibration.reset_cache() is None

    def test_public_api_exports(self):
        """Test that public API functions are exported."""
        assert hasattr(routing_calibration, "get_abstain_threshold")
        assert hasattr(routing_calibration, "get_similarity_threshold")
        assert hasattr(routing_calibration, "get_v12_threshold")
        assert hasattr(routing_calibration, "get_v12_int")
        assert hasattr(routing_calibration, "reset_cache")
