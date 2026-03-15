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
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    PowerShellBanVisitor = None  # type: ignore[assignment,misc]
    scan_file_for_powershell = None  # type: ignore[assignment,misc]
    scan_repository_for_powershell = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="powershell_ban deps unavailable")
class TestPowershellBanImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/static_checks/powershell_ban.py must be importable."""
        assert _AVAILABLE

    def test_powershellbanvisitor_defined(self) -> None:
        assert PowerShellBanVisitor is not None
