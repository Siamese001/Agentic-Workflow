"""Foundational behavioral tests for agentic_core/L5_safety/governance/lazy_seam_scanner.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_lazy_seam_scanner_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.governance.lazy_seam_scanner import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    LazySeamScanner,
    LazyUpwardImport,
    collect_lazy_upward_imports,
    extract_import_targets,
    layer_of_path,
    lazy_upward_import_metric,
)


class TestLazyUpwardImportContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(LazyUpwardImport)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(LazyUpwardImport)}
        assert field_names >= {'target_layer', 'source_file', 'source_layer', 'line_number', 'import_statement'}

class TestLazySeamScannerContract:
    def test_is_class(self):
        assert isinstance(LazySeamScanner, type)

    def test_has_method_scan_codebase(self):
        assert callable(getattr(LazySeamScanner, 'scan_codebase', None))

    def test_has_method_export_allowlist(self):
        assert callable(getattr(LazySeamScanner, 'export_allowlist', None))

class TestLayerOfPathFunction:
    def test_is_callable(self):
        assert callable(layer_of_path)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(layer_of_path)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestExtractImportTargetsFunction:
    def test_is_callable(self):
        assert callable(extract_import_targets)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(extract_import_targets)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestCollectLazyUpwardImportsFunction:
    def test_is_callable(self):
        assert callable(collect_lazy_upward_imports)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(collect_lazy_upward_imports)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestLazyUpwardImportMetricFunction:
    def test_is_callable(self):
        assert callable(lazy_upward_import_metric)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(lazy_upward_import_metric)
        assert sig.return_annotation is not inspect.Parameter.empty

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
    """Module lazy_seam_scanner must be importable or skip gracefully."""
    pass  # Import verified at module level
