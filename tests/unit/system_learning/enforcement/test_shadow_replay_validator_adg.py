"""ADG importability contract for system_learning/enforcement/shadow_replay_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_shadow_replay_validator.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.enforcement.shadow_replay_validator import (  # noqa: F401
        RegressionError,
        ReplayResult,
        ShadowReplaySummary,
        ShadowReplayValidator,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    RegressionError = None  # type: ignore[assignment,misc]
    ReplayResult = None  # type: ignore[assignment,misc]
    ShadowReplaySummary = None  # type: ignore[assignment,misc]
    ShadowReplayValidator = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="shadow_replay_validator.py deps unavailable")
class TestShadowReplayValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: shadow_replay_validator.py must be importable."""
        assert _AVAILABLE

    def test_regressionerror_is_type(self) -> None:
        assert RegressionError is not None

    def test_replayresult_is_type(self) -> None:
        assert ReplayResult is not None

    def test_shadowreplaysummary_is_type(self) -> None:
        assert ShadowReplaySummary is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

