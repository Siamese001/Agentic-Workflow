"""Test MissionRunnerWiring functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMissionRunnerWiring:
    """Test MissionRunnerWiring functionality."""

    def test_mission_runner_wiring_imports(self):
        """Test mission_runner_wiring module imports."""
        from agentic_core import mission_runner_wiring
        assert mission_runner_wiring is not None

    def test_mission_runner_wiring_class(self):
        """Test MissionRunnerWiring class exists."""
        from agentic_core import MissionRunnerWiring
        assert MissionRunnerWiring is not None

    def test_mission_runner_wiring_callable(self):
        """Test mission_runner_wiring functions are callable."""
        from agentic_core import validate_mission_runner_wiring
        assert callable(validate_mission_runner_wiring)
