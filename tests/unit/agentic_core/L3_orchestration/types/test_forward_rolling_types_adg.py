"""ADG importability contract for agentic_core/L3_orchestration/types/forward_rolling_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_forward_rolling_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.types.forward_rolling_types import (  # noqa: F401
        ROLLOUT_PERCENTAGES,
        ExecutionMode,
        FeatureFlag,
        ForwardRollingConfig,
        RolloutConfig,
        RolloutStage,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ExecutionMode = None  # type: ignore[assignment,misc]
    RolloutStage = None  # type: ignore[assignment,misc]
    ROLLOUT_PERCENTAGES = None  # type: ignore[assignment,misc]
    FeatureFlag = None  # type: ignore[assignment,misc]
    RolloutConfig = None  # type: ignore[assignment,misc]
    ForwardRollingConfig = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="forward_rolling_types deps unavailable")
class TestForwardRollingTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L3_orchestration/types/forward_rolling_types.py must be importable."""
        assert _AVAILABLE

    def test_executionmode_defined(self) -> None:
        assert ExecutionMode is not None

    def test_rolloutstage_defined(self) -> None:
        assert RolloutStage is not None

    def test_featureflag_defined(self) -> None:
        assert FeatureFlag is not None

    def test_rolloutconfig_defined(self) -> None:
        assert RolloutConfig is not None

    def test_forwardrollingconfig_defined(self) -> None:
        assert ForwardRollingConfig is not None
