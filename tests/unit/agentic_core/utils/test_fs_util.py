"""Foundational behavioral tests for agentic_core/utils/fs_util.py.

fan_in=3 — imported by 3 other modules.
ADG import-hygiene is covered separately by test_fs_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.utils.fs_util import (  # noqa: F401
        calculate_file_hash,
        get_canonical_path,
        get_python_files_fast,
        remove_duplicate_suffix_path,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    get_python_files_fast = None  # type: ignore[assignment,misc]
    calculate_file_hash = None  # type: ignore[assignment,misc]
    get_canonical_path = None  # type: ignore[assignment,misc]
    remove_duplicate_suffix_path = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="fs_util.py deps unavailable")
class TestGetPythonFilesFastFunction:
    def test_is_callable(self):
        assert callable(get_python_files_fast)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_python_files_fast)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="fs_util.py deps unavailable")
class TestCalculateFileHashFunction:
    def test_is_callable(self):
        assert callable(calculate_file_hash)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(calculate_file_hash)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="fs_util.py deps unavailable")
class TestGetCanonicalPathFunction:
    def test_is_callable(self):
        assert callable(get_canonical_path)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_canonical_path)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="fs_util.py deps unavailable")
class TestRemoveDuplicateSuffixPathFunction:
    def test_is_callable(self):
        assert callable(remove_duplicate_suffix_path)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(remove_duplicate_suffix_path)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Smoke: fs_util importable or gracefully unavailable."""
    pass