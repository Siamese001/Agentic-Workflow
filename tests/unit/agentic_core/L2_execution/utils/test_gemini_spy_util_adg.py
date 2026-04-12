"""Test GeminiSpyUtilAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGeminiSpyUtilAdg:
    """Test GeminiSpyUtilAdg functionality."""

    def test_gemini_spy_util_adg_imports(self):
        """Test gemini_spy_util_adg module imports."""
        from agentic_core import gemini_spy_util_adg

        assert gemini_spy_util_adg is not None

    def test_gemini_spy_util_adg_class(self):
        """Test GeminiSpyUtilAdg class exists."""
        from agentic_core import GeminiSpyUtilAdg

        assert GeminiSpyUtilAdg is not None

    def test_gemini_spy_util_adg_callable(self):
        """Test gemini_spy_util_adg functions are callable."""
        from agentic_core import validate_gemini_spy_util_adg

        assert callable(validate_gemini_spy_util_adg)
