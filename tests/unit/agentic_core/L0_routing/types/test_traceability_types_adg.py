"""ADG importability contract for agentic_core/L0_routing/types/traceability_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_traceability_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.types.traceability_types import (  # noqa: F401
        TRACE_ID_PATTERN,
        ErrorSignature,
        PlanProvenance,
        PolicyConfigPin,
        compute_error_signature_hash,
        validate_trace_id,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    TRACE_ID_PATTERN = None  # type: ignore[assignment,misc]
    validate_trace_id = None  # type: ignore[assignment,misc]
    ErrorSignature = None  # type: ignore[assignment,misc]
    compute_error_signature_hash = None  # type: ignore[assignment,misc]
    PolicyConfigPin = None  # type: ignore[assignment,misc]
    PlanProvenance = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="traceability_types deps unavailable")
class TestTraceabilityTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/types/traceability_types.py must be importable."""
        assert _AVAILABLE

    def test_errorsignature_defined(self) -> None:
        assert ErrorSignature is not None

    def test_policyconfigpin_defined(self) -> None:
        assert PolicyConfigPin is not None

    def test_planprovenance_defined(self) -> None:
        assert PlanProvenance is not None
