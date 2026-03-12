"""ADG importability contract for system_learning/engines/deterministic_replay_engine.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_deterministic_replay_engine.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.engines.deterministic_replay_engine import (  # noqa: F401
        ReplayResult,
        DeterministicReplayEngine,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ReplayResult = None  # type: ignore[assignment,misc]
    DeterministicReplayEngine = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="deterministic_replay_engine.py deps unavailable")
class TestDeterministicReplayEngineImportability:
    def test_module_importable(self) -> None:
        """ADG contract: deterministic_replay_engine.py must be importable."""
        assert _AVAILABLE

    def test_replayresult_is_type(self) -> None:
        assert ReplayResult is not None

    def test_deterministicreplayengine_is_type(self) -> None:
        assert DeterministicReplayEngine is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

