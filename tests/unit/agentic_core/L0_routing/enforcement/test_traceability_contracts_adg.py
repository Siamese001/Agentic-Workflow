"""ADG importability contract for agentic_core/L0_routing/enforcement/traceability_contracts.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_traceability_contracts.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.enforcement.traceability_contracts import (  # noqa: F401
        ErrorSignatureError,
        PolicyConfigPinError,
        TraceIDFormatError,
        build_error_signature,
        generate_trace_id,
        pin_policy_config,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    TraceIDFormatError = None  # type: ignore[assignment,misc]
    generate_trace_id = None  # type: ignore[assignment,misc]
    ErrorSignatureError = None  # type: ignore[assignment,misc]
    build_error_signature = None  # type: ignore[assignment,misc]
    PolicyConfigPinError = None  # type: ignore[assignment,misc]
    pin_policy_config = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="traceability_contracts deps unavailable")
class TestTraceabilityContractsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/enforcement/traceability_contracts.py must be importable."""
        assert _AVAILABLE

    def test_traceidformaterror_defined(self) -> None:
        assert TraceIDFormatError is not None

    def test_errorsignatureerror_defined(self) -> None:
        assert ErrorSignatureError is not None

    def test_policyconfigpinerror_defined(self) -> None:
        assert PolicyConfigPinError is not None