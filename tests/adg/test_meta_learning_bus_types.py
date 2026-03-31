"""Test meta learning bus types functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMetaLearningBusTypes:
    """Test meta learning bus types functionality."""

    def test_meta_learning_types_imports(self):
        """Test meta learning types module imports."""
        from system_learning.meta_learning import types
        assert types is not None

    def test_meta_learning_event_type(self):
        """Test meta learning event type exists."""
        from system_learning.meta_learning.types import MetaLearningEvent
        assert MetaLearningEvent is not None

    def test_meta_learning_state_type(self):
        """Test meta learning state type exists."""
        from system_learning.meta_learning.types import MetaLearningState
        assert MetaLearningState is not None
