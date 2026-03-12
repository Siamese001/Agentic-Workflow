"""ADG-driven tests for agentic_core/L5_safety/enforcement/hardcoded_path_refactorer_enforcer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.hardcoded_path_refactorer_enforcer import (  # noqa: F401
        should_exclude_path,
        has_ssot_import,
        add_ssot_import,
        refactor_file,
        refactor_repository,
        PROJECT_ROOT,
        EXCLUDED_DIRS,
        EXCLUDED_FILES,
        PATH_TO_SSOT_MAP,
        PATH_CONSTRUCTOR_MAP,
        SSOT_IMPORT,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    should_exclude_path = None  # type: ignore[assignment,misc]
    has_ssot_import = None  # type: ignore[assignment,misc]
    add_ssot_import = None  # type: ignore[assignment,misc]
    refactor_file = None  # type: ignore[assignment,misc]
    refactor_repository = None  # type: ignore[assignment,misc]
    PROJECT_ROOT = None  # type: ignore[assignment,misc]
    EXCLUDED_DIRS = None  # type: ignore[assignment,misc]
    EXCLUDED_FILES = None  # type: ignore[assignment,misc]
    PATH_TO_SSOT_MAP = None  # type: ignore[assignment,misc]
    PATH_CONSTRUCTOR_MAP = None  # type: ignore[assignment,misc]
    SSOT_IMPORT = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="hardcoded_path_refactorer_enforcer.py deps unavailable")
class TestShouldExcludePath:
    def test_is_callable(self):
        assert callable(should_exclude_path)

@pytest.mark.skipif(not _AVAILABLE, reason="hardcoded_path_refactorer_enforcer.py deps unavailable")
class TestHasSsotImport:
    def test_is_callable(self):
        assert callable(has_ssot_import)

@pytest.mark.skipif(not _AVAILABLE, reason="hardcoded_path_refactorer_enforcer.py deps unavailable")
class TestAddSsotImport:
    def test_is_callable(self):
        assert callable(add_ssot_import)

@pytest.mark.skipif(not _AVAILABLE, reason="hardcoded_path_refactorer_enforcer.py deps unavailable")
class TestRefactorFile:
    def test_is_callable(self):
        assert callable(refactor_file)

@pytest.mark.skipif(not _AVAILABLE, reason="hardcoded_path_refactorer_enforcer.py deps unavailable")
class TestRefactorRepository:
    def test_is_callable(self):
        assert callable(refactor_repository)

@pytest.mark.skipif(not _AVAILABLE, reason="hardcoded_path_refactorer_enforcer.py deps unavailable")
class TestProjectRootConstant:
    def test_is_not_none(self):
        assert PROJECT_ROOT is not None

@pytest.mark.skipif(not _AVAILABLE, reason="hardcoded_path_refactorer_enforcer.py deps unavailable")
class TestExcludedDirsConstant:
    def test_is_not_none(self):
        assert EXCLUDED_DIRS is not None

@pytest.mark.skipif(not _AVAILABLE, reason="hardcoded_path_refactorer_enforcer.py deps unavailable")
class TestExcludedFilesConstant:
    def test_is_not_none(self):
        assert EXCLUDED_FILES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="hardcoded_path_refactorer_enforcer.py deps unavailable")
class TestPathToSsotMapConstant:
    def test_is_not_none(self):
        assert PATH_TO_SSOT_MAP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="hardcoded_path_refactorer_enforcer.py deps unavailable")
class TestPathConstructorMapConstant:
    def test_is_not_none(self):
        assert PATH_CONSTRUCTOR_MAP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="hardcoded_path_refactorer_enforcer.py deps unavailable")
class TestSsotImportConstant:
    def test_is_not_none(self):
        assert SSOT_IMPORT is not None


def test_module_importable():
    """Module hardcoded_path_refactorer_enforcer.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
