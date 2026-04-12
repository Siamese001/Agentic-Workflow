"""Test LlmJudgeAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestLlmJudgeAdg:
    """Test LlmJudgeAdg functionality."""

    def test_llm_judge_adg_imports(self):
        """Test llm_judge_adg module imports."""
        from agentic_core import llm_judge_adg

        assert llm_judge_adg is not None

    def test_llm_judge_adg_class(self):
        """Test LlmJudgeAdg class exists."""
        from agentic_core import LlmJudgeAdg

        assert LlmJudgeAdg is not None

    def test_llm_judge_adg_callable(self):
        """Test llm_judge_adg functions are callable."""
        from agentic_core import validate_llm_judge_adg

        assert callable(validate_llm_judge_adg)
