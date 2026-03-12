"""ADG-driven tests for agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py — fan_in=8.

Contract tests: ArchitectureGovernorAgent init, stats, heal_repository, LAYER_DIRS.
"""
from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import (
    ArchitectureGovernorAgent,
    LAYER_DIRS,
)

_REPO_ROOT = Path(__file__).parents[5]


class TestLayerDirs:
    def test_layer_dirs_is_set(self):
        assert isinstance(LAYER_DIRS, set)

    def test_layer_dirs_nonempty(self):
        assert len(LAYER_DIRS) > 0

    def test_contains_l5_safety(self):
        assert any("L5" in d for d in LAYER_DIRS)


class TestArchitectureGovernorAgentInit:
    def test_creates_with_defaults(self):
        agent = ArchitectureGovernorAgent()
        assert agent is not None

    def test_project_root_is_path(self):
        agent = ArchitectureGovernorAgent()
        assert isinstance(agent.project_root, Path)

    def test_healing_enabled_default_true(self):
        agent = ArchitectureGovernorAgent()
        assert agent.healing_enabled is True

    def test_auto_approve_default_false(self):
        agent = ArchitectureGovernorAgent()
        assert agent.auto_approve is False

    def test_ci_mode_default_false(self):
        agent = ArchitectureGovernorAgent()
        assert agent.ci_mode is False

    def test_violations_starts_empty(self):
        agent = ArchitectureGovernorAgent()
        assert agent.violations == []

    def test_stats_dict_populated(self):
        agent = ArchitectureGovernorAgent()
        assert isinstance(agent.stats, dict)
        assert "violations_found" in agent.stats
        assert "violations_fixed" in agent.stats
        assert "errors" in agent.stats

    def test_python_files_starts_empty(self):
        agent = ArchitectureGovernorAgent()
        assert agent.python_files == []

    def test_lazy_loaded_agents_start_none(self):
        agent = ArchitectureGovernorAgent()
        assert agent._structure_validator is None
        assert agent._gravity_repair_agent is None
        assert agent._archival_gatekeeper is None

    def test_creates_with_custom_root(self):
        agent = ArchitectureGovernorAgent(project_root=_REPO_ROOT)
        assert agent.project_root == _REPO_ROOT

    def test_creates_with_ci_mode(self):
        agent = ArchitectureGovernorAgent(ci_mode=True, auto_approve=True)
        assert agent.ci_mode is True
        assert agent.auto_approve is True


class TestArchitectureGovernorAgentMethods:
    def setup_method(self):
        self.agent = ArchitectureGovernorAgent(project_root=_REPO_ROOT)

    def test_has_heal_repository(self):
        assert callable(self.agent.heal_repository)

    def test_has_get_structure_validator_lazy(self):
        assert hasattr(self.agent, "_get_structure_validator")
        assert callable(self.agent._get_structure_validator)

    def test_heal_repository_dry_run_returns_dict(self):
        result = self.agent.heal_repository(dry_run=True)
        assert isinstance(result, dict)
