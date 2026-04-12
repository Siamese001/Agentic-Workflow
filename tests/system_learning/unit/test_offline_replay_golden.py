"""Test OfflineReplayGolden functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestOfflineReplayGolden:
    """Test OfflineReplayGolden functionality."""

    def test_offline_replay_golden_imports(self):
        """Test offline_replay_golden module imports."""
        from agentic_core import offline_replay_golden

        assert offline_replay_golden is not None

    def test_offline_replay_golden_class(self):
        """Test OfflineReplayGolden class exists."""
        from agentic_core import OfflineReplayGolden

        assert OfflineReplayGolden is not None

    def test_offline_replay_golden_callable(self):
        """Test offline_replay_golden functions are callable."""
        from agentic_core import validate_offline_replay_golden

        assert callable(validate_offline_replay_golden)
