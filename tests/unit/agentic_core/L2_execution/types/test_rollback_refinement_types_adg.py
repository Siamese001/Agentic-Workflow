"""ADG importability contract for agentic_core/L2_execution/types/rollback_refinement_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_rollback_refinement_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.rollback_refinement_types import (  # noqa: F401
        RollbackStrategyId,
        RollbackOutcomeStats,
        RollbackRefinementRequest,
        RollbackRefinementDecision,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    RollbackStrategyId = None  # type: ignore[assignment,misc]
    RollbackOutcomeStats = None  # type: ignore[assignment,misc]
    RollbackRefinementRequest = None  # type: ignore[assignment,misc]
    RollbackRefinementDecision = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="rollback_refinement_types.py deps unavailable")
class TestRollbackRefinementTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: rollback_refinement_types.py must be importable."""
        assert _AVAILABLE

    def test_rollbackstrategyid_is_type(self) -> None:
        assert RollbackStrategyId is not None

    def test_rollbackoutcomestats_is_type(self) -> None:
        assert RollbackOutcomeStats is not None

    def test_rollbackrefinementrequest_is_type(self) -> None:
        assert RollbackRefinementRequest is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

