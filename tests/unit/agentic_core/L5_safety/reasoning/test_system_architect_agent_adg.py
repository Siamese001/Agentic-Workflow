"""ADG-driven tests for agentic_core/L5_safety/reasoning/SystemArchitectAgent.py — fan_in=2.

Contract tests: SystemArchitectAgent init, heal(), get_validation_keys(), check methods.
"""
from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.reasoning.SystemArchitectAgent import SystemArchitectAgent


class TestSystemArchitectAgentInit:
    def test_creates_with_defaults(self):
        agent = SystemArchitectAgent()
        assert agent is not None

    def test_cached_scan_root_starts_none(self):
        agent = SystemArchitectAgent()
        assert agent._cached_scan_root is None

    def test_cached_module_map_starts_none(self):
        agent = SystemArchitectAgent()
        assert agent._cached_module_map is None

    def test_cached_dependency_graph_starts_none(self):
        agent = SystemArchitectAgent()
        assert agent._cached_dependency_graph is None


class TestSystemArchitectAgentHeal:
    def setup_method(self):
        self.agent = SystemArchitectAgent()

    def test_heal_returns_dict(self):
        result = self.agent.heal({"type": "DEPTH", "file": "agentic_core/L5/foo.py"})
        assert isinstance(result, dict)

    def test_heal_status_manual_required(self):
        result = self.agent.heal({"type": "IMPORT_VIOLATION", "file": "foo.py"})
        assert result["status"] == "manual_required"

    def test_heal_has_reason(self):
        result = self.agent.heal({"type": "DEPTH", "file": "foo.py"})
        assert "reason" in result

    def test_heal_has_suggested_action(self):
        result = self.agent.heal({"type": "DEPTH", "file": "foo.py"})
        assert "suggested_action" in result

    def test_heal_missing_file_still_returns_dict(self):
        result = self.agent.heal({"type": "DEPTH"})
        assert isinstance(result, dict)


class TestSystemArchitectAgentValidationKeys:
    def test_get_validation_keys_returns_list(self):
        agent = SystemArchitectAgent()
        keys = agent.get_validation_keys()
        assert isinstance(keys, list)

    def test_validation_keys_range_40_to_50(self):
        agent = SystemArchitectAgent()
        keys = agent.get_validation_keys()
        assert 40 in keys
        assert 50 in keys

    def test_validation_keys_count(self):
        agent = SystemArchitectAgent()
        keys = agent.get_validation_keys()
        assert len(keys) == 11  # 40..50 inclusive


class TestSystemArchitectAgentCheckMethods:
    def setup_method(self):
        self.agent = SystemArchitectAgent(project_root=Path("."))

    def test_check_core_architecture_method_exists(self):
        assert callable(self.agent.check_core_architecture)

    def test_check_no_deep_nesting_method_exists(self):
        assert callable(self.agent.check_no_deep_nesting)

    def test_check_no_large_files_method_exists(self):
        assert callable(self.agent.check_no_large_files)
