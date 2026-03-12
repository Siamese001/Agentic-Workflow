"""ADG-driven tests for agentic_core/L5_safety/reasoning/NamingAgent.py — fan_in=4.

Contract tests: NamingAgent, PlacementResult, get_naming_agent factory.
"""
from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.reasoning.NamingAgent import (
    TREE_SITTER_AVAILABLE,
    NamingAgent,
    PlacementResult,
    get_naming_agent,
)


class TestModuleConstants:
    def test_tree_sitter_available_is_bool(self):
        assert isinstance(TREE_SITTER_AVAILABLE, bool)

    def test_all_exports(self):
        from agentic_core.L5_safety.reasoning.NamingAgent import __all__
        for name in ("NamingAgent", "get_naming_agent", "PlacementResult"):
            assert name in __all__


class TestPlacementResult:
    def test_default_init(self):
        p = PlacementResult()
        assert p.path == ""
        assert p.confidence == 1.0
        assert p.suggestions == []

    def test_custom_init(self):
        p = PlacementResult(path="agentic_core/L5_safety/foo.py", confidence=0.9)
        assert p.path == "agentic_core/L5_safety/foo.py"
        assert p.confidence == 0.9


class TestNamingAgentInit:
    def test_creates_without_args(self):
        a = NamingAgent()
        assert a is not None

    def test_creates_with_path_arg(self):
        a = NamingAgent(Path("."))
        assert a is not None


class TestNamingAgentInterface:
    def setup_method(self):
        self.agent = NamingAgent()

    def test_validate_name_returns_bool(self):
        result = self.agent.validate_name("my_module.py")
        assert isinstance(result, bool)

    def test_validate_name_accepts_string(self):
        assert self.agent.validate_name("valid_name") is True

    def test_suggest_name_returns_string(self):
        result = self.agent.suggest_name("some context")
        assert isinstance(result, str)

    def test_analyze_placement_returns_placement_result(self):
        result = self.agent.analyze_placement("class MyAgent: pass")
        assert isinstance(result, PlacementResult)

    def test_validate_prefix_location_returns_list(self):
        result = self.agent.validate_prefix_location_match(Path("agentic_core/L5_safety/foo.py"))
        assert isinstance(result, list)

    def test_scan_repository_duplicates_returns_dict(self):
        result = self.agent.scan_repository_duplicates()
        assert isinstance(result, dict)

    def test_move_to_canonical_location_dry_run(self):
        result = self.agent.move_to_canonical_location(Path("foo.py"), dry_run=True)
        assert isinstance(result, dict)

    def test_heal_violation_no_target(self):
        result = self.agent.heal({})
        assert result["status"] == "skipped"

    def test_heal_violation_with_target(self):
        result = self.agent.heal({"file": "some_module.py", "type": "naming_violation"})
        assert result["status"] in ("manual_required", "error")

    def test_heal_repository_returns_dict(self):
        result = self.agent.heal_repository(dry_run=True)
        assert isinstance(result, dict)
        assert "violations_found" in result


class TestGetNamingAgent:
    def test_factory_returns_naming_agent(self):
        agent = get_naming_agent()
        assert isinstance(agent, NamingAgent)

    def test_factory_with_root(self):
        agent = get_naming_agent(project_root=".")
        assert isinstance(agent, NamingAgent)
