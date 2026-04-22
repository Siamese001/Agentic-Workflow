"""Smoke tests for token_budget_preflight_fallback exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestTokenBudgetPreflightFallback:
    """Smoke tests for token_budget_preflight_fallback exports."""

    def test_token_budget_preflight_fallback_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "token_budget_preflight_fallback")
        assert module is not None

    def test_token_budget_preflight_fallback_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "TokenBudgetPreflightFallback")
        assert klass is not None

    def test_token_budget_preflight_fallback_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_token_budget_preflight_fallback")
        assert callable(validator)
