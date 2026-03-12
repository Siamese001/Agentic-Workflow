"""ADG-driven tests for agentic_core/L5_safety/reasoning/root_hygiene_healer.py — fan_in=4.

Contract tests: RootHygieneAgent init, stats structure, and run() in dry-run mode.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from pathlib import Path as _Path
from agentic_core.L5_safety.reasoning.root_hygiene_healer import (
    RootHygieneAgent,
    get_project_root,
)

# Use the actual repo root — SovereignBaseAgent rejects paths outside the project
_REPO_ROOT = _Path(__file__).parents[5]  # tests/unit/agentic_core/L5_safety/reasoning -> repo root


class TestGetProjectRoot:
    def test_returns_path(self):
        try:
            root = get_project_root()
            assert isinstance(root, Path)
        except RuntimeError:
            pytest.skip("Not running from project root — expected in CI sub-dirs")


class TestRootHygieneAgentInit:
    def test_creates_with_defaults(self):
        agent = RootHygieneAgent(project_root=_REPO_ROOT)
        assert agent is not None

    def test_project_root_stored(self):
        agent = RootHygieneAgent(project_root=_REPO_ROOT)
        assert agent.project_root == _REPO_ROOT.resolve()

    def test_dry_run_default_false(self):
        agent = RootHygieneAgent(project_root=_REPO_ROOT)
        assert agent.dry_run is False

    def test_dry_run_can_be_set(self):
        agent = RootHygieneAgent(project_root=_REPO_ROOT, dry_run=True)
        assert agent.dry_run is True

    def test_stats_initialized(self):
        agent = RootHygieneAgent(project_root=_REPO_ROOT)
        for key in ("scripts_evacuated", "dirs_evacuated", "coverage_relocated",
                    "illegal_dirs_removed", "n_duplicates_removed", "errors"):
            assert key in agent.stats
            assert agent.stats[key] == 0


class TestRootHygieneAgentInterface:
    def test_run_method_exists(self):
        agent = RootHygieneAgent(project_root=_REPO_ROOT)
        assert callable(agent.run)

    def test_run_returns_dict(self):
        agent = RootHygieneAgent(project_root=_REPO_ROOT, dry_run=True)
        result = agent.run()
        assert isinstance(result, dict)

    def test_run_result_has_required_keys(self):
        agent = RootHygieneAgent(project_root=_REPO_ROOT, dry_run=True)
        result = agent.run()
        assert "success" in result
        assert "stats" in result
        assert "summary" in result

    def test_run_summary_is_string(self):
        agent = RootHygieneAgent(project_root=_REPO_ROOT, dry_run=True)
        result = agent.run()
        assert isinstance(result["summary"], str)

    def test_stats_has_all_keys(self):
        agent = RootHygieneAgent(project_root=_REPO_ROOT, dry_run=True)
        result = agent.run()
        for key in ("scripts_evacuated", "dirs_evacuated", "errors"):
            assert key in result["stats"]
