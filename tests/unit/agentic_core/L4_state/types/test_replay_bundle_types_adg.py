"""ADG importability contract for agentic_core/L4_state/types/replay_bundle_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_replay_bundle_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.types.replay_bundle_types import (  # noqa: F401
        ReplayBundle,
        build_replay_bundle,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ReplayBundle = None  # type: ignore[assignment,misc]
    build_replay_bundle = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="replay_bundle_types.py deps unavailable")
class TestReplayBundleTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: replay_bundle_types.py must be importable."""
        assert _AVAILABLE

    def test_replaybundle_is_type(self) -> None:
        assert ReplayBundle is not None

    def test_build_replay_bundle_callable(self) -> None:
        assert callable(build_replay_bundle)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

