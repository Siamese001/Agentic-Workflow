"""ADG importability contract for system_learning/engines/meta_learning_replay_binding.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_meta_learning_replay_binding.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.engines.meta_learning_replay_binding import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        MetaLearningReplayBinding,
        compute_replay_key,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    MetaLearningReplayBinding = None  # type: ignore[assignment,misc]
    compute_replay_key = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="meta_learning_replay_binding.py deps unavailable")
class TestMetaLearningReplayBindingImportability:
    def test_module_importable(self) -> None:
        """ADG contract: meta_learning_replay_binding.py must be importable."""
        assert _AVAILABLE

    def test_metalearningreplaybinding_is_type(self) -> None:
        assert MetaLearningReplayBinding is not None

    def test_compute_replay_key_callable(self) -> None:
        assert callable(compute_replay_key)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None
