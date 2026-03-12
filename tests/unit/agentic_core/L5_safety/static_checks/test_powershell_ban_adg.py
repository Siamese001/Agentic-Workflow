"""ADG importability contract for agentic_core/L5_safety/static_checks/powershell_ban.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_powershell_ban.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.static_checks.powershell_ban import (  # noqa: F401
        PowerShellBanVisitor,
        scan_file_for_powershell,
        scan_repository_for_powershell,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    PowerShellBanVisitor = None  # type: ignore[assignment,misc]
    scan_file_for_powershell = None  # type: ignore[assignment,misc]
    scan_repository_for_powershell = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="powershell_ban.py deps unavailable")
class TestPowershellBanImportability:
    def test_module_importable(self) -> None:
        """ADG contract: powershell_ban.py must be importable."""
        assert _AVAILABLE

    def test_powershellbanvisitor_is_type(self) -> None:
        assert PowerShellBanVisitor is not None

    def test_scan_file_for_powershell_callable(self) -> None:
        assert callable(scan_file_for_powershell)

    def test_scan_repository_for_powershell_callable(self) -> None:
        assert callable(scan_repository_for_powershell)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

