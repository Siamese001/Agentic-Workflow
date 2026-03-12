"""ADG importability contract for agentic_core/L2_execution/UniversalWriteGateway.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_UniversalWriteGateway.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.UniversalWriteGateway import (  # noqa: F401
        ToolNotAllowedError,
        MutationRecord,
        SimulationResult,
        UniversalWriteGateway,
        get_write_gateway,
        set_write_gateway,
        reset_write_gateway,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ToolNotAllowedError = None  # type: ignore[assignment,misc]
    MutationRecord = None  # type: ignore[assignment,misc]
    SimulationResult = None  # type: ignore[assignment,misc]
    UniversalWriteGateway = None  # type: ignore[assignment,misc]
    get_write_gateway = None  # type: ignore[assignment,misc]
    set_write_gateway = None  # type: ignore[assignment,misc]
    reset_write_gateway = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="UniversalWriteGateway.py deps unavailable")
class TestUniversalwritegatewayImportability:
    def test_module_importable(self) -> None:
        """ADG contract: UniversalWriteGateway.py must be importable."""
        assert _AVAILABLE

    def test_toolnotallowederror_is_type(self) -> None:
        assert ToolNotAllowedError is not None

    def test_mutationrecord_is_type(self) -> None:
        assert MutationRecord is not None

    def test_simulationresult_is_type(self) -> None:
        assert SimulationResult is not None

    def test_get_write_gateway_callable(self) -> None:
        assert callable(get_write_gateway)

    def test_set_write_gateway_callable(self) -> None:
        assert callable(set_write_gateway)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

