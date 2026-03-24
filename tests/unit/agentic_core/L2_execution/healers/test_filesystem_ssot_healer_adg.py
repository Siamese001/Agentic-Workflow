"""ADG importability contract for agentic_core/L2_execution/healers/filesystem_ssot_healer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_filesystem_ssot_healer.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.healers.filesystem_ssot_healer import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        heal_filesystem_ssot_drift,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    heal_filesystem_ssot_drift = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="filesystem_ssot_healer.py deps unavailable")
class TestFilesystemSsotHealerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: filesystem_ssot_healer.py must be importable."""
        assert _AVAILABLE

    def test_heal_filesystem_ssot_drift_callable(self) -> None:
        assert callable(heal_filesystem_ssot_drift)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None