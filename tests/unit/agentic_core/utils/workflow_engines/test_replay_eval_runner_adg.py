"""Test ReplayEvalRunnerAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestReplayEvalRunnerAdg:
    """Test ReplayEvalRunnerAdg functionality."""

    def test_replay_eval_runner_adg_imports(self):
        """Test replay_eval_runner_adg module imports."""
        from agentic_core import replay_eval_runner_adg

        assert replay_eval_runner_adg is not None

    def test_replay_eval_runner_adg_class(self):
        """Test ReplayEvalRunnerAdg class exists."""
        from agentic_core import ReplayEvalRunnerAdg

        assert ReplayEvalRunnerAdg is not None

    def test_replay_eval_runner_adg_callable(self):
        """Test replay_eval_runner_adg functions are callable."""
        from agentic_core import validate_replay_eval_runner_adg

        assert callable(validate_replay_eval_runner_adg)
