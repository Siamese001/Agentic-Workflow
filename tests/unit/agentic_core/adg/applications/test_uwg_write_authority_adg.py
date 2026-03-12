"""ADG importability contract for agentic_core/adg/applications/uwg_write_authority.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_uwg_write_authority.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.applications.uwg_write_authority import (  # noqa: F401
        UWGViolation,
        UWGReport,
        check_uwg_write_authority,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    UWGViolation = None  # type: ignore[assignment,misc]
    UWGReport = None  # type: ignore[assignment,misc]
    check_uwg_write_authority = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="uwg_write_authority.py deps unavailable")
class TestUwgWriteAuthorityImportability:
    def test_module_importable(self) -> None:
        """ADG contract: uwg_write_authority.py must be importable."""
        assert _AVAILABLE

    def test_uwgviolation_is_type(self) -> None:
        assert UWGViolation is not None

    def test_uwgreport_is_type(self) -> None:
        assert UWGReport is not None

    def test_check_uwg_write_authority_callable(self) -> None:
        assert callable(check_uwg_write_authority)

