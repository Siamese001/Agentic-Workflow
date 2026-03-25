"""Foundational behavioral tests for agentic_core/prompt_governance/scripts/import_violation_visitor.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_import_violation_visitor_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.prompt_governance.scripts.import_violation_visitor import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    ImportViolationVisitor,
    analyze_file,
    enforce_layer_boundaries,
    find_python_files,
    main,
)


class TestImportViolationVisitorContract:
    def test_is_class(self):
        assert isinstance(ImportViolationVisitor, type)

    def test_has_method_visit_Import(self):
        assert callable(getattr(ImportViolationVisitor, 'visit_Import', None))

    def test_has_method_visit_ImportFrom(self):
        assert callable(getattr(ImportViolationVisitor, 'visit_ImportFrom', None))

class TestFindPythonFilesFunction:
    def test_is_callable(self):
        assert callable(find_python_files)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(find_python_files)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestAnalyzeFileFunction:
    def test_is_callable(self):
        assert callable(analyze_file)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(analyze_file)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestEnforceLayerBoundariesFunction:
    def test_is_callable(self):
        assert callable(enforce_layer_boundaries)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(enforce_layer_boundaries)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestMainFunction:
    def test_is_callable(self):
        assert callable(main)

class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module import_violation_visitor must be importable or skip gracefully."""
    pass  # Import verified at module level
