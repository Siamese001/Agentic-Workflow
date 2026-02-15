"""Unit tests for instructional injections module."""

from unittest.mock import patch

import pytest

from agentic_core.runtime.config.instructional_injections import (
    _get_markdown_injections,
    get_instructional_injections,
    get_required_injections,
)


class TestInstructionalInjections:
    """Test instructional injections functionality."""

    def test_get_required_injections_deterministic_rule(self):
        """Test that required injections follow deterministic rule (framing layer)."""
        # Test with markdown fallback (deterministic)
        with patch("agentic_core.config.core.yaml_injection_loader.get_yaml_loader") as mock_loader:
            mock_loader.side_effect = ImportError("Force markdown fallback")

            required = get_required_injections()

            # Should have exactly 5 required patterns (framing layer)
            assert len(required) == 5, f"Expected 5 required patterns, got {len(required)}"

            # All should have required=True
            for pattern in required:
                assert pattern.required is True, f"Pattern {pattern.id} should be required"

            # Should be from framing layer (1-5)
            required_ids = {pattern.id for pattern in required}
            assert required_ids == {1, 2, 3, 4, 5}, f"Required IDs should be 1-5, got {required_ids}"

    def test_runtime_error_not_swallowed(self):
        """Test that RuntimeError is not swallowed in get_instructional_injections."""
        # Mock the import inside the function
        with patch("agentic_core.config.core.yaml_injection_loader.get_yaml_loader") as mock_loader:
            mock_loader.side_effect = RuntimeError("Programmer error")

            # RuntimeError should propagate, not be swallowed
            with pytest.raises(RuntimeError, match="Programmer error"):
                get_instructional_injections()

    def test_import_error_handled_gracefully(self):
        """Test that ImportError is handled gracefully with fallback."""
        # Mock the import inside the function
        with patch("agentic_core.config.core.yaml_injection_loader.get_yaml_loader") as mock_loader:
            mock_loader.side_effect = ImportError("Module not found")

            # Should fall back to markdown without raising
            patterns = get_instructional_injections()
            assert len(patterns) == 30, "Should fall back to 30 markdown patterns"

    def test_file_not_found_error_handled_gracefully(self):
        """Test that FileNotFoundError is handled gracefully with fallback."""
        # Mock the import inside the function
        with patch("agentic_core.config.core.yaml_injection_loader.get_yaml_loader") as mock_loader:
            mock_loader.return_value.load_all_patterns.side_effect = FileNotFoundError("YAML not found")

            # Should fall back to markdown without raising
            patterns = get_instructional_injections()
            assert len(patterns) == 30, "Should fall back to 30 markdown patterns"

    def test_framing_patterns_are_required_in_markdown(self):
        """Test that framing layer patterns are marked as required in markdown fallback."""
        patterns = _get_markdown_injections()

        # Check framing patterns (1-5) are required
        for pattern_id in range(1, 6):
            pattern = next(p for p in patterns if p.id == pattern_id)
            assert pattern.required is True, f"Framing pattern {pattern_id} should be required"
            assert pattern.layer.value == "framing", f"Pattern {pattern_id} should be framing"

        # Check other patterns are not required
        for pattern_id in range(6, 31):
            pattern = next(p for p in patterns if p.id == pattern_id)
            assert pattern.required is False, f"Non-framing pattern {pattern_id} should not be required"

    def test_required_count_consistency(self):
        """Test that required count is consistent across multiple calls."""
        with patch("agentic_core.config.core.yaml_injection_loader.get_yaml_loader") as mock_loader:
            mock_loader.side_effect = ImportError("Force markdown fallback")

            required1 = get_required_injections()
            required2 = get_required_injections()

            assert len(required1) == len(required2), "Required count should be consistent"
            assert len(required1) == 5, "Should always have 5 required patterns"
