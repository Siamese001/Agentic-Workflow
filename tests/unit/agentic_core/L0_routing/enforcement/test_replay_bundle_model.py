"""Test ReplayBundleModel functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestReplayBundleModel:
    """Test ReplayBundleModel functionality."""

    def test_replay_bundle_model_imports(self):
        """Test replay_bundle_model module imports."""
        from agentic_core import replay_bundle_model

        assert replay_bundle_model is not None

    def test_replay_bundle_model_class(self):
        """Test ReplayBundleModel class exists."""
        from agentic_core import ReplayBundleModel

        assert ReplayBundleModel is not None

    def test_replay_bundle_model_callable(self):
        """Test replay_bundle_model functions are callable."""
        from agentic_core import validate_replay_bundle_model

        assert callable(validate_replay_bundle_model)
