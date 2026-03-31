"""Test meta learning bus creative functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMetaLearningBusCreative:
    """Test meta learning bus creative functionality."""

    def test_meta_learning_creative_imports(self):
        """Test meta learning creative module imports."""
        from system_learning.meta_learning import creative
        assert creative is not None

    def test_meta_learning_creative_strategy(self):
        """Test meta learning creative strategy exists."""
        from system_learning.meta_learning.creative import CreativeStrategy
        assert CreativeStrategy is not None

    def test_meta_learning_apply_creative(self):
        """Test meta learning apply creative function."""
        from system_learning.meta_learning.creative import apply_creative_strategy
        assert callable(apply_creative_strategy)
