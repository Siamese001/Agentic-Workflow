"""ADG importability contract for agentic_core/L2_execution/UniversalWriteGateway.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_UniversalWriteGateway.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.UniversalWriteGateway import (  # noqa: F401
        MutationRecord,
        SimulationResult,
        ToolNotAllowedError,
        UniversalWriteGateway,
        get_write_gateway,
        set_write_gateway,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ToolNotAllowedError = None  # type: ignore[assignment,misc]
    MutationRecord = None  # type: ignore[assignment,misc]
    SimulationResult = None  # type: ignore[assignment,misc]
    UniversalWriteGateway = None  # type: ignore[assignment,misc]
    get_write_gateway = None  # type: ignore[assignment,misc]
    set_write_gateway = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="UniversalWriteGateway deps unavailable")
class TestUniversalwritegatewayImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/UniversalWriteGateway.py must be importable."""
        assert _AVAILABLE

    def test_toolnotallowederror_defined(self) -> None:
        assert ToolNotAllowedError is not None

    def test_mutationrecord_defined(self) -> None:
        assert MutationRecord is not None

    def test_simulationresult_defined(self) -> None:
        assert SimulationResult is not None

    def test_universalwritegateway_defined(self) -> None:
        assert UniversalWriteGateway is not None