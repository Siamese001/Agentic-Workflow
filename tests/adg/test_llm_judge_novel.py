"""Test LLM judge novel functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestLlmJudgeNovel:
    """Test LLM judge novel functionality."""

    def test_llm_judge_novel_imports(self):
        """Test LLM judge novel module imports."""
        from system_learning.confidence import novel_judge
        assert novel_judge is not None

    def test_novel_judge_class(self):
        """Test novel judge class exists."""
        from system_learning.confidence.novel_judge import NovelJudge
        assert NovelJudge is not None

    def test_novel_judge_evaluate_function(self):
        """Test novel judge evaluate function."""
        from system_learning.confidence.novel_judge import evaluate_novel
        assert callable(evaluate_novel)
