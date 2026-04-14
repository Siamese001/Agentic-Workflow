"""Smoke tests for vllm_token_budget_types exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestVllmTokenBudgetTypes:
    """Smoke tests for vllm_token_budget_types exports."""

    def test_vllm_token_budget_types_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "vllm_token_budget_types")
        assert module is not None

    def test_vllm_token_budget_types_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "VllmTokenBudgetTypes")
        assert klass is not None

    def test_vllm_token_budget_types_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_vllm_token_budget_types")
        assert callable(validator)
