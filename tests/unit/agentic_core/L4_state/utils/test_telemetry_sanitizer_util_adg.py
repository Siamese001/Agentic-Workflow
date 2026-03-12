"""ADG-driven tests for L4_state/utils/telemetry_sanitizer_util.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L4_state.utils.telemetry_sanitizer_util import sanitize_tool_output


class TestTelemetrySanitizerUtil:
    def test_importable(self):
        assert callable(sanitize_tool_output)

    def test_returns_string(self):
        result = sanitize_tool_output("some output text")
        assert isinstance(result, str)

    def test_passes_clean_text_unchanged(self):
        result = sanitize_tool_output("clean output")
        assert "clean output" in result

    def test_handles_empty_string(self):
        result = sanitize_tool_output("")
        assert isinstance(result, str)

    def test_handles_none_gracefully(self):
        result = sanitize_tool_output(None)
        assert result is None or isinstance(result, str)
