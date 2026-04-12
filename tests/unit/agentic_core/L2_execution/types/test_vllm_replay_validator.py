"""Test VllmReplayValidator functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestVllmReplayValidator:
    """Test VllmReplayValidator functionality."""

    def test_vllm_replay_validator_imports(self):
        """Test vllm_replay_validator module imports."""
        from agentic_core import vllm_replay_validator

        assert vllm_replay_validator is not None

    def test_vllm_replay_validator_class(self):
        """Test VllmReplayValidator class exists."""
        from agentic_core import VllmReplayValidator

        assert VllmReplayValidator is not None

    def test_vllm_replay_validator_callable(self):
        """Test vllm_replay_validator functions are callable."""
        from agentic_core import validate_vllm_replay_validator

        assert callable(validate_vllm_replay_validator)
