"""ADG-driven tests for L4_state/memory/runtime_models.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L4_state.memory.runtime_models import InjectionMatch, InjectionPattern


class TestInjectionPattern:
    def test_creates_with_defaults(self):
        p = InjectionPattern()
        assert p.priority == 0
        assert p.template == ""

    def test_creates_with_values(self):
        p = InjectionPattern(priority=5, template="Hello {name}")
        assert p.priority == 5
        assert p.template == "Hello {name}"


class TestInjectionMatch:
    def test_creates_with_defaults(self):
        m = InjectionMatch()
        assert isinstance(m.injection, InjectionPattern)
        assert m.relevance_score == 0.0
        assert m.variable_values == {}

    def test_creates_with_injection(self):
        p = InjectionPattern(priority=3, template="t")
        m = InjectionMatch(injection=p, relevance_score=0.9)
        assert m.injection.priority == 3
        assert m.relevance_score == pytest.approx(0.9)

    def test_variable_values_mutable(self):
        m = InjectionMatch()
        m.variable_values["key"] = "value"
        assert m.variable_values["key"] == "value"
