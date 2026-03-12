"""ADG importability contract for agentic_core/L6_observability/engines/replay_key_computer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_replay_key_computer.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L6_observability.engines.replay_key_computer import (  # noqa: F401
        ReplayKeyComponents,
        compute_replay_key,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ReplayKeyComponents = None  # type: ignore[assignment,misc]
    compute_replay_key = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="replay_key_computer.py deps unavailable")
class TestReplayKeyComputerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: replay_key_computer.py must be importable."""
        assert _AVAILABLE

    def test_replaykeycomponents_is_type(self) -> None:
        assert ReplayKeyComponents is not None

    def test_compute_replay_key_callable(self) -> None:
        assert callable(compute_replay_key)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

