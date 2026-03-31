"""Test LLM judge Gemini integration functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestLlmJudgeGeminiIntegration:
    """Test LLM judge Gemini integration functionality."""

    def test_llm_judge_gemini_integration_imports(self):
        """Test LLM judge Gemini integration module imports."""
        from system_learning.confidence import gemini_judge
        assert gemini_judge is not None

    def test_gemini_judge_class(self):
        """Test Gemini judge class exists."""
        from system_learning.confidence.gemini_judge import GeminiJudge
        assert GeminiJudge is not None

    def test_gemini_judge_score_function(self):
        """Test Gemini judge score function."""
        from system_learning.confidence.gemini_judge import score_with_gemini
        assert callable(score_with_gemini)
