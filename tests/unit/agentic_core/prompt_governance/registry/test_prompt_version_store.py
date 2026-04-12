"""Test PromptVersionStore functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPromptVersionStore:
    """Test PromptVersionStore functionality."""

    def test_prompt_version_store_imports(self):
        """Test prompt_version_store module imports."""
        from agentic_core import prompt_version_store

        assert prompt_version_store is not None

    def test_prompt_version_store_class(self):
        """Test PromptVersionStore class exists."""
        from agentic_core import PromptVersionStore

        assert PromptVersionStore is not None

    def test_prompt_version_store_callable(self):
        """Test prompt_version_store functions are callable."""
        from agentic_core import validate_prompt_version_store

        assert callable(validate_prompt_version_store)
