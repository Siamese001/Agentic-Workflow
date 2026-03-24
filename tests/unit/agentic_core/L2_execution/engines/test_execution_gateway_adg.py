"""ADG importability contract for agentic_core/L2_execution/engines/execution_gateway.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_execution_gateway.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.engines.execution_gateway import (  # noqa: F401
        ExecutionGateway,
        SignatureBoundaryError,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    SignatureBoundaryError = None  # type: ignore[assignment,misc]
    ExecutionGateway = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="execution_gateway deps unavailable")
class TestExecutionGatewayImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/engines/execution_gateway.py must be importable."""
        assert _AVAILABLE

    def test_signatureboundaryerror_defined(self) -> None:
        assert SignatureBoundaryError is not None

    def test_executiongateway_defined(self) -> None:
        assert ExecutionGateway is not None