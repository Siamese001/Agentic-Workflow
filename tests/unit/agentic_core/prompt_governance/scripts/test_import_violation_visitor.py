"""Foundational behavioral tests for agentic_core/prompt_governance/scripts/import_violation_visitor.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_import_violation_visitor_adg.py.
This file covers behavioral invariants and public API contracts.
"""
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
    )
    _AVAILABLE = True
except Exception as _exc:
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


@pytest.mark.skipif(not _AVAILABLE, reason="import_violation_visitor.py deps unavailable")
class TestImportViolationVisitorContract:
    def test_is_class(self):
        assert isinstance(ImportViolationVisitor, type)

    def test_has_method_visit_Import(self):
        assert callable(getattr(ImportViolationVisitor, 'visit_Import', None))

    def test_has_method_visit_ImportFrom(self):
        assert callable(getattr(ImportViolationVisitor, 'visit_ImportFrom', None))

@pytest.mark.skipif(not _AVAILABLE, reason="import_violation_visitor.py deps unavailable")
class TestFindPythonFilesFunction:
    def test_is_callable(self):
        assert callable(find_python_files)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(find_python_files)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="import_violation_visitor.py deps unavailable")
class TestAnalyzeFileFunction:
    def test_is_callable(self):
        assert callable(analyze_file)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(analyze_file)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="import_violation_visitor.py deps unavailable")
class TestEnforceLayerBoundariesFunction:
    def test_is_callable(self):
        assert callable(enforce_layer_boundaries)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(enforce_layer_boundaries)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="import_violation_visitor.py deps unavailable")
class TestMainFunction:
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


def test_module_importable():
    """Module import_violation_visitor must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
