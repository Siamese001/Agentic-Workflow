"""ADG-driven tests for interfaces/validators.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.interfaces.validators as m


class TestValidatorsInterface:
    def test_importable(self):
        assert m is not None

    def test_rule_failure_present(self):
        assert hasattr(m, "RuleFailure")

    def test_all_exports(self):
        assert "RuleFailure" in m.__all__

    def test_rule_failure_is_class(self):
        assert isinstance(m.RuleFailure, type)
