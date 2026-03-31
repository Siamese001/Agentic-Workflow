"""Test LLM judge system functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestLlmJudgeSystem:
    """Test LLM judge system functionality."""

    def test_llm_judge_imports(self):
        """Test LLM judge module imports."""
        from system_learning.confidence import llm_judge
        assert llm_judge is not None

    def test_llm_judge_evaluate_function(self):
        """Test LLM judge evaluate function."""
        from system_learning.confidence.llm_judge import evaluate
        assert callable(evaluate)

    def test_llm_judge_score_function(self):
        """Test LLM judge score function."""
        from system_learning.confidence.llm_judge import score_output
        assert callable(score_output)
