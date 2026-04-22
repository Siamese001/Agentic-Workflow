"""Smoke tests for vllm_backpressure_types exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestVllmBackpressureTypes:
    """Smoke tests for vllm_backpressure_types exports."""

    def test_vllm_backpressure_types_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "vllm_backpressure_types")
        assert module is not None

    def test_vllm_backpressure_types_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "VllmBackpressureTypes")
        assert klass is not None

    def test_vllm_backpressure_types_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_vllm_backpressure_types")
        assert callable(validator)
