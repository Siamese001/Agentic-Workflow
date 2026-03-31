"""Test HardenedGeminiExecutor functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHardenedGeminiExecutor:
    """Test HardenedGeminiExecutor functionality."""

    def test_hardened_gemini_executor_imports(self):
        """Test hardened_gemini_executor module imports."""
        from agentic_core import hardened_gemini_executor
        assert hardened_gemini_executor is not None

    def test_hardened_gemini_executor_class(self):
        """Test HardenedGeminiExecutor class exists."""
        from agentic_core import HardenedGeminiExecutor
        assert HardenedGeminiExecutor is not None

    def test_hardened_gemini_executor_callable(self):
        """Test hardened_gemini_executor functions are callable."""
        from agentic_core import validate_hardened_gemini_executor
        assert callable(validate_hardened_gemini_executor)
