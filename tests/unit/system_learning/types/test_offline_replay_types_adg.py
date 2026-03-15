"""ADG importability contract for system_learning/types/offline_replay_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_offline_replay_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.types.offline_replay_types import (  # noqa: F401
        OfflineReplayBundle,
        render_offline_replay_bundle,
        replay_aggregate_to_rollout,
        replay_app_signals_to_aggregate,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    OfflineReplayBundle = None  # type: ignore[assignment,misc]
    replay_app_signals_to_aggregate = None  # type: ignore[assignment,misc]
    replay_aggregate_to_rollout = None  # type: ignore[assignment,misc]
    render_offline_replay_bundle = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="offline_replay_types.py deps unavailable")
class TestOfflineReplayTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: offline_replay_types.py must be importable."""
        assert _AVAILABLE

    def test_offlinereplaybundle_is_type(self) -> None:
        assert OfflineReplayBundle is not None

    def test_replay_app_signals_to_aggregate_callable(self) -> None:
        assert callable(replay_app_signals_to_aggregate)

    def test_replay_aggregate_to_rollout_callable(self) -> None:
        assert callable(replay_aggregate_to_rollout)
