"""Test FixMissionRunnerUtilAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestFixMissionRunnerUtilAdg:
    """Test FixMissionRunnerUtilAdg functionality."""

    def test_fix_mission_runner_util_adg_imports(self):
        """Test fix_mission_runner_util_adg module imports."""
        from agentic_core import fix_mission_runner_util_adg

        assert fix_mission_runner_util_adg is not None

    def test_fix_mission_runner_util_adg_class(self):
        """Test FixMissionRunnerUtilAdg class exists."""
        from agentic_core import FixMissionRunnerUtilAdg

        assert FixMissionRunnerUtilAdg is not None

    def test_fix_mission_runner_util_adg_callable(self):
        """Test fix_mission_runner_util_adg functions are callable."""
        from agentic_core import validate_fix_mission_runner_util_adg

        assert callable(validate_fix_mission_runner_util_adg)
