"""Smoke tests for vllm_telemetry_end_to_end exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestVllmTelemetryEndToEnd:
    """Smoke tests for vllm_telemetry_end_to_end exports."""

    def test_vllm_telemetry_end_to_end_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "vllm_telemetry_end_to_end")
        assert module is not None

    def test_vllm_telemetry_end_to_end_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "VllmTelemetryEndToEnd")
        assert klass is not None

    def test_vllm_telemetry_end_to_end_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_vllm_telemetry_end_to_end")
        assert callable(validator)
