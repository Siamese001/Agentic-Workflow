"""Tests for agentic_core/utils/ast_fuzzy.py — _parse_threshold and get_threshold."""

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes


@pytest.mark.unit
class TestAstFuzzy:
    """Tests for _parse_threshold and get_threshold in ast_fuzzy."""

    def test_parse_threshold_none_returns_default(self):
        """_parse_threshold(None) returns the default threshold."""
        from agentic_core.utils.ast_fuzzy import _DEFAULT_THRESHOLD, _parse_threshold

        assert _parse_threshold(None) == _DEFAULT_THRESHOLD

    def test_parse_threshold_valid_value(self):
        """_parse_threshold returns the parsed float for a valid string."""
        from agentic_core.utils.ast_fuzzy import _parse_threshold

        result = _parse_threshold("0.8")
        assert abs(result - 0.8) < 1e-9

    def test_parse_threshold_invalid_string_returns_default(self):
        """_parse_threshold falls back to default for non-numeric input."""
        from agentic_core.utils.ast_fuzzy import _DEFAULT_THRESHOLD, _parse_threshold

        assert _parse_threshold("not_a_float") == _DEFAULT_THRESHOLD

    def test_parse_threshold_out_of_range_returns_default(self):
        """_parse_threshold falls back to default for value > 1.0."""
        from agentic_core.utils.ast_fuzzy import _DEFAULT_THRESHOLD, _parse_threshold

        assert _parse_threshold("1.5") == _DEFAULT_THRESHOLD

    def test_get_threshold_with_valid_env(self, monkeypatch):
        """get_threshold() returns value from AST_FUZZY_THRESHOLD env var."""
        monkeypatch.setenv("AST_FUZZY_THRESHOLD", "0.75")
        from agentic_core.utils.ast_fuzzy import get_threshold

        assert abs(get_threshold() - 0.75) < 1e-9

    def test_get_threshold_unset_returns_default(self, monkeypatch):
        """get_threshold() returns default when AST_FUZZY_THRESHOLD is not set."""
        monkeypatch.delenv("AST_FUZZY_THRESHOLD", raising=False)
        from agentic_core.utils.ast_fuzzy import _DEFAULT_THRESHOLD, get_threshold

        assert get_threshold() == _DEFAULT_THRESHOLD
