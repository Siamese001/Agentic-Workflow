"""Smoke tests for vllm_infrastructure_fingerprint_types exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestVllmInfrastructureFingerprintTypes:
    """Smoke tests for vllm_infrastructure_fingerprint_types exports."""

    def test_vllm_infrastructure_fingerprint_types_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "vllm_infrastructure_fingerprint_types")
        assert module is not None

    def test_vllm_infrastructure_fingerprint_types_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "VllmInfrastructureFingerprintTypes")
        assert klass is not None

    def test_vllm_infrastructure_fingerprint_types_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_vllm_infrastructure_fingerprint_types")
        assert callable(validator)
