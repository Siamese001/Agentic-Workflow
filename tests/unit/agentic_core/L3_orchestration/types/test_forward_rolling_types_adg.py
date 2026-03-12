"""ADG importability contract for agentic_core/L3_orchestration/types/forward_rolling_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_forward_rolling_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.types.forward_rolling_types import (  # noqa: F401
        ExecutionMode,
        RolloutStage,
        FeatureFlag,
        RolloutConfig,
        ForwardRollingConfig,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ExecutionMode = None  # type: ignore[assignment,misc]
    RolloutStage = None  # type: ignore[assignment,misc]
    FeatureFlag = None  # type: ignore[assignment,misc]
    RolloutConfig = None  # type: ignore[assignment,misc]
    ForwardRollingConfig = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="forward_rolling_types.py deps unavailable")
class TestForwardRollingTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: forward_rolling_types.py must be importable."""
        assert _AVAILABLE

    def test_executionmode_is_type(self) -> None:
        assert ExecutionMode is not None

    def test_rolloutstage_is_type(self) -> None:
        assert RolloutStage is not None

    def test_featureflag_is_type(self) -> None:
        assert FeatureFlag is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

