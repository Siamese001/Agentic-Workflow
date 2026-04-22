"""Smoke tests for resource_prediction_types exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestResourcePredictionTypes:
    """Smoke tests for resource_prediction_types exports."""

    def test_resource_prediction_types_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "resource_prediction_types")
        assert module is not None

    def test_resource_prediction_types_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "ResourcePredictionTypes")
        assert klass is not None

    def test_resource_prediction_types_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_resource_prediction_types")
        assert callable(validator)
