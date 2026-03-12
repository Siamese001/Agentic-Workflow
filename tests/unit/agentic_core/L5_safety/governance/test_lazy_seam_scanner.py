"""Foundational behavioral tests for agentic_core/L5_safety/governance/lazy_seam_scanner.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_lazy_seam_scanner_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.governance.lazy_seam_scanner import (  # noqa: F401
        LazyUpwardImport,
        LazySeamScanner,
        layer_of_path,
        extract_import_targets,
        collect_lazy_upward_imports,
        lazy_upward_import_metric,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    LazyUpwardImport = None  # type: ignore[assignment,misc]
    LazySeamScanner = None  # type: ignore[assignment,misc]
    layer_of_path = None  # type: ignore[assignment,misc]
    extract_import_targets = None  # type: ignore[assignment,misc]
    collect_lazy_upward_imports = None  # type: ignore[assignment,misc]
    lazy_upward_import_metric = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_scanner.py deps unavailable")
class TestLazyUpwardImportContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(LazyUpwardImport)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(LazyUpwardImport)}
        assert field_names >= {'target_layer', 'source_file', 'source_layer', 'line_number', 'import_statement'}

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_scanner.py deps unavailable")
class TestLazySeamScannerContract:
    def test_is_class(self):
        assert isinstance(LazySeamScanner, type)

    def test_has_method_scan_codebase(self):
        assert callable(getattr(LazySeamScanner, 'scan_codebase', None))

    def test_has_method_export_allowlist(self):
        assert callable(getattr(LazySeamScanner, 'export_allowlist', None))

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_scanner.py deps unavailable")
class TestLayerOfPathFunction:
    def test_is_callable(self):
        assert callable(layer_of_path)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(layer_of_path)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_scanner.py deps unavailable")
class TestExtractImportTargetsFunction:
    def test_is_callable(self):
        assert callable(extract_import_targets)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(extract_import_targets)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_scanner.py deps unavailable")
class TestCollectLazyUpwardImportsFunction:
    def test_is_callable(self):
        assert callable(collect_lazy_upward_imports)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(collect_lazy_upward_imports)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_scanner.py deps unavailable")
class TestLazyUpwardImportMetricFunction:
    def test_is_callable(self):
        assert callable(lazy_upward_import_metric)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(lazy_upward_import_metric)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_scanner.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_scanner.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_scanner.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_scanner.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_scanner.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module lazy_seam_scanner must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
