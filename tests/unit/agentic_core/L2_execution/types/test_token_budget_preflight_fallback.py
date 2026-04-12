"""Test TokenBudgetPreflightFallback functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestTokenBudgetPreflightFallback:
    """Test TokenBudgetPreflightFallback functionality."""

    def test_token_budget_preflight_fallback_imports(self):
        """Test token_budget_preflight_fallback module imports."""
        from agentic_core import token_budget_preflight_fallback

        assert token_budget_preflight_fallback is not None

    def test_token_budget_preflight_fallback_class(self):
        """Test TokenBudgetPreflightFallback class exists."""
        from agentic_core import TokenBudgetPreflightFallback

        assert TokenBudgetPreflightFallback is not None

    def test_token_budget_preflight_fallback_callable(self):
        """Test token_budget_preflight_fallback functions are callable."""
        from agentic_core import validate_token_budget_preflight_fallback

        assert callable(validate_token_budget_preflight_fallback)
