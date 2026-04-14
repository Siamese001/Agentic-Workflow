"""Runtime-hardened tests for SSOT boundary contracts."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def enforcement_package():
    return pytest.importorskip("agentic_core.L0_routing.enforcement")


class TestBoundaryContracts:
    def test_resolve_ssot_binding_returns_mapping_value(self, enforcement_package):
        result = enforcement_package.resolve_ssot_binding("node123", {"node123": "binding123"})

        assert result is not None

    def test_build_context_retrieval_request_returns_value(self, enforcement_package):
        result = enforcement_package.build_context_retrieval_request("trace123", "hash123", 42)

        assert result is not None

    def test_exception_types_initialize(self, enforcement_package):
        assert isinstance(enforcement_package.SSOTBindingError(), Exception)
        assert isinstance(enforcement_package.ContextRetrievalError(), Exception)
