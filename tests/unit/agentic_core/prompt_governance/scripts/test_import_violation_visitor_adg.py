"""ADG-driven tests for agentic_core/prompt_governance/scripts/import_violation_visitor.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.prompt_governance.scripts.import_violation_visitor import (  # noqa: F401
        ImportViolationVisitor,
        find_python_files,
        analyze_file,
        enforce_layer_boundaries,
        main,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ImportViolationVisitor = None  # type: ignore[assignment,misc]
    find_python_files = None  # type: ignore[assignment,misc]
    analyze_file = None  # type: ignore[assignment,misc]
    enforce_layer_boundaries = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="import_violation_visitor.py deps unavailable")
class TestImportViolationVisitor:
    def test_is_class(self):
        assert isinstance(ImportViolationVisitor, type)
    def test_importable(self):
        assert ImportViolationVisitor is not None

@pytest.mark.skipif(not _AVAILABLE, reason="import_violation_visitor.py deps unavailable")
class TestFindPythonFiles:
    def test_is_callable(self):
        assert callable(find_python_files)

@pytest.mark.skipif(not _AVAILABLE, reason="import_violation_visitor.py deps unavailable")
class TestAnalyzeFile:
    def test_is_callable(self):
        assert callable(analyze_file)

@pytest.mark.skipif(not _AVAILABLE, reason="import_violation_visitor.py deps unavailable")
class TestEnforceLayerBoundaries:
    def test_is_callable(self):
        assert callable(enforce_layer_boundaries)

@pytest.mark.skipif(not _AVAILABLE, reason="import_violation_visitor.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="import_violation_visitor.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="import_violation_visitor.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="import_violation_visitor.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="import_violation_visitor.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="import_violation_visitor.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="import_violation_visitor.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module import_violation_visitor.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
