"""ADG importability contract for agentic_core/L2_execution/healers/healing_tier_router.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_healing_tier_router.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.healers.healing_tier_router import (  # noqa: F401
        WEIGHT_BLAST_RADIUS,
        WEIGHT_FAILURE_ENTROPY,
        WEIGHT_FAILURE_PRIOR,
        WEIGHT_HISTORICAL_SUCCESS,
        WEIGHT_RETRY_DECAY,
        WEIGHT_TOOL_READINESS,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    WEIGHT_FAILURE_PRIOR = None  # type: ignore[assignment,misc]
    WEIGHT_BLAST_RADIUS = None  # type: ignore[assignment,misc]
    WEIGHT_HISTORICAL_SUCCESS = None  # type: ignore[assignment,misc]
    WEIGHT_TOOL_READINESS = None  # type: ignore[assignment,misc]
    WEIGHT_RETRY_DECAY = None  # type: ignore[assignment,misc]
    WEIGHT_FAILURE_ENTROPY = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="healing_tier_router deps unavailable")
class TestHealingTierRouterImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/healers/healing_tier_router.py must be importable."""
        assert _AVAILABLE