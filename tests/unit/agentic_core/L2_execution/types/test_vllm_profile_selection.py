"""Test VllmProfileSelection functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestVllmProfileSelection:
    """Test VllmProfileSelection functionality."""

    def test_vllm_profile_selection_imports(self):
        """Test vllm_profile_selection module imports."""
        from agentic_core import vllm_profile_selection

        assert vllm_profile_selection is not None

    def test_vllm_profile_selection_class(self):
        """Test VllmProfileSelection class exists."""
        from agentic_core import VllmProfileSelection

        assert VllmProfileSelection is not None

    def test_vllm_profile_selection_callable(self):
        """Test vllm_profile_selection functions are callable."""
        from agentic_core import validate_vllm_profile_selection

        assert callable(validate_vllm_profile_selection)
