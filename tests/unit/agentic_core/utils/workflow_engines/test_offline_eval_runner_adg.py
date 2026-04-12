"""Test OfflineEvalRunnerAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestOfflineEvalRunnerAdg:
    """Test OfflineEvalRunnerAdg functionality."""

    def test_offline_eval_runner_adg_imports(self):
        """Test offline_eval_runner_adg module imports."""
        from agentic_core import offline_eval_runner_adg

        assert offline_eval_runner_adg is not None

    def test_offline_eval_runner_adg_class(self):
        """Test OfflineEvalRunnerAdg class exists."""
        from agentic_core import OfflineEvalRunnerAdg

        assert OfflineEvalRunnerAdg is not None

    def test_offline_eval_runner_adg_callable(self):
        """Test offline_eval_runner_adg functions are callable."""
        from agentic_core import validate_offline_eval_runner_adg

        assert callable(validate_offline_eval_runner_adg)
