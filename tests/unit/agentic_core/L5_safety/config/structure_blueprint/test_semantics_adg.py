"""ADG-driven tests for L5 structure_blueprint/semantics.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.config.structure_blueprint.semantics import (
    NAMING_CONVENTIONS,
)


class TestNamingConventions:
    def test_is_mapping(self):
        assert hasattr(NAMING_CONVENTIONS, "__getitem__")

    def test_has_agent_convention(self):
        assert "agent" in NAMING_CONVENTIONS

    def test_has_utility_convention(self):
        assert "utility" in NAMING_CONVENTIONS

    def test_has_config_convention(self):
        assert "config" in NAMING_CONVENTIONS

    def test_agent_convention_has_pattern(self):
        assert "pattern" in NAMING_CONVENTIONS["agent"]

    def test_agent_convention_pattern_string(self):
        assert isinstance(NAMING_CONVENTIONS["agent"]["pattern"], str)

    def test_utility_convention_has_description(self):
        assert "description" in NAMING_CONVENTIONS["utility"]

    def test_non_empty(self):
        assert len(NAMING_CONVENTIONS) > 0
