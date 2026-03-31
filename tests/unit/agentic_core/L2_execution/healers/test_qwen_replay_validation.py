"""Test QwenReplayValidation functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestQwenReplayValidation:
    """Test QwenReplayValidation functionality."""

    def test_qwen_replay_validation_imports(self):
        """Test qwen_replay_validation module imports."""
        from agentic_core import qwen_replay_validation
        assert qwen_replay_validation is not None

    def test_qwen_replay_validation_class(self):
        """Test QwenReplayValidation class exists."""
        from agentic_core import QwenReplayValidation
        assert QwenReplayValidation is not None

    def test_qwen_replay_validation_callable(self):
        """Test qwen_replay_validation functions are callable."""
        from agentic_core import validate_qwen_replay_validation
        assert callable(validate_qwen_replay_validation)
