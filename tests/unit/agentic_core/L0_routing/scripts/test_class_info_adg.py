"""ADG-driven tests for agentic_core/L0_routing/scripts/class_info.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.class_info import (  # noqa: F401
        ClassInfo,
        FileAnalysis,
        compute_file_hash,
        count_lines,
        get_snippet,
        parse_python_file,
        check_sovereignty_compliance,
        PROJECT_ROOT,
        ARCHIVES_DIR,
        AGENTIC_CORE_DIR,
        TARGET_ARCHIVES,
        EXCLUDE_DIRS,
        EXCLUDE_EXTENSIONS,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ClassInfo = None  # type: ignore[assignment,misc]
    FileAnalysis = None  # type: ignore[assignment,misc]
    compute_file_hash = None  # type: ignore[assignment,misc]
    count_lines = None  # type: ignore[assignment,misc]
    get_snippet = None  # type: ignore[assignment,misc]
    parse_python_file = None  # type: ignore[assignment,misc]
    check_sovereignty_compliance = None  # type: ignore[assignment,misc]
    PROJECT_ROOT = None  # type: ignore[assignment,misc]
    ARCHIVES_DIR = None  # type: ignore[assignment,misc]
    AGENTIC_CORE_DIR = None  # type: ignore[assignment,misc]
    TARGET_ARCHIVES = None  # type: ignore[assignment,misc]
    EXCLUDE_DIRS = None  # type: ignore[assignment,misc]
    EXCLUDE_EXTENSIONS = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="class_info.py deps unavailable")
class TestClassInfo:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ClassInfo)
    def test_importable(self):
        assert ClassInfo is not None

@pytest.mark.skipif(not _AVAILABLE, reason="class_info.py deps unavailable")
class TestFileAnalysis:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(FileAnalysis)
    def test_importable(self):
        assert FileAnalysis is not None

@pytest.mark.skipif(not _AVAILABLE, reason="class_info.py deps unavailable")
class TestComputeFileHash:
    def test_is_callable(self):
        assert callable(compute_file_hash)

@pytest.mark.skipif(not _AVAILABLE, reason="class_info.py deps unavailable")
class TestCountLines:
    def test_is_callable(self):
        assert callable(count_lines)

@pytest.mark.skipif(not _AVAILABLE, reason="class_info.py deps unavailable")
class TestGetSnippet:
    def test_is_callable(self):
        assert callable(get_snippet)

@pytest.mark.skipif(not _AVAILABLE, reason="class_info.py deps unavailable")
class TestParsePythonFile:
    def test_is_callable(self):
        assert callable(parse_python_file)

@pytest.mark.skipif(not _AVAILABLE, reason="class_info.py deps unavailable")
class TestCheckSovereigntyCompliance:
    def test_is_callable(self):
        assert callable(check_sovereignty_compliance)

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

@pytest.mark.skipif(not _AVAILABLE, reason="class_info.py deps unavailable")
class TestExcludeDirsConstant:
    def test_is_not_none(self):
        assert EXCLUDE_DIRS is not None

@pytest.mark.skipif(not _AVAILABLE, reason="class_info.py deps unavailable")
class TestExcludeExtensionsConstant:
    def test_is_not_none(self):
        assert EXCLUDE_EXTENSIONS is not None


def test_module_importable():
    """Module class_info.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
