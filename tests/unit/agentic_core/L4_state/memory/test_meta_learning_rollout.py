"""Test MetaLearningRollout functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMetaLearningRollout:
    """Test MetaLearningRollout functionality."""

    def test_meta_learning_rollout_imports(self):
        """Test meta_learning_rollout module imports."""
        from agentic_core import meta_learning_rollout
        assert meta_learning_rollout is not None

    def test_meta_learning_rollout_class(self):
        """Test MetaLearningRollout class exists."""
        from agentic_core import MetaLearningRollout
        assert MetaLearningRollout is not None

    def test_meta_learning_rollout_callable(self):
        """Test meta_learning_rollout functions are callable."""
        from agentic_core import validate_meta_learning_rollout
        assert callable(validate_meta_learning_rollout)
