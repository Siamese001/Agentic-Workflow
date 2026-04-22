"""Smoke tests for capability_token_types exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestCapabilityTokenTypes:
    """Smoke tests for capability_token_types exports."""

    def test_capability_token_types_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "capability_token_types")
        assert module is not None

    def test_capability_token_types_docstring_present(self) -> None:
        """Ensure the module docstring is present."""
        module = import_attr_or_skip("agentic_core", "capability_token_types")
        assert module.__doc__ is not None

    def test_capability_token_types_public_attributes_accessible(self) -> None:
        """Ensure public attributes can be enumerated."""
        module = import_attr_or_skip("agentic_core", "capability_token_types")
        attrs = [name for name in dir(module) if not name.startswith("_")]
        assert isinstance(attrs, list)
