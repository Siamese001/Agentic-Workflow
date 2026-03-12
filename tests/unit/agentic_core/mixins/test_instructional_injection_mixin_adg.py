"""ADG-driven tests for agentic_core/mixins/instructional_injection_mixin.py — fan_in=3.

Contract tests: InstructionalInjectionMixin interface and injection layer methods.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.mixins.instructional_injection_mixin import (
    InstructionalInjectionMixin,
    get_instructional_injection_mixin,
    instructional_injection_mixin,
)


class ConcreteAgent(InstructionalInjectionMixin):
    pass


class TestInstructionalInjectionMixinImport:
    def test_class_importable(self):
        assert callable(InstructionalInjectionMixin)

    def test_alias_same_as_class(self):
        assert instructional_injection_mixin is InstructionalInjectionMixin

    def test_factory_function_callable(self):
        assert callable(get_instructional_injection_mixin)

    def test_factory_returns_instance(self):
        obj = get_instructional_injection_mixin()
        assert isinstance(obj, InstructionalInjectionMixin)


class TestGetPattern:
    def test_returns_pattern_for_valid_id(self):
        agent = ConcreteAgent()
        pattern = agent.get_pattern(1)
        assert pattern is not None

    def test_returns_none_for_invalid_id(self):
        agent = ConcreteAgent()
        assert agent.get_pattern(999) is None

    def test_pattern_has_expected_attributes(self):
        agent = ConcreteAgent()
        pattern = agent.get_pattern(1)
        if pattern is not None:
            assert hasattr(pattern, "layer")
            assert hasattr(pattern, "enabled")
            assert hasattr(pattern, "template")


class TestGetPatternsByLayer:
    def test_returns_list(self):
        from agentic_core.config.core.injection_layer_config import InjectionLayer
        agent = ConcreteAgent()
        result = agent.get_patterns_by_layer(InjectionLayer.SAFETY)
        assert isinstance(result, list)

    def test_safety_layer_has_patterns(self):
        from agentic_core.config.core.injection_layer_config import InjectionLayer
        agent = ConcreteAgent()
        patterns = agent.get_patterns_by_layer(InjectionLayer.SAFETY)
        assert len(patterns) > 0


class TestInjectPattern:
    def test_inject_unchanged_on_disabled(self):
        agent = ConcreteAgent()
        # Pattern 999 doesn't exist → should return prompt unchanged
        result = agent.inject_pattern("my prompt", 999)
        assert result == "my prompt"

    def test_inject_safety_layer_returns_string(self):
        agent = ConcreteAgent()
        result = agent.inject_safety_layer("base prompt")
        assert isinstance(result, str)

    def test_inject_safety_layer_contains_original(self):
        agent = ConcreteAgent()
        result = agent.inject_safety_layer("original content")
        assert "original content" in result


class TestGetInjectionSummary:
    def test_returns_dict(self):
        agent = ConcreteAgent()
        summary = agent.get_injection_summary()
        assert isinstance(summary, dict)

    def test_has_total_patterns(self):
        agent = ConcreteAgent()
        summary = agent.get_injection_summary()
        assert "total_patterns" in summary
        assert summary["total_patterns"] >= 30

    def test_has_enabled_count(self):
        agent = ConcreteAgent()
        summary = agent.get_injection_summary()
        assert "enabled_count" in summary
        assert summary["enabled_count"] >= 0

    def test_has_layers_key(self):
        agent = ConcreteAgent()
        summary = agent.get_injection_summary()
        assert "layers" in summary
        assert isinstance(summary["layers"], dict)
