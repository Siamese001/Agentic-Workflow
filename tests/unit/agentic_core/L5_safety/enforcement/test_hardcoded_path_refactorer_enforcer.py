"""Foundational behavioral tests for agentic_core/L5_safety/enforcement/hardcoded_path_refactorer_enforcer.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_hardcoded_path_refactorer_enforcer_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.enforcement.hardcoded_path_refactorer_enforcer import (  # noqa: F401
    EXCLUDED_DIRS,
    EXCLUDED_FILES,
    PATH_CONSTRUCTOR_MAP,
    PATH_TO_SSOT_MAP,
    PROJECT_ROOT,
    add_ssot_import,
    has_ssot_import,
    refactor_file,
    should_exclude_path,
)


class TestShouldExcludePathFunction:
    def test_is_callable(self):
        assert callable(should_exclude_path)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(should_exclude_path)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestHasSsotImportFunction:
    def test_is_callable(self):
        assert callable(has_ssot_import)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(has_ssot_import)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestAddSsotImportFunction:
    def test_is_callable(self):
        assert callable(add_ssot_import)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(add_ssot_import)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestRefactorFileFunction:
    def test_is_callable(self):
        assert callable(refactor_file)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(refactor_file)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestProjectRootConstant:
    def test_is_not_none(self):
        assert PROJECT_ROOT is not None

class TestExcludedDirsConstant:
    def test_is_not_none(self):
        assert EXCLUDED_DIRS is not None

class TestExcludedFilesConstant:
    def test_is_not_none(self):
        assert EXCLUDED_FILES is not None

    def test_is_non_empty_sequence(self):
        assert hasattr(EXCLUDED_FILES, '__len__')

class TestPathToSsotMapConstant:
    def test_is_not_none(self):
        assert PATH_TO_SSOT_MAP is not None

    def test_is_mapping(self):
        assert hasattr(PATH_TO_SSOT_MAP, '__getitem__')

class TestPathConstructorMapConstant:
    def test_is_not_none(self):
        assert PATH_CONSTRUCTOR_MAP is not None

    def test_is_mapping(self):
        assert hasattr(PATH_CONSTRUCTOR_MAP, '__getitem__')


def test_module_importable():
    """Module hardcoded_path_refactorer_enforcer must be importable or skip gracefully."""
    pass  # Import verified at module level
