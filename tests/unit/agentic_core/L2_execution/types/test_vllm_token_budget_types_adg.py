"""Smoke tests for vllm_token_budget_types_adg exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestVllmTokenBudgetTypesAdg:
    """Smoke tests for vllm_token_budget_types_adg exports."""

    def test_vllm_token_budget_types_adg_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "vllm_token_budget_types_adg")
        assert module is not None

    def test_vllm_token_budget_types_adg_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "VllmTokenBudgetTypesAdg")
        assert klass is not None

    def test_vllm_token_budget_types_adg_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_vllm_token_budget_types_adg")
        assert callable(validator)
