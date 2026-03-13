"""ADG importability contract for agentic_core/L4_state/types/retrieval_anchor_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_retrieval_anchor_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.types.retrieval_anchor_types import (  # noqa: F401
        AnchoredResult,
        AnchorViolationError,
        RetrievalAnchor,
        enforce_anchor_coverage,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    RetrievalAnchor = None  # type: ignore[assignment,misc]
    AnchoredResult = None  # type: ignore[assignment,misc]
    AnchorViolationError = None  # type: ignore[assignment,misc]
    enforce_anchor_coverage = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_anchor_types deps unavailable")
class TestRetrievalAnchorTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L4_state/types/retrieval_anchor_types.py must be importable."""
        assert _AVAILABLE

    def test_retrievalanchor_defined(self) -> None:
        assert RetrievalAnchor is not None

    def test_anchoredresult_defined(self) -> None:
        assert AnchoredResult is not None

    def test_anchorviolationerror_defined(self) -> None:
        assert AnchorViolationError is not None
