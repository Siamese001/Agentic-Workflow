"""Runtime-hardened tests for traceability contracts."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def enforcement_package():
    return pytest.importorskip("agentic_core.L0_routing.enforcement")


class TestTraceabilityContracts:
    def test_generate_trace_id_returns_string(self, enforcement_package, monkeypatch):
        monkeypatch.setenv("DISABLE_RUNTIME_MUTATION_GUARD", "1")
        result = enforcement_package.generate_trace_id("ABCDEF12")

        assert isinstance(result, str)
        assert result

    def test_build_error_signature_returns_value(self, enforcement_package, monkeypatch):
        monkeypatch.setenv("DISABLE_RUNTIME_MUTATION_GUARD", "1")
        result = enforcement_package.build_error_signature("TypeError", "node123", 42)

        assert result is not None

    def test_exception_types_initialize(self, enforcement_package):
        assert isinstance(enforcement_package.TraceIDFormatError(), Exception)
        assert isinstance(enforcement_package.ErrorSignatureError(), Exception)

    def test_generate_trace_id_boundary_conditions(self, enforcement_package, monkeypatch):
        monkeypatch.setenv("DISABLE_RUNTIME_MUTATION_GUARD", "1")
        with pytest.raises(ValueError):
            enforcement_package.generate_trace_id("WXYZ1234")
        with pytest.raises(enforcement_package.TraceIDFormatError):
            enforcement_package.generate_trace_id("ABC")
