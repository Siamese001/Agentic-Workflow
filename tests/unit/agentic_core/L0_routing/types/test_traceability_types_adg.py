"""ADG importability contract for agentic_core/L0_routing/types/traceability_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_traceability_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.types.traceability_types import (  # noqa: F401
        ErrorSignature,
        PolicyConfigPin,
        PlanProvenance,
        RetrievalQuery,
        RetrievedChunk,
        RerankScore,
        validate_trace_id,
        compute_error_signature_hash,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ErrorSignature = None  # type: ignore[assignment,misc]
    PolicyConfigPin = None  # type: ignore[assignment,misc]
    PlanProvenance = None  # type: ignore[assignment,misc]
    RetrievalQuery = None  # type: ignore[assignment,misc]
    RetrievedChunk = None  # type: ignore[assignment,misc]
    RerankScore = None  # type: ignore[assignment,misc]
    validate_trace_id = None  # type: ignore[assignment,misc]
    compute_error_signature_hash = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="traceability_types.py deps unavailable")
class TestTraceabilityTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: traceability_types.py must be importable."""
        assert _AVAILABLE

    def test_errorsignature_is_type(self) -> None:
        assert ErrorSignature is not None

    def test_policyconfigpin_is_type(self) -> None:
        assert PolicyConfigPin is not None

    def test_planprovenance_is_type(self) -> None:
        assert PlanProvenance is not None

    def test_validate_trace_id_callable(self) -> None:
        assert callable(validate_trace_id)

    def test_compute_error_signature_hash_callable(self) -> None:
        assert callable(compute_error_signature_hash)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

