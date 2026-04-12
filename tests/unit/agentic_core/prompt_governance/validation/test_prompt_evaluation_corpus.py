"""Test PromptEvaluationCorpus functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPromptEvaluationCorpus:
    """Test PromptEvaluationCorpus functionality."""

    def test_prompt_evaluation_corpus_imports(self):
        """Test prompt_evaluation_corpus module imports."""
        from agentic_core import prompt_evaluation_corpus

        assert prompt_evaluation_corpus is not None

    def test_prompt_evaluation_corpus_class(self):
        """Test PromptEvaluationCorpus class exists."""
        from agentic_core import PromptEvaluationCorpus

        assert PromptEvaluationCorpus is not None

    def test_prompt_evaluation_corpus_callable(self):
        """Test prompt_evaluation_corpus functions are callable."""
        from agentic_core import validate_prompt_evaluation_corpus

        assert callable(validate_prompt_evaluation_corpus)
