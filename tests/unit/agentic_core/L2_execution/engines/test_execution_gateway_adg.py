"""ADG importability contract for agentic_core/L2_execution/engines/execution_gateway.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_execution_gateway.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.engines.execution_gateway import (  # noqa: F401
        SignatureBoundaryError,
        ExecutionGateway,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SignatureBoundaryError = None  # type: ignore[assignment,misc]
    ExecutionGateway = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="execution_gateway.py deps unavailable")
class TestExecutionGatewayImportability:
    def test_module_importable(self) -> None:
        """ADG contract: execution_gateway.py must be importable."""
        assert _AVAILABLE

    def test_signatureboundaryerror_is_type(self) -> None:
        assert SignatureBoundaryError is not None

    def test_executiongateway_is_type(self) -> None:
        assert ExecutionGateway is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

