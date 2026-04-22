"""Smoke tests for vllm_profile_selection exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestVllmProfileSelection:
    """Smoke tests for vllm_profile_selection exports."""

    def test_vllm_profile_selection_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "vllm_profile_selection")
        assert module is not None

    def test_vllm_profile_selection_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "VllmProfileSelection")
        assert klass is not None

    def test_vllm_profile_selection_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_vllm_profile_selection")
        assert callable(validator)
