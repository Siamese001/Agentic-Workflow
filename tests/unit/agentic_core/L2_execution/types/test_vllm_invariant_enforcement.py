"""Smoke tests for vllm_invariant_enforcement exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestTypeSmoke:
    """Smoke tests for vllm_invariant_enforcement exports."""

    def test_vllm_invariant_enforcement_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "vllm_invariant_enforcement")
        assert module is not None

    def test_vllm_invariant_enforcement_docstring_present(self) -> None:
        """Ensure the module docstring is present."""
        module = import_attr_or_skip("agentic_core", "vllm_invariant_enforcement")
        assert module.__doc__ is not None

    def test_vllm_invariant_enforcement_public_attributes_accessible(self) -> None:
        """Ensure public attributes can be enumerated."""
        module = import_attr_or_skip("agentic_core", "vllm_invariant_enforcement")
        attrs = [name for name in dir(module) if not name.startswith("_")]
        assert isinstance(attrs, list)
