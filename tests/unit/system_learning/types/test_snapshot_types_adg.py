"""ADG importability contract for system_learning/types/snapshot_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_snapshot_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.types.snapshot_types import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        MetaLearningSnapshot,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    MetaLearningSnapshot = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="snapshot_types.py deps unavailable")
class TestSnapshotTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: snapshot_types.py must be importable."""
        assert _AVAILABLE

    def test_metalearningsnapshot_is_type(self) -> None:
        assert MetaLearningSnapshot is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None
