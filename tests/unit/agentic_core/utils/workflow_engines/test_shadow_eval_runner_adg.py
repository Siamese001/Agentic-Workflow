"""Test ShadowEvalRunnerAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestShadowEvalRunnerAdg:
    """Test ShadowEvalRunnerAdg functionality."""

    def test_shadow_eval_runner_adg_imports(self):
        """Test shadow_eval_runner_adg module imports."""
        from agentic_core import shadow_eval_runner_adg

        assert shadow_eval_runner_adg is not None

    def test_shadow_eval_runner_adg_class(self):
        """Test ShadowEvalRunnerAdg class exists."""
        from agentic_core import ShadowEvalRunnerAdg

        assert ShadowEvalRunnerAdg is not None

    def test_shadow_eval_runner_adg_callable(self):
        """Test shadow_eval_runner_adg functions are callable."""
        from agentic_core import validate_shadow_eval_runner_adg

        assert callable(validate_shadow_eval_runner_adg)
