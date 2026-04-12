"""Test MissionStatusAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMissionStatusAdg:
    """Test MissionStatusAdg functionality."""

    def test_mission_status_adg_imports(self):
        """Test mission_status_adg module imports."""
        from agentic_core import mission_status_adg

        assert mission_status_adg is not None

    def test_mission_status_adg_class(self):
        """Test MissionStatusAdg class exists."""
        from agentic_core import MissionStatusAdg

        assert MissionStatusAdg is not None

    def test_mission_status_adg_callable(self):
        """Test mission_status_adg functions are callable."""
        from agentic_core import validate_mission_status_adg

        assert callable(validate_mission_status_adg)
