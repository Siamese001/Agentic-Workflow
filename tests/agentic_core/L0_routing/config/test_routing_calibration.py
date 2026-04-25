"""Tests for routing_calibration.py module."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from agentic_core.L0_routing.config.routing_calibration import (
    get_abstain_threshold,
    get_similarity_threshold,
    get_v12_threshold,
    get_v12_int,
    reset_cache,
    _coerce_threshold,
    _coerce_positive_int,
)


class TestCoerceThreshold:
    """Tests for _coerce_threshold function."""

    def test_coerce_threshold_int(self):
        """Test _coerce_threshold with int input."""
        assert _coerce_threshold(5, 0.5) == 0.5

    def test_coerce_threshold_float(self):
        """Test _coerce_threshold with float input."""
        assert _coerce_threshold(0.75, 0.5) == 0.75

    def test_coerce_threshold_string(self):
        """Test _coerce_threshold with string input."""
        assert _coerce_threshold("0.75", 0.5) == 0.75

    def test_coerce_threshold_string_whitespace(self):
        """Test _coerce_threshold with string containing whitespace."""
        assert _coerce_threshold(" 0.75 ", 0.5) == 0.75

    def test_coerce_threshold_string_scientific(self):
        """Test _coerce_threshold with scientific notation."""
        assert _coerce_threshold("1e-2", 0.5) == 0.01

    def test_coerce_threshold_bool_rejected(self):
        """Test _coerce_threshold rejects bool."""
        assert _coerce_threshold(True, 0.5) == 0.5
        assert _coerce_threshold(False, 0.5) == 0.5

    def test_coerce_threshold_nan(self):
        """Test _coerce_threshold rejects NaN."""
        assert _coerce_threshold(float("nan"), 0.5) == 0.5

    def test_coerce_threshold_inf(self):
        """Test _coerce_threshold rejects infinity."""
        assert _coerce_threshold(float("inf"), 0.5) == 0.5
        assert _coerce_threshold(float("-inf"), 0.5) == 0.5

    def test_coerce_threshold_out_of_range_high(self):
        """Test _coerce_threshold rejects values > 1.0."""
        assert _coerce_threshold(1.5, 0.5) == 0.5

    def test_coerce_threshold_out_of_range_low(self):
        """Test _coerce_threshold rejects values < 0.0."""
        assert _coerce_threshold(-0.1, 0.5) == 0.5

    def test_coerce_threshold_invalid_string(self):
        """Test _coerce_threshold rejects invalid string."""
        assert _coerce_threshold("invalid", 0.5) == 0.5

    def test_coerce_threshold_empty_string(self):
        """Test _coerce_threshold rejects empty string."""
        assert _coerce_threshold("", 0.5) == 0.5

    def test_coerce_threshold_invalid_type(self):
        """Test _coerce_threshold rejects invalid types."""
        assert _coerce_threshold([], 0.5) == 0.5
        assert _coerce_threshold({}, 0.5) == 0.5

    def test_coerce_threshold_boundary_0(self):
        """Test _coerce_threshold accepts 0.0."""
        assert _coerce_threshold(0.0, 0.5) == 0.0

    def test_coerce_threshold_boundary_1(self):
        """Test _coerce_threshold accepts 1.0."""
        assert _coerce_threshold(1.0, 0.5) == 1.0


class TestCoercePositiveInt:
    """Tests for _coerce_positive_int function."""

    def test_coerce_positive_int_int(self):
        """Test _coerce_positive_int with int input."""
        assert _coerce_positive_int(5, 10) == 5

    def test_coerce_positive_int_float_integer(self):
        """Test _coerce_positive_int with float that is an integer."""
        assert _coerce_positive_int(5.0, 10) == 5

    def test_coerce_positive_int_float_fractional(self):
        """Test _coerce_positive_int rejects float with fractional part."""
        assert _coerce_positive_int(5.5, 10) == 10

    def test_coerce_positive_int_string(self):
        """Test _coerce_positive_int with string input."""
        assert _coerce_positive_int("5", 10) == 5

    def test_coerce_positive_int_string_whitespace(self):
        """Test _coerce_positive_int with string containing whitespace."""
        assert _coerce_positive_int(" 5 ", 10) == 5

    def test_coerce_positive_int_bool_rejected(self):
        """Test _coerce_positive_int rejects bool."""
        assert _coerce_positive_int(True, 10) == 10
        assert _coerce_positive_int(False, 10) == 10

    def test_coerce_positive_int_zero_rejected(self):
        """Test _coerce_positive_int rejects zero."""
        assert _coerce_positive_int(0, 10) == 10

    def test_coerce_positive_int_negative_rejected(self):
        """Test _coerce_positive_int rejects negative values."""
        assert _coerce_positive_int(-1, 10) == 10

    def test_coerce_positive_int_invalid_string(self):
        """Test _coerce_positive_int rejects invalid string."""
        assert _coerce_positive_int("invalid", 10) == 10

    def test_coerce_positive_int_empty_string(self):
        """Test _coerce_positive_int rejects empty string."""
        assert _coerce_positive_int("", 10) == 10

    def test_coerce_positive_int_invalid_type(self):
        """Test _coerce_positive_int rejects invalid types."""
        assert _coerce_positive_int([], 10) == 10
        assert _coerce_positive_int({}, 10) == 10


class TestGetAbstainThreshold:
    """Tests for get_abstain_threshold function."""

    def test_get_abstain_threshold_env_override(self):
        """Test get_abstain_threshold with env override."""
        with patch.dict("os.environ", {"AGENTIC_ABSTAIN_THRESHOLD": "0.75"}, clear=True):
            assert get_abstain_threshold() == 0.75

    def test_get_abstain_threshold_env_invalid(self):
        """Test get_abstain_threshold with invalid env uses fallback."""
        with patch.dict("os.environ", {"AGENTIC_ABSTAIN_THRESHOLD": "invalid"}, clear=True):
            # Should use fallback when env is invalid
            result = get_abstain_threshold()
            assert isinstance(result, float)

    def test_get_abstain_threshold_env_out_of_range(self):
        """Test get_abstain_threshold with env out of range uses fallback."""
        with patch.dict("os.environ", {"AGENTIC_ABSTAIN_THRESHOLD": "1.5"}, clear=True):
            result = get_abstain_threshold()
            assert isinstance(result, float)

    def test_get_abstain_threshold_yaml_override(self):
        """Test get_abstain_threshold with YAML override."""
        with patch("agentic_core.L0_routing.config.routing_calibration._load_yaml") as mock_load:
            mock_load.return_value = {"abstain": {"default_threshold": 0.75}}
            assert get_abstain_threshold() == 0.75

    def test_get_abstain_threshold_fallback(self):
        """Test get_abstain_threshold uses fallback when no override."""
        with patch("agentic_core.L0_routing.config.routing_calibration._load_yaml") as mock_load:
            mock_load.return_value = {}
            result = get_abstain_threshold()
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0


class TestGetSimilarityThreshold:
    """Tests for get_similarity_threshold function."""

    def test_get_similarity_threshold_env_override(self):
        """Test get_similarity_threshold with env override."""
        with patch.dict("os.environ", {"AGENTIC_SIMILARITY_THRESHOLD": "0.95"}, clear=True):
            assert get_similarity_threshold() == 0.95

    def test_get_similarity_threshold_namespace_override(self):
        """Test get_similarity_threshold with per-namespace override."""
        with patch("agentic_core.L0_routing.config.routing_calibration._load_yaml") as mock_load:
            mock_load.return_value = {
                "semantic_cache": {
                    "per_namespace_thresholds": {"test_namespace": 0.95},
                }
            }
            assert get_similarity_threshold("test_namespace") == 0.95

    def test_get_similarity_threshold_yaml_override(self):
        """Test get_similarity_threshold with YAML global override."""
        with patch("agentic_core.L0_routing.config.routing_calibration._load_yaml") as mock_load:
            mock_load.return_value = {"semantic_cache": {"similarity_threshold": 0.95}}
            assert get_similarity_threshold() == 0.95

    def test_get_similarity_threshold_fallback(self):
        """Test get_similarity_threshold uses fallback when no override."""
        with patch("agentic_core.L0_routing.config.routing_calibration._load_yaml") as mock_load:
            mock_load.return_value = {}
            result = get_similarity_threshold()
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_get_similarity_threshold_no_namespace(self):
        """Test get_similarity_threshold without namespace parameter."""
        with patch("agentic_core.L0_routing.config.routing_calibration._load_yaml") as mock_load:
            mock_load.return_value = {"semantic_cache": {"similarity_threshold": 0.95}}
            assert get_similarity_threshold() == 0.95


class TestGetV12Threshold:
    """Tests for get_v12_threshold function."""

    def test_get_v12_threshold_env_override(self):
        """Test get_v12_threshold with env override."""
        with patch.dict("os.environ", {"AGENTIC_V12_CLASSIFIER_SURFACE_THRESHOLD": "0.80"}, clear=True):
            assert get_v12_threshold("classifier_surface_threshold") == 0.80

    def test_get_v12_threshold_yaml_override(self):
        """Test get_v12_threshold with YAML override."""
        with patch("agentic_core.L0_routing.config.routing_calibration._load_yaml") as mock_load:
            mock_load.return_value = {"v12_routing": {"classifier_surface_threshold": 0.80}}
            assert get_v12_threshold("classifier_surface_threshold") == 0.80

    def test_get_v12_threshold_fallback(self):
        """Test get_v12_threshold uses fallback when no override."""
        with patch("agentic_core.L0_routing.config.routing_calibration._load_yaml") as mock_load:
            mock_load.return_value = {}
            result = get_v12_threshold("classifier_surface_threshold")
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_get_v12_threshold_unknown_name(self):
        """Test get_v12_threshold raises KeyError for unknown name."""
        with pytest.raises(KeyError, match="unknown v12 routing threshold"):
            get_v12_threshold("unknown_threshold")

    def test_get_v12_threshold_all_fallbacks(self):
        """Test that all V12 fallback thresholds are in valid range."""
        # This test validates the fallback constants themselves
        fallbacks = [
            "classifier_surface_threshold",
            "classifier_dominance_delta",
            "r1b_semantic_match_threshold",
            "r_casc_escalation_threshold",
            "r_loop_quality_threshold",
            "cold_start_conservative_threshold",
            "loop_guard_efficiency_threshold",
        ]
        for name in fallbacks:
            result = get_v12_threshold(name)
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0


class TestGetV12Int:
    """Tests for get_v12_int function."""

    def test_get_v12_int_env_override(self):
        """Test get_v12_int with env override."""
        with patch.dict("os.environ", {"AGENTIC_V12_MIN_SPANS_FOR_LOOP_GUARD": "10"}, clear=True):
            assert get_v12_int("min_spans_for_loop_guard") == 10

    def test_get_v12_int_yaml_override(self):
        """Test get_v12_int with YAML override."""
        with patch("agentic_core.L0_routing.config.routing_calibration._load_yaml") as mock_load:
            mock_load.return_value = {"v12_routing": {"min_spans_for_loop_guard": 10}}
            assert get_v12_int("min_spans_for_loop_guard") == 10

    def test_get_v12_int_fallback(self):
        """Test get_v12_int uses fallback when no override."""
        with patch("agentic_core.L0_routing.config.routing_calibration._load_yaml") as mock_load:
            mock_load.return_value = {}
            result = get_v12_int("min_spans_for_loop_guard")
            assert isinstance(result, int)
            assert result >= 1

    def test_get_v12_int_unknown_name(self):
        """Test get_v12_int raises KeyError for unknown name."""
        with pytest.raises(KeyError, match="unknown v12 routing int param"):
            get_v12_int("unknown_int")

    def test_get_v12_int_all_fallbacks(self):
        """Test that all V12 int fallbacks are positive."""
        # This test validates the fallback constants themselves
        int_fallbacks = [
            "min_spans_for_loop_guard",
            "r_casc_max_depth",
            "r_loop_max_iterations",
        ]
        for name in int_fallbacks:
            result = get_v12_int(name)
            assert isinstance(result, int)
            assert result >= 1


class TestResetCache:
    """Tests for reset_cache function."""

    def test_reset_cache_clears_yaml_cache(self):
        """Test that reset_cache clears the YAML cache."""
        # First call loads and caches
        with patch("agentic_core.L0_routing.config.routing_calibration._load_yaml") as mock_load:
            mock_load.return_value = {"abstain": {"default_threshold": 0.75}}
            get_abstain_threshold()
            assert mock_load.call_count == 1

        # Reset cache
        reset_cache()

        # Second call should reload
        with patch("agentic_core.L0_routing.config.routing_calibration._load_yaml") as mock_load:
            mock_load.return_value = {"abstain": {"default_threshold": 0.80}}
            result2 = get_abstain_threshold()
            assert mock_load.call_count == 1
            assert result2 == 0.80
