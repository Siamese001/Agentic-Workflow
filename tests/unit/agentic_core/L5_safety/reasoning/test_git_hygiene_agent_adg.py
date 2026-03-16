"""ADG-driven tests for L5_safety/reasoning/GitHygieneAgent.py — fan_in=1."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_git_hygiene_agent_adg")
_emit_applies_guardrail("p0", "test_git_hygiene_agent_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_git_hygiene_agent_adg", "policy_binding")
_emit_snapshots_state("p0", "test_git_hygiene_agent_adg", "state_snapshot")
emit_replay_key("p0", "test_git_hygiene_agent_adg")
emit_determinism_digest("p0", "test_git_hygiene_agent_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
