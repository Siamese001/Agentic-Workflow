"""Smoke tests for self_healing_trigger exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestSelfHealingTrigger:
    """Smoke tests for self_healing_trigger exports."""

    def test_self_healing_trigger_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "self_healing_trigger")
        assert module is not None

    def test_self_healing_trigger_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "SelfHealingTrigger")
        assert klass is not None

    def test_self_healing_trigger_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_self_healing_trigger")
        assert callable(validator)
