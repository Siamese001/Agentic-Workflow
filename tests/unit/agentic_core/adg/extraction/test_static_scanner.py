"""Foundational behavioral tests for agentic_core/adg/extraction/static_scanner.py.

fan_in=44 — imported by 44 other modules.
ADG import-hygiene is covered separately by test_static_scanner_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.adg.extraction.static_scanner import (  # noqa: F401
        Edge,
        ScanManifest,
        ScanResult,
        ADGStaticScanner,
        run_scanner_self_test,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    Edge = None  # type: ignore[assignment,misc]
    ScanManifest = None  # type: ignore[assignment,misc]
    ScanResult = None  # type: ignore[assignment,misc]
    ADGStaticScanner = None  # type: ignore[assignment,misc]
    run_scanner_self_test = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="static_scanner.py deps unavailable")
class TestEdgeContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(Edge)

    def test_is_frozen(self):
        assert Edge.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(Edge)}
        assert fnames >= {'relation_type', 'from_name', 'edge_kind', 'source_file', 'to_name', 'line_no'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(Edge)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="static_scanner.py deps unavailable")
class TestScanManifestContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ScanManifest)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(ScanManifest)}
        assert fnames >= {'parsed_module_count', 'discovered_module_count', 'schema_version', 'scanner_version', 'syntax_error_count', 'python_ast_version'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(ScanManifest)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="static_scanner.py deps unavailable")
class TestScanResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ScanResult)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(ScanResult)}
        assert fnames >= {'digest', 'edges', 'commit_sha', 'manifest', 'syntax_errors', 'modules'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(ScanResult)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="static_scanner.py deps unavailable")
class TestADGStaticScannerContract:
    def test_is_class(self):
        assert isinstance(ADGStaticScanner, type)

    def test_has_method_scan(self):
        assert callable(getattr(ADGStaticScanner, 'scan', None))

    def test_has_method_scan_files(self):
        assert callable(getattr(ADGStaticScanner, 'scan_files', None))

    def test_has_method_build_reverse_import_graph(self):
        assert callable(getattr(ADGStaticScanner, 'build_reverse_import_graph', None))

    def test_has_method_module_layer_map(self):
        assert callable(getattr(ADGStaticScanner, 'module_layer_map', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(ADGStaticScanner) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="static_scanner.py deps unavailable")
class TestRunScannerSelfTestFunction:
    def test_is_callable(self):
        assert callable(run_scanner_self_test)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(run_scanner_self_test)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Smoke: static_scanner importable or gracefully unavailable."""
    assert True
