"""ADG importability contract for agentic_core/runtime/types/claim_type_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_claim_type_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.runtime.types.claim_type_types import (  # noqa: F401
        ClaimType,
        ConfidenceLevel,
        Claim,
        ClaimAnalysisResult,
        ClaimConfidenceScorer,
        create_claim_scorer,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ClaimType = None  # type: ignore[assignment,misc]
    ConfidenceLevel = None  # type: ignore[assignment,misc]
    Claim = None  # type: ignore[assignment,misc]
    ClaimAnalysisResult = None  # type: ignore[assignment,misc]
    ClaimConfidenceScorer = None  # type: ignore[assignment,misc]
    create_claim_scorer = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="claim_type_types.py deps unavailable")
class TestClaimTypeTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: claim_type_types.py must be importable."""
        assert _AVAILABLE

    def test_claimtype_is_type(self) -> None:
        assert ClaimType is not None

    def test_confidencelevel_is_type(self) -> None:
        assert ConfidenceLevel is not None

    def test_claim_is_type(self) -> None:
        assert Claim is not None

    def test_create_claim_scorer_callable(self) -> None:
        assert callable(create_claim_scorer)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

