"""Smoke tests for resource predictor exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestResourcePredictorAdg:
    """Smoke tests for resource predictor exports."""

    def test_predict_export(self) -> None:
        """Import predict export."""
        func = import_attr_or_skip("agentic_core.L2_execution.reasoning", "predict")
        assert callable(func)

    def test_ResourcePredictor_init(self) -> None:
        """Import ResourcePredictor class."""
        klass = import_attr_or_skip("agentic_core.L2_execution.reasoning", "ResourcePredictor")
        assert klass is not None

    def test_ResourcePredictor_predict(self) -> None:
        """Validate ResourcePredictor.predict method is present."""
        klass = import_attr_or_skip("agentic_core.L2_execution.reasoning", "ResourcePredictor")
        assert hasattr(klass, "predict")

    def test_DefaultDeterministicResourcePredictor_init(self) -> None:
        """Import DefaultDeterministicResourcePredictor class."""
        klass = import_attr_or_skip(
            "agentic_core.L2_execution.reasoning", "DefaultDeterministicResourcePredictor"
        )
        assert klass is not None

    def test_DefaultDeterministicResourcePredictor_predict(self) -> None:
        """Validate DefaultDeterministicResourcePredictor.predict method is present."""
        klass = import_attr_or_skip(
            "agentic_core.L2_execution.reasoning", "DefaultDeterministicResourcePredictor"
        )
        assert hasattr(klass, "predict")
