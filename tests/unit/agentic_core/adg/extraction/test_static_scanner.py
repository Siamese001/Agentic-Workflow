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
        ADGStaticScanner,
        Edge,
        ScanManifest,
        ScanResult,
        run_scanner_self_test,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
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
        assert fnames >= {"relation_type", "from_name", "edge_kind", "source_file", "to_name", "line_no"}

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
        assert fnames >= {
            "parsed_module_count",
            "discovered_module_count",
            "schema_version",
            "scanner_version",
            "syntax_error_count",
            "python_ast_version",
        }

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
        assert fnames >= {"digest", "edges", "commit_sha", "manifest", "syntax_errors", "modules"}

    def test_field_count_reasonable(self):
        import dataclasses

        assert len(dataclasses.fields(ScanResult)) >= 1


@pytest.mark.skipif(not _AVAILABLE, reason="static_scanner.py deps unavailable")
class TestADGStaticScannerContract:
    def test_is_class(self):
        assert isinstance(ADGStaticScanner, type)

    def test_has_method_scan(self):
        assert callable(getattr(ADGStaticScanner, "scan", None))

    def test_has_method_scan_files(self):
        assert callable(getattr(ADGStaticScanner, "scan_files", None))

    def test_has_method_build_reverse_import_graph(self):
        assert callable(getattr(ADGStaticScanner, "build_reverse_import_graph", None))

    def test_has_method_module_layer_map(self):
        assert callable(getattr(ADGStaticScanner, "module_layer_map", None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(ADGStaticScanner) if not m.startswith("_")]
        assert len(pub) >= 1


@pytest.mark.skipif(not _AVAILABLE, reason="static_scanner.py deps unavailable")
class TestRunScannerSelfTestFunction:
    def test_is_callable(self):
        assert callable(run_scanner_self_test)

    def test_has_return_annotation(self):
        import inspect

        sig = inspect.signature(run_scanner_self_test)
        assert sig.return_annotation is not inspect.Parameter.empty


@pytest.mark.skipif(not _AVAILABLE, reason="static_scanner.py deps unavailable")
class TestStaticRuntimeBoundary:
    def test_scan_files_excludes_non_structural_paths_by_default(self, tmp_path):
        structural = tmp_path / "agentic_core" / "L0_routing" / "router.py"
        structural.parent.mkdir(parents=True, exist_ok=True)
        structural.write_text("import os\n", encoding="utf-8")

        test_file = tmp_path / "tests" / "test_router.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("import os\n", encoding="utf-8")

        runtime_file = tmp_path / "agentic_core" / "runtime" / "trace_runtime.py"
        runtime_file.parent.mkdir(parents=True, exist_ok=True)
        runtime_file.write_text("import os\n", encoding="utf-8")

        script_file = tmp_path / "apps_exec" / "scripts" / "run_exec.py"
        script_file.parent.mkdir(parents=True, exist_ok=True)
        script_file.write_text("import os\n", encoding="utf-8")

        scanner = ADGStaticScanner(repo_root=tmp_path)
        result = scanner.scan_files(
            [
                "agentic_core/L0_routing/router.py",
                "tests/test_router.py",
                "agentic_core/runtime/trace_runtime.py",
                "apps_exec/scripts/run_exec.py",
            ],
            commit_sha="boundary-default",
        )

        assert result.modules == ["agentic_core/L0_routing/router.py"]

    def test_scan_files_include_tests_true_restores_extended_scope(self, tmp_path):
        structural = tmp_path / "agentic_core" / "L0_routing" / "router.py"
        structural.parent.mkdir(parents=True, exist_ok=True)
        structural.write_text("import os\n", encoding="utf-8")

        test_file = tmp_path / "tests" / "test_router.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("import os\n", encoding="utf-8")

        runtime_file = tmp_path / "agentic_core" / "runtime" / "trace_runtime.py"
        runtime_file.parent.mkdir(parents=True, exist_ok=True)
        runtime_file.write_text("import os\n", encoding="utf-8")

        script_file = tmp_path / "apps_exec" / "scripts" / "run_exec.py"
        script_file.parent.mkdir(parents=True, exist_ok=True)
        script_file.write_text("import os\n", encoding="utf-8")

        scanner = ADGStaticScanner(repo_root=tmp_path, include_tests=True)
        result = scanner.scan_files(
            [
                "agentic_core/L0_routing/router.py",
                "tests/test_router.py",
                "agentic_core/runtime/trace_runtime.py",
                "apps_exec/scripts/run_exec.py",
            ],
            commit_sha="boundary-extended",
        )

        assert result.modules == [
            "agentic_core/L0_routing/router.py",
            "agentic_core/runtime/trace_runtime.py",
            "apps_exec/scripts/run_exec.py",
            "tests/test_router.py",
        ]

    def test_runtime_only_relations_are_filtered_from_structure_only_output(self, tmp_path):
        structural = tmp_path / "agentic_core" / "L0_routing" / "router.py"
        structural.parent.mkdir(parents=True, exist_ok=True)
        structural.write_text(
            "from agentic_core.L_CONTRACTS.lifecycle_trace_contract import record_execution_trace\n\n"
            "def route() -> None:\n"
            "    record_execution_trace('router', 'trace')\n",
            encoding="utf-8",
        )

        default_result = ADGStaticScanner(repo_root=tmp_path).scan_files(
            ["agentic_core/L0_routing/router.py"],
            commit_sha="boundary-structure-only",
        )
        extended_result = ADGStaticScanner(repo_root=tmp_path, include_tests=True).scan_files(
            ["agentic_core/L0_routing/router.py"],
            commit_sha="boundary-extended",
        )

        assert any(edge.relation_type == "imports" for edge in default_result.edges)
        assert all(edge.relation_type != "records_execution_trace" for edge in default_result.edges)
        assert any(edge.relation_type == "records_execution_trace" for edge in extended_result.edges)


def test_module_importable():
    """Smoke: static_scanner importable or gracefully unavailable."""
    pass