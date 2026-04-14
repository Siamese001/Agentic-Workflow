"""Smoke tests for tool_intent_model exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestToolIntentModel:
    """Smoke tests for tool_intent_model exports."""

    def test_tool_intent_model_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "tool_intent_model")
        assert module is not None

    def test_tool_intent_model_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "ToolIntentModel")
        assert klass is not None

    def test_tool_intent_model_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_tool_intent_model")
        assert callable(validator)
