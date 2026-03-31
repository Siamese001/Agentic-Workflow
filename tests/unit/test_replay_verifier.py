"""Test ReplayVerifier functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestReplayVerifier:
    """Test ReplayVerifier functionality."""

    def test_replay_verifier_imports(self):
        """Test replay_verifier module imports."""
        from agentic_core import replay_verifier
        assert replay_verifier is not None

    def test_replay_verifier_class(self):
        """Test ReplayVerifier class exists."""
        from agentic_core import ReplayVerifier
        assert ReplayVerifier is not None

    def test_replay_verifier_callable(self):
        """Test replay_verifier functions are callable."""
        from agentic_core import validate_replay_verifier
        assert callable(validate_replay_verifier)
