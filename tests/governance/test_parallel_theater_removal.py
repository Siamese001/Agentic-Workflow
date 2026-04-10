"""Tests verifying dead CPU-parallel theater code has been removed.

Validates:
1. generate_full_adg no longer imports CPU optimizer or parallel modules
2. Dead parallel modules (parallel_scanner, parallel_report_generator,
   batch_operations) are deleted from extraction/
3. Their _compat shims are also deleted
4. generate_full_adg function signature has no parallel/workers/cpu_affinity params
5. ADG generation still runs end-to-end without parallel infrastructure
"""

from __future__ import annotations

import ast
import importlib
import inspect
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


class TestParallelTheaterRemoval:
    """Verify fake parallel infrastructure is fully removed."""

    def test_dead_modules_deleted(self):
        """Deleted parallel modules must not exist on disk."""
        dead_modules = [
            "agentic_core/adg/extraction/parallel_scanner.py",
            "agentic_core/adg/extraction/parallel_report_generator.py",
            "agentic_core/adg/extraction/batch_operations.py",
            "agentic_core/adg/_compat/parallel_scanner.py",
            "agentic_core/adg/_compat/parallel_report_generator.py",
            "agentic_core/adg/_compat/batch_operations.py",
        ]
        for rel in dead_modules:
            path = ROOT / rel
            assert not path.exists(), f"Dead module still exists: {rel}"

    def test_generate_full_adg_no_parallel_imports(self):
        """generate_full_adg.py must not import CPU optimizer or parallel modules."""
        src_path = ROOT / "tools" / "generate" / "generate_full_adg.py"
        source = src_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(src_path))

        forbidden_modules = {
            "agentic_core.L2_execution.utils.cpu_optimizer",
            "agentic_core.L2_execution.utils.parallel_file_processor",
            "agentic_core.L2_execution.utils.batch_processor",
        }
        found = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module in forbidden_modules:
                names = [alias.name for alias in node.names]
                found.append(f"from {node.module} import {', '.join(names)}")

        assert not found, f"Forbidden parallel imports found: {found}"

    def test_generate_full_adg_signature_clean(self):
        """generate_full_adg() must not have parallel/workers/cpu_affinity/batch_size params."""
        src_path = ROOT / "tools" / "generate" / "generate_full_adg.py"
        source = src_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(src_path))

        forbidden_params = {"parallel", "workers", "cpu_affinity", "batch_size"}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "generate_full_adg":
                param_names = {arg.arg for arg in node.args.args}
                overlap = param_names & forbidden_params
                assert not overlap, f"generate_full_adg still has theater params: {overlap}"
                break
        else:
            pytest.fail("generate_full_adg function not found in AST")

    def test_main_cli_no_parallel_flags(self):
        """main() CLI must not have --no-parallel, --workers, --cpu-affinity, --batch-size."""
        src_path = ROOT / "tools" / "generate" / "generate_full_adg.py"
        source = src_path.read_text(encoding="utf-8")

        forbidden_flags = ["--no-parallel", "--workers", "--cpu-affinity", "--batch-size"]
        for flag in forbidden_flags:
            assert flag not in source, f"CLI still has theater flag: {flag}"

    def test_no_optimizer_banner_in_source(self):
        """The fake 'CPU Optimizer: N workers' banner must be gone."""
        src_path = ROOT / "tools" / "generate" / "generate_full_adg.py"
        source = src_path.read_text(encoding="utf-8")

        assert "CPU Optimizer:" not in source, "Fake CPU Optimizer banner still present"
        assert "CPU optimizer shutdown" not in source, "Optimizer shutdown message still present"
        assert "shutdown_cpu_optimizer" not in source, "shutdown_cpu_optimizer still referenced"
        assert "shutdown_file_processor" not in source, "shutdown_file_processor still referenced"

    def test_dead_modules_not_importable(self):
        """Deleted modules must raise ImportError when imported."""
        dead_imports = [
            "agentic_core.adg.extraction.parallel_scanner",
            "agentic_core.adg.extraction.parallel_report_generator",
            "agentic_core.adg.extraction.batch_operations",
        ]
        for mod_name in dead_imports:
            with pytest.raises(
                (ImportError, ModuleNotFoundError),
                match=r"No module named|cannot import name",
            ):
                importlib.import_module(mod_name)

    def test_static_scanner_still_importable(self):
        """The real scanner must still work after dead code removal."""
        mod = importlib.import_module("agentic_core.adg.extraction.static_scanner")
        assert hasattr(mod, "ADGStaticScanner"), "ADGStaticScanner missing from static_scanner"

    def test_vllm_batch_processor_archived(self):
        """VLLMBatchProcessor module must not exist in apps_shared/utils/."""
        path = ROOT / "apps_shared" / "utils" / "vllm_advanced_features.py"
        assert not path.exists(), "Dead VLLMBatchProcessor module still in apps_shared/utils/"
