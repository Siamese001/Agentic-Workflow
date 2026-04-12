"""Test LlmReplayTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestLlmReplayTypesAdg:
    """Test LlmReplayTypesAdg functionality."""

    def test_llm_replay_types_adg_imports(self):
        """Test llm_replay_types_adg module imports."""
        from agentic_core import llm_replay_types_adg

        assert llm_replay_types_adg is not None

    def test_llm_replay_types_adg_class(self):
        """Test LlmReplayTypesAdg class exists."""
        from agentic_core import LlmReplayTypesAdg

        assert LlmReplayTypesAdg is not None

    def test_llm_replay_types_adg_callable(self):
        """Test llm_replay_types_adg functions are callable."""
        from agentic_core import validate_llm_replay_types_adg

        assert callable(validate_llm_replay_types_adg)
