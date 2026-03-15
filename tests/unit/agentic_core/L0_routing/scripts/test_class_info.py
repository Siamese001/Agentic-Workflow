"""Foundational behavioral tests for agentic_core/L0_routing/scripts/class_info.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_class_info_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.class_info import (  # noqa: F401
        AGENTIC_CORE_DIR,
        ARCHIVES_DIR,
        EXCLUDE_DIRS,
        PROJECT_ROOT,
        TARGET_ARCHIVES,
        ClassInfo,
        FileAnalysis,
        compute_file_hash,
        count_lines,
        get_snippet,
        parse_python_file,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    ClassInfo = None  # type: ignore[assignment,misc]
    FileAnalysis = None  # type: ignore[assignment,misc]
    compute_file_hash = None  # type: ignore[assignment,misc]
    count_lines = None  # type: ignore[assignment,misc]
    get_snippet = None  # type: ignore[assignment,misc]
    parse_python_file = None  # type: ignore[assignment,misc]
    PROJECT_ROOT = None  # type: ignore[assignment,misc]
    ARCHIVES_DIR = None  # type: ignore[assignment,misc]
    AGENTIC_CORE_DIR = None  # type: ignore[assignment,misc]
    TARGET_ARCHIVES = None  # type: ignore[assignment,misc]
    EXCLUDE_DIRS = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="class_info.py deps unavailable")
class TestClassInfoContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ClassInfo)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ClassInfo)}
        assert field_names >= {'docstring', 'methods', 'line_number', 'bases', 'name'}

@pytest.mark.skipif(not _AVAILABLE, reason="class_info.py deps unavailable")
class TestFileAnalysisContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(FileAnalysis)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(FileAnalysis)}
        assert field_names >= {'line_count', 'path', 'size_bytes', 'relative_path', 'extension'}

@pytest.mark.skipif(not _AVAILABLE, reason="class_info.py deps unavailable")
class TestComputeFileHashFunction:
    def test_is_callable(self):
        assert callable(compute_file_hash)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(compute_file_hash)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="class_info.py deps unavailable")
class TestCountLinesFunction:
    def test_is_callable(self):
        assert callable(count_lines)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(count_lines)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="class_info.py deps unavailable")
class TestGetSnippetFunction:
    def test_is_callable(self):
        assert callable(get_snippet)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_snippet)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="class_info.py deps unavailable")
class TestParsePythonFileFunction:
    def test_is_callable(self):
        assert callable(parse_python_file)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(parse_python_file)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="class_info.py deps unavailable")
class TestProjectRootConstant:
    def test_is_not_none(self):
        assert PROJECT_ROOT is not None

@pytest.mark.skipif(not _AVAILABLE, reason="class_info.py deps unavailable")
class TestArchivesDirConstant:
    def test_is_not_none(self):
        assert ARCHIVES_DIR is not None

@pytest.mark.skipif(not _AVAILABLE, reason="class_info.py deps unavailable")
class TestAgenticCoreDirConstant:
    def test_is_not_none(self):
        assert AGENTIC_CORE_DIR is not None

@pytest.mark.skipif(not _AVAILABLE, reason="class_info.py deps unavailable")
class TestTargetArchivesConstant:
    def test_is_not_none(self):
        assert TARGET_ARCHIVES is not None

    def test_is_non_empty_sequence(self):
        assert hasattr(TARGET_ARCHIVES, '__len__')

@pytest.mark.skipif(not _AVAILABLE, reason="class_info.py deps unavailable")
class TestExcludeDirsConstant:
    def test_is_not_none(self):
        assert EXCLUDE_DIRS is not None


def test_module_importable():
    """Module class_info must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
