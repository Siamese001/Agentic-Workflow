"""ADG-driven tests for L5_safety/reasoning/GitHygieneAgent.py — fan_in=1."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.reasoning.GitHygieneAgent import GitHygieneAgent


class TestGitHygieneAgentInit:
    def test_creates(self):
        ctx = MagicMock()
        agent = GitHygieneAgent(project_root=Path("."), ctx=ctx)
        assert agent is not None

    def test_project_root_stored(self):
        ctx = MagicMock()
        p = Path(".")
        agent = GitHygieneAgent(project_root=p, ctx=ctx)
        assert agent.project_root == p

    def test_has_execute(self):
        assert hasattr(GitHygieneAgent, "execute")

    def test_has_heal_repository(self):
        assert hasattr(GitHygieneAgent, "heal_repository")
