"""Registry enforcement at L0 execution gateway."""

import pytest

pytestmark = pytest.mark.unit_min_deps
from agentic_core.L0_routing.enforcement.execution_gateway import (
    UnregisteredAgentError,
    V15ExecutionGateway,
)


def test_registered_agent_passes():
    gw = V15ExecutionGateway()
    # SovereignLLMGateway is registered in AGENT_REGISTRY
    gw._enforce_agent_registered("SovereignLLMGateway")  # must not raise


def test_unregistered_agent_hard_fails():
    gw = V15ExecutionGateway()
    with pytest.raises(UnregisteredAgentError, match="not registered"):
        gw._enforce_agent_registered("GhostAgent_NotInRegistry")
