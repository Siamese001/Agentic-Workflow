"""Test LLM judge Gemini e2e novel functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestLlmJudgeGeminiE2ENovel:
    """Test LLM judge Gemini e2e novel functionality."""
