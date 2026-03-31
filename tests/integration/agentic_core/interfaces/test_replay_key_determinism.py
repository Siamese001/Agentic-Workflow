"""Test ReplayKeyDeterminism functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestReplayKeyDeterminism:
    """Test ReplayKeyDeterminism functionality."""

    def test_replay_key_determinism_imports(self):
        """Test replay_key_determinism module imports."""
        from agentic_core import replay_key_determinism
        assert replay_key_determinism is not None

    def test_replay_key_determinism_class(self):
        """Test ReplayKeyDeterminism class exists."""
        from agentic_core import ReplayKeyDeterminism
        assert ReplayKeyDeterminism is not None

    def test_replay_key_determinism_callable(self):
        """Test replay_key_determinism functions are callable."""
        from agentic_core import validate_replay_key_determinism
        assert callable(validate_replay_key_determinism)
