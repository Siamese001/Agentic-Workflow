"""Runtime-hardened ADG smoke tests for ExecutionGateway surface."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def enforcement_package():
    return pytest.importorskip("agentic_core.L0_routing.enforcement")


@pytest.fixture()
def gateway(enforcement_package):
    return enforcement_package.ExecutionGateway()


class TestExecutionGatewayADGSurface:
    def test_clock_property_exists(self, gateway):
        assert gateway.clock is not None

    def test_execute_is_callable(self, gateway):
        assert callable(getattr(gateway, "execute", None))

    def test_exception_types_initialize(self, enforcement_package):
        assert isinstance(enforcement_package.ExecutionGatewayError("test error"), Exception)
        assert isinstance(enforcement_package.UnregisteredAgentError(), Exception)
