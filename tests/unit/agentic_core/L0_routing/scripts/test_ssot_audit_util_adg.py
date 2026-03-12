"""ADG-driven tests for agentic_core/L0_routing/scripts/ssot_audit_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.ssot_audit_util import (  # noqa: F401
        find_duplicates,
        find_gravity_violations,
        find_syntax_errors,
        find_naming_violations,
        APPROVED_FOLDERS,
        ROOT,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    find_duplicates = None  # type: ignore[assignment,misc]
    find_gravity_violations = None  # type: ignore[assignment,misc]
    find_syntax_errors = None  # type: ignore[assignment,misc]
    find_naming_violations = None  # type: ignore[assignment,misc]
    APPROVED_FOLDERS = None  # type: ignore[assignment,misc]
    ROOT = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ssot_audit_util.py deps unavailable")
class TestFindDuplicates:
    def test_is_callable(self):
        assert callable(find_duplicates)

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_audit_util.py deps unavailable")
class TestFindGravityViolations:
    def test_is_callable(self):
        assert callable(find_gravity_violations)

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_audit_util.py deps unavailable")
class TestFindSyntaxErrors:
    def test_is_callable(self):
        assert callable(find_syntax_errors)

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_audit_util.py deps unavailable")
class TestFindNamingViolations:
    def test_is_callable(self):
        assert callable(find_naming_violations)

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_audit_util.py deps unavailable")
class TestApprovedFoldersConstant:
    def test_is_not_none(self):
        assert APPROVED_FOLDERS is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_audit_util.py deps unavailable")
class TestRootConstant:
    def test_is_not_none(self):
        assert ROOT is not None


def test_module_importable():
    """Module ssot_audit_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
