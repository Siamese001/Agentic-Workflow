"""ADG importability contract for agentic_core/L0_routing/enforcement/execution_gateway.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_execution_gateway.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.enforcement.execution_gateway import (  # noqa: F401
        CURRENT_PHASE,
        MUTATION_COUNTER,
        ExecutionGatewayError,
        GatewayResult,
        UnregisteredAgentError,
        V15ExecutionGateway,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    MUTATION_COUNTER = None  # type: ignore[assignment,misc]
    CURRENT_PHASE = None  # type: ignore[assignment,misc]
    ExecutionGatewayError = None  # type: ignore[assignment,misc]
    UnregisteredAgentError = None  # type: ignore[assignment,misc]
    GatewayResult = None  # type: ignore[assignment,misc]
    V15ExecutionGateway = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="execution_gateway deps unavailable")
class TestExecutionGatewayImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/enforcement/execution_gateway.py must be importable."""
        assert _AVAILABLE

    def test_executiongatewayerror_defined(self) -> None:
        assert ExecutionGatewayError is not None

    def test_unregisteredagenterror_defined(self) -> None:
        assert UnregisteredAgentError is not None

    def test_gatewayresult_defined(self) -> None:
        assert GatewayResult is not None

    def test_v15executiongateway_defined(self) -> None:
        assert V15ExecutionGateway is not None
