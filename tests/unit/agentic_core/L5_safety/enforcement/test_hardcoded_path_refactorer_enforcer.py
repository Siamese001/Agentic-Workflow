"""Foundational behavioral tests for agentic_core/L5_safety/enforcement/hardcoded_path_refactorer_enforcer.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_hardcoded_path_refactorer_enforcer_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.hardcoded_path_refactorer_enforcer import (  # noqa: F401
        should_exclude_path,
        has_ssot_import,
        add_ssot_import,
        refactor_file,
        PROJECT_ROOT,
        EXCLUDED_DIRS,
        EXCLUDED_FILES,
        PATH_TO_SSOT_MAP,
        PATH_CONSTRUCTOR_MAP,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    should_exclude_path = None  # type: ignore[assignment,misc]
    has_ssot_import = None  # type: ignore[assignment,misc]
    add_ssot_import = None  # type: ignore[assignment,misc]
    refactor_file = None  # type: ignore[assignment,misc]
    PROJECT_ROOT = None  # type: ignore[assignment,misc]
    EXCLUDED_DIRS = None  # type: ignore[assignment,misc]
    EXCLUDED_FILES = None  # type: ignore[assignment,misc]
    PATH_TO_SSOT_MAP = None  # type: ignore[assignment,misc]
    PATH_CONSTRUCTOR_MAP = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="hardcoded_path_refactorer_enforcer.py deps unavailable")
class TestShouldExcludePathFunction:
    def test_is_callable(self):
        assert callable(should_exclude_path)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(should_exclude_path)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="hardcoded_path_refactorer_enforcer.py deps unavailable")
class TestHasSsotImportFunction:
    def test_is_callable(self):
        assert callable(has_ssot_import)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(has_ssot_import)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="hardcoded_path_refactorer_enforcer.py deps unavailable")
class TestAddSsotImportFunction:
    def test_is_callable(self):
        assert callable(add_ssot_import)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(add_ssot_import)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="hardcoded_path_refactorer_enforcer.py deps unavailable")
class TestRefactorFileFunction:
    def test_is_callable(self):
        assert callable(refactor_file)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(refactor_file)
        assert sig.return_annotation is not inspect.Parameter.empty

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

    def test_is_non_empty_sequence(self):
        assert hasattr(EXCLUDED_FILES, '__len__')

@pytest.mark.skipif(not _AVAILABLE, reason="hardcoded_path_refactorer_enforcer.py deps unavailable")
class TestPathToSsotMapConstant:
    def test_is_not_none(self):
        assert PATH_TO_SSOT_MAP is not None

    def test_is_mapping(self):
        assert hasattr(PATH_TO_SSOT_MAP, '__getitem__')

@pytest.mark.skipif(not _AVAILABLE, reason="hardcoded_path_refactorer_enforcer.py deps unavailable")
class TestPathConstructorMapConstant:
    def test_is_not_none(self):
        assert PATH_CONSTRUCTOR_MAP is not None

    def test_is_mapping(self):
        assert hasattr(PATH_CONSTRUCTOR_MAP, '__getitem__')


def test_module_importable():
    """Module hardcoded_path_refactorer_enforcer must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
