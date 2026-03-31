"""Test SsotHealRunnerPreflight functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSsotHealRunnerPreflight:
    """Test SsotHealRunnerPreflight functionality."""

    def test_ssot_heal_runner_preflight_imports(self):
        """Test ssot_heal_runner_preflight module imports."""
        from agentic_core import ssot_heal_runner_preflight
        assert ssot_heal_runner_preflight is not None

    def test_ssot_heal_runner_preflight_class(self):
        """Test SsotHealRunnerPreflight class exists."""
        from agentic_core import SsotHealRunnerPreflight
        assert SsotHealRunnerPreflight is not None

    def test_ssot_heal_runner_preflight_callable(self):
        """Test ssot_heal_runner_preflight functions are callable."""
        from agentic_core import validate_ssot_heal_runner_preflight
        assert callable(validate_ssot_heal_runner_preflight)
