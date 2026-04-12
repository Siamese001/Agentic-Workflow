"""Test AiCheckingAiHardenings functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAiCheckingAiHardenings:
    """Test AiCheckingAiHardenings functionality."""

    def test_ai_checking_imports(self):
        """Test AI checking module imports."""
        from system_learning import ai_checking_hardening

        assert ai_checking_hardening is not None

    def test_ai_checker_class(self):
        """Test AI checker class exists."""
        from system_learning.ai_checking_hardening import AIChecker

        assert AIChecker is not None

    def test_run_ai_checks(self):
        """Test run AI checks function."""
        from system_learning.ai_checking_hardening import run_ai_checks

        assert callable(run_ai_checks)
