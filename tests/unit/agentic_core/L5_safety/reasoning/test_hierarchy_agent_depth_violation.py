"""
Tests for HierarchyAgent._heal_depth_violation (depth_aligned bug fix).

## BRANCH_INVENTORY
| file | function | branch | expected | test |
|------|----------|--------|----------|------|
| HierarchyAgent.py | _heal_depth_violation | depth > expected (DEEP) | calls gatekeeper.safe_move, returns 1 | test_deep_calls_gatekeeper |
| HierarchyAgent.py | _heal_depth_violation | DEEP + target exists collision | delegates to _legacy_archive | test_deep_collision_delegates_legacy |
| HierarchyAgent.py | _heal_depth_violation | DEEP + gk move fails | logs error, returns 0 | test_deep_gk_failure_returns_zero |
| HierarchyAgent.py | _heal_depth_violation | depth < expected (SHALLOW) | logs error, returns 0, NO gk call | test_shallow_returns_zero_no_gk |
| HierarchyAgent.py | _heal_depth_violation | SHALLOW any depth deficit | still returns 0 | test_shallow_any_deficit |
| HierarchyAgent.py | _heal_depth_violation | exception raised | caught, logs error, returns 0 | test_exception_returns_zero |
| HierarchyAgent.py | _heal_depth_violation | DEEP success | logs HEALED, returns 1 | test_deep_success_returns_one |
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Minimal agent factory
# ---------------------------------------------------------------------------

def _make_agent(project_root: Path):
    from agentic_core.L5_safety.reasoning.HierarchyAgent import HierarchyAgent

    agent = object.__new__(HierarchyAgent)
    agent.project_root = project_root
    agent.agent_name = "HierarchyAgent"
    agent.healing_enabled = True

    gk = MagicMock()
    gk.safe_move.return_value = MagicMock(success=True, error=None)
    agent.gatekeeper = gk
    agent._legacy_archive_depth_violation = MagicMock(return_value=0)
    return agent


def _call(agent, file_path, rel, depth, expected):
    with patch("agentic_core.L5_safety.reasoning.HierarchyAgent._wg") as mock_wg:
        mock_wg.ensure_dir = MagicMock()
        return agent._heal_depth_violation(file_path, rel, depth, expected)


# ---------------------------------------------------------------------------
# DEEP violation (depth > expected)
# ---------------------------------------------------------------------------

class TestHierarchyDeepViolation:
    def test_deep_calls_gatekeeper_safe_move(self, tmp_path):
        """DEEP: gatekeeper.safe_move is called once with flattened target."""
        agent = _make_agent(tmp_path)
        # rel: agentic_core/L0_routing/scripts/extra/agent.py → depth 4, expected 3
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        result = _call(agent, file_path, rel, depth=4, expected=3)

        agent.gatekeeper.safe_move.assert_called_once()
        target_arg = agent.gatekeeper.safe_move.call_args[0][1]
        # Flattened: parts[:3] + (name,) = agentic_core/L0_routing/scripts/agent.py
        assert "extra" not in str(target_arg)
        assert target_arg.name == "agent.py"

    def test_deep_success_returns_one(self, tmp_path):
        """DEEP + gk success → returns 1."""
        agent = _make_agent(tmp_path)
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        result = _call(agent, file_path, rel, depth=4, expected=3)

        assert result == 1

    def test_deep_gk_failure_returns_zero(self, tmp_path):
        """DEEP + gk failure → returns 0, logs error."""
        agent = _make_agent(tmp_path)
        agent.gatekeeper.safe_move.return_value = MagicMock(success=False, error="permission denied")
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        with patch("agentic_core.L5_safety.reasoning.HierarchyAgent.Logger") as mock_log:
            result = _call(agent, file_path, rel, depth=4, expected=3)

        assert result == 0
        mock_log.error.assert_called_once()

    def test_deep_collision_delegates_to_legacy_archive(self, tmp_path):
        """DEEP + target already exists → delegates to _legacy_archive_depth_violation."""
        agent = _make_agent(tmp_path)
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")
        # Pre-create the target to trigger collision
        target = tmp_path / "agentic_core" / "L0_routing" / "scripts" / "agent.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("existing")

        _call(agent, file_path, rel, depth=4, expected=3)

        agent._legacy_archive_depth_violation.assert_called_once()
        # gatekeeper.safe_move must NOT be called — collision path takes over
        agent.gatekeeper.safe_move.assert_not_called()

    def test_deep_no_depth_aligned_folder_created(self, tmp_path):
        """Mutation: depth_aligned must never appear in filesystem after DEEP heal."""
        agent = _make_agent(tmp_path)
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        _call(agent, file_path, rel, depth=4, expected=3)

        all_dirs = [p for p in tmp_path.rglob("*") if p.is_dir()]
        assert all("depth_aligned" not in d.name for d in all_dirs)


# ---------------------------------------------------------------------------
# SHALLOW violation (depth < expected) — depth_aligned bug fix
# ---------------------------------------------------------------------------

class TestHierarchyShallowViolation:
    def test_shallow_returns_zero(self, tmp_path):
        """SHALLOW: returns 0 — no healing action taken."""
        agent = _make_agent(tmp_path)
        rel = Path("tests/test_x.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        result = _call(agent, file_path, rel, depth=1, expected=3)

        assert result == 0

    def test_shallow_gatekeeper_never_called(self, tmp_path):
        """Fail-closed: SHALLOW never calls gatekeeper.safe_move."""
        agent = _make_agent(tmp_path)
        rel = Path("tests/test_x.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        _call(agent, file_path, rel, depth=1, expected=3)

        agent.gatekeeper.safe_move.assert_not_called()

    def test_shallow_logs_error(self, tmp_path):
        """SHALLOW: Logger.error called with SHALLOW DEPTH message."""
        agent = _make_agent(tmp_path)
        rel = Path("tests/test_x.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        with patch("agentic_core.L5_safety.reasoning.HierarchyAgent.Logger") as mock_log:
            _call(agent, file_path, rel, depth=1, expected=3)

        mock_log.error.assert_called_once()
        msg = mock_log.error.call_args[0][0]
        assert "SHALLOW" in msg
        assert "Manual intervention" in msg

    def test_shallow_no_depth_aligned_created(self, tmp_path):
        """Mutation: depth_aligned folder must NEVER be created for any deficit."""
        agent = _make_agent(tmp_path)
        rel = Path("tests/test_x.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        # Large deficit (depth 1, expected 5)
        _call(agent, file_path, rel, depth=1, expected=5)

        all_dirs = [p for p in tmp_path.rglob("*") if p.is_dir()]
        assert all("depth_aligned" not in d.name for d in all_dirs)

    @pytest.mark.parametrize("deficit", [1, 2, 3, 5])
    def test_shallow_any_deficit_returns_zero(self, tmp_path, deficit):
        """Matrix: any depth deficit → always returns 0, never mutates filesystem."""
        agent = _make_agent(tmp_path)
        rel = Path("tests/test_x.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        result = _call(agent, file_path, rel, depth=1, expected=1 + deficit)

        assert result == 0
        agent.gatekeeper.safe_move.assert_not_called()


# ---------------------------------------------------------------------------
# Exception path (§1.5)
# ---------------------------------------------------------------------------

class TestHierarchyExceptionPath:
    def test_exception_returns_zero(self, tmp_path):
        """Exception during heal → caught, returns 0."""
        agent = _make_agent(tmp_path)
        agent.gatekeeper.safe_move.side_effect = RuntimeError("disk full")
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        result = _call(agent, file_path, rel, depth=4, expected=3)

        assert result == 0

    def test_exception_logs_error(self, tmp_path):
        """Exception → Logger.error called."""
        agent = _make_agent(tmp_path)
        agent.gatekeeper.safe_move.side_effect = OSError("permission denied")
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        with patch("agentic_core.L5_safety.reasoning.HierarchyAgent.Logger") as mock_log:
            _call(agent, file_path, rel, depth=4, expected=3)

        mock_log.error.assert_called_once()

    def test_exception_no_side_effects(self, tmp_path):
        """Exception → no filesystem mutation occurs."""
        agent = _make_agent(tmp_path)
        agent.gatekeeper.safe_move.side_effect = ValueError("bad state")
        rel = Path("agentic_core/L0_routing/scripts/extra/agent.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("original content")

        _call(agent, file_path, rel, depth=4, expected=3)

        # Source file untouched
        assert file_path.read_text() == "original content"


# ---------------------------------------------------------------------------
# Boundary / determinism (§1.8, §1.10)
# ---------------------------------------------------------------------------

class TestHierarchyBoundaries:
    def test_depth_equals_expected_is_deep_path_edge(self, tmp_path):
        """Boundary: depth == expected → not DEEP, not SHALLOW → handled upstream (depth==expected skipped before call)."""
        # _heal_depth_violation is only called when depth != expected.
        # If called with equal values (depth==expected) it hits neither branch.
        agent = _make_agent(tmp_path)
        rel = Path("agentic_core/L0_routing/scripts/agent.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        # depth == expected → neither branch: DEEP (3 > 3 False), SHALLOW (3 < 3 False)
        # Falls through to else: returns 0
        result = _call(agent, file_path, rel, depth=3, expected=3)
        assert result == 0
        agent.gatekeeper.safe_move.assert_not_called()

    def test_deterministic_shallow_repeated_calls(self, tmp_path):
        """Determinism: identical SHALLOW input → identical result."""
        agent = _make_agent(tmp_path)
        rel = Path("tests/test_x.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        r1 = _call(agent, file_path, rel, depth=1, expected=3)
        r2 = _call(agent, file_path, rel, depth=1, expected=3)

        assert r1 == r2 == 0
