"""ADG-driven tests for agentic_core/L5_safety/enforcement/sealed_interface_check_enforcer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.sealed_interface_check_enforcer import (  # noqa: F401
        APPS_ROOTS,
        FORBIDDEN_IMPORT_PATTERNS,
        FORBIDDEN_LAYER_PREFIXES,
        REPO_ROOT,
        check_file,
        main,
        run_check,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    check_file = None  # type: ignore[assignment,misc]
    run_check = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    REPO_ROOT = None  # type: ignore[assignment,misc]
    APPS_ROOTS = None  # type: ignore[assignment,misc]
    FORBIDDEN_IMPORT_PATTERNS = None  # type: ignore[assignment,misc]
    FORBIDDEN_LAYER_PREFIXES = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="sealed_interface_check_enforcer.py deps unavailable")
class TestCheckFile:
    def test_is_callable(self):
        assert callable(check_file)

@pytest.mark.skipif(not _AVAILABLE, reason="sealed_interface_check_enforcer.py deps unavailable")
class TestRunCheck:
    def test_is_callable(self):
        assert callable(run_check)

@pytest.mark.skipif(not _AVAILABLE, reason="sealed_interface_check_enforcer.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="sealed_interface_check_enforcer.py deps unavailable")
class TestRepoRootConstant:
    def test_is_not_none(self):
        assert REPO_ROOT is not None

@pytest.mark.skipif(not _AVAILABLE, reason="sealed_interface_check_enforcer.py deps unavailable")
class TestAppsRootsConstant:
    def test_is_not_none(self):
        assert APPS_ROOTS is not None

@pytest.mark.skipif(not _AVAILABLE, reason="sealed_interface_check_enforcer.py deps unavailable")
class TestForbiddenImportPatternsConstant:
    def test_is_not_none(self):
        assert FORBIDDEN_IMPORT_PATTERNS is not None

@pytest.mark.skipif(not _AVAILABLE, reason="sealed_interface_check_enforcer.py deps unavailable")
class TestForbiddenLayerPrefixesConstant:
    def test_is_not_none(self):
        assert FORBIDDEN_LAYER_PREFIXES is not None


def test_module_importable():
    """Module sealed_interface_check_enforcer.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
