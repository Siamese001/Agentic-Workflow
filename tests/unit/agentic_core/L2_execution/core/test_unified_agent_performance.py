"""Smoke tests for UnifiedAgentPerformance exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestUnifiedAgentPerformance:
    """Smoke tests for UnifiedAgentPerformance exports."""

    def test_unified_agent_performance_imports(self) -> None:
        """Import module export."""
        module = import_attr_or_skip("agentic_core", "unified_agent_performance")
        assert module is not None

    def test_unified_agent_performance_class(self) -> None:
        """Import class export."""
        klass = import_attr_or_skip("agentic_core", "UnifiedAgentPerformance")
        assert klass is not None

    def test_unified_agent_performance_callable(self) -> None:
        """Import validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_unified_agent_performance")
        assert callable(validator)
