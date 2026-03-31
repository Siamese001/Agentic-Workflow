"""Test LLM judge Gemini e2e novel functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestLlmJudgeGeminiE2ENovel:
    """Test LLM judge Gemini e2e novel functionality."""

    def test_llm_judge_gemini_e2e_imports(self):
        """Test LLM judge Gemini e2e module imports."""
        from system_learning.confidence import gemini_judge
        assert gemini_judge is not None

    def test_gemini_e2e_judge_class(self):
        """Test Gemini e2e judge class exists."""
        from system_learning.confidence.gemini_judge import GeminiE2EJudge
        assert GeminiE2EJudge is not None

    def test_gemini_e2e_evaluate_function(self):
        """Test Gemini e2e evaluate function."""
        from system_learning.confidence.gemini_judge import evaluate_e2e
        assert callable(evaluate_e2e)
