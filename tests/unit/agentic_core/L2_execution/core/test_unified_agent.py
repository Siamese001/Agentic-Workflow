"""Smoke tests for UnifiedAgent exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestUnifiedAgent:
    """Smoke tests for UnifiedAgent exports."""

    def test_unified_agent_imports(self) -> None:
        """Import module export."""
        module = import_attr_or_skip("agentic_core", "unified_agent")
        assert module is not None

    def test_unified_agent_class(self) -> None:
        """Import class export."""
        klass = import_attr_or_skip("agentic_core", "UnifiedAgent")
        assert klass is not None

    def test_unified_agent_callable(self) -> None:
        """Import validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_unified_agent")
        assert callable(validator)
