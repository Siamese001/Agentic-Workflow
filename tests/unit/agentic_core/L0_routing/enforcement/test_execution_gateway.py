"""Runtime-hardened tests for ``ExecutionGateway``."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def enforcement_package():
    return pytest.importorskip("agentic_core.L0_routing.enforcement")


@pytest.fixture()
def gateway(enforcement_package):
    return enforcement_package.ExecutionGateway()


class TestExecutionGatewaySurface:
    def test_clock_property_exists(self, gateway):
        assert gateway.clock is not None

    def test_execute_is_callable(self, gateway):
        assert callable(getattr(gateway, "execute", None))

    def test_execution_gateway_error_initialization(self, enforcement_package):
        instance = enforcement_package.ExecutionGatewayError("test error")

        assert instance is not None
        assert isinstance(instance, Exception)

    def test_unregistered_agent_error_initialization(self, enforcement_package):
        instance = enforcement_package.UnregisteredAgentError()

        assert instance is not None
        assert isinstance(instance, Exception)

    @pytest.mark.parametrize("agent_id", ["", "   "])
    def test_execute_rejects_empty_or_blank_agent_id(self, gateway, enforcement_package, agent_id):
        with pytest.raises(enforcement_package.UnregisteredAgentError):
            gateway.execute(
                object(),
                lambda material: {},
                lambda: ("h", "g", "m"),
                agent_id=agent_id,
            )

    def test_max_heal_attempts_accepted_as_kwarg(self, gateway, enforcement_package):
        with pytest.raises(enforcement_package.UnregisteredAgentError):
            gateway.execute(
                object(),
                lambda material: {},
                lambda: ("h", "g", "m"),
                agent_id="",
                max_heal_attempts=0,
            )
