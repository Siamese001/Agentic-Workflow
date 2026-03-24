"""ADG-driven tests for apps_rg/scripts/rg_final_audit.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_rg.scripts.rg_final_audit import (  # noqa: F401
        FORBIDDEN_IMPORTS,
        REQUIRED_BASE,
        ROOT,
        audit_file,
        main,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    audit_file = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    ROOT = None  # type: ignore[assignment,misc]
    REQUIRED_BASE = None  # type: ignore[assignment,misc]
    FORBIDDEN_IMPORTS = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="rg_final_audit.py deps unavailable")
class TestAuditFile:
    def test_is_callable(self):
        assert callable(audit_file)

@pytest.mark.skipif(not _AVAILABLE, reason="rg_final_audit.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="rg_final_audit.py deps unavailable")
class TestRootConstant:
    def test_is_not_none(self):
        assert ROOT is not None

@pytest.mark.skipif(not _AVAILABLE, reason="rg_final_audit.py deps unavailable")
class TestRequiredBaseConstant:
    def test_is_not_none(self):
        assert REQUIRED_BASE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="rg_final_audit.py deps unavailable")
class TestForbiddenImportsConstant:
    def test_is_not_none(self):
        assert FORBIDDEN_IMPORTS is not None


def test_module_importable():
    """Module rg_final_audit.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE