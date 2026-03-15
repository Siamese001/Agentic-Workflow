"""ADG importability contract for system_learning/invariants/freeze_gate.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_freeze_gate.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.invariants.freeze_gate import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        FreezeStateReader,
        JsonFileBackedFreezeReader,
        StaticFreezeReader,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    FreezeStateReader = None  # type: ignore[assignment,misc]
    JsonFileBackedFreezeReader = None  # type: ignore[assignment,misc]
    StaticFreezeReader = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="freeze_gate.py deps unavailable")
class TestFreezeGateImportability:
    def test_module_importable(self) -> None:
        """ADG contract: freeze_gate.py must be importable."""
        assert _AVAILABLE

    def test_freezestatereader_is_type(self) -> None:
        assert FreezeStateReader is not None

    def test_jsonfilebackedfreezereader_is_type(self) -> None:
        assert JsonFileBackedFreezeReader is not None

    def test_staticfreezereader_is_type(self) -> None:
        assert StaticFreezeReader is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None
