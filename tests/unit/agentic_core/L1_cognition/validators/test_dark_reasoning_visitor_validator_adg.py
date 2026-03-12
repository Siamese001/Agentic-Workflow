"""ADG-driven tests for L1_cognition/validators/dark_reasoning_visitor_validator.py — fan_in=0."""
from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.validators.dark_reasoning_visitor_validator import (
    check_dark_reasoning,
)


class TestCheckDarkReasoning:
    def test_returns_list(self, tmp_path):
        dummy = tmp_path / "dummy.py"
        dummy.write_text("x = 1\n")
        result = check_dark_reasoning(dummy)
        assert isinstance(result, list)

    def test_non_l1_l2_l3_returns_empty(self, tmp_path):
        dummy = tmp_path / "L0_routing" / "some_file.py"
        dummy.parent.mkdir(parents=True)
        dummy.write_text("x = 1\n")
        result = check_dark_reasoning(dummy)
        assert result == []

    def test_callable(self):
        assert callable(check_dark_reasoning)
