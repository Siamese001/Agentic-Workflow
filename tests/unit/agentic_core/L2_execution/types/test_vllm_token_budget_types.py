"""Test VllmTokenBudgetTypes functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestVllmTokenBudgetTypes:
    """Test VllmTokenBudgetTypes functionality."""

    def test_vllm_token_budget_types_imports(self):
        """Test vllm_token_budget_types module imports."""
        from agentic_core import vllm_token_budget_types

        assert vllm_token_budget_types is not None

    def test_vllm_token_budget_types_class(self):
        """Test VllmTokenBudgetTypes class exists."""
        from agentic_core import VllmTokenBudgetTypes

        assert VllmTokenBudgetTypes is not None

    def test_vllm_token_budget_types_callable(self):
        """Test vllm_token_budget_types functions are callable."""
        from agentic_core import validate_vllm_token_budget_types

        assert callable(validate_vllm_token_budget_types)
