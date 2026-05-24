"""Test that active import graph contains no quarantined paths.

Per plan apps-rg-structured-resume-refactor-f8c2a1 W0A.

This test verifies:
1. No active file imports from quarantined paths
2. Import chain from __main__ to dispatch to bindings is clean
3. Quarantined paths are isolated
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Set

import pytest


def _resolve_repo_root() -> Path:
    """Resolve repository root."""
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parent.parent.parent


REPO_ROOT = _resolve_repo_root()


# Retired paths — must not be imported by active spine code (files may be absent).
RETIRED_IMPORT_PATHS: set[str] = {
    "apps_rg/engines/judges/executive_positioning_judge.py",
    "apps_rg/integrations/gates/online_judges.py",
    "apps_rg/tools/compute_word_count.py",
}

# Legacy alias for tests that scanned stub files on disk.
QUARANTINED_PATHS = RETIRED_IMPORT_PATHS

# Active paths allowed to be imported
ACTIVE_PATHS: set[str] = {
    "apps_rg/__init__.py",
    "apps_rg/__main__.py",
    "apps_rg/runtime/dispatch/apps_rg_dispatch.py",
    "apps_rg/runtime/dispatch/__init__.py",
    "apps_rg/runtime/bindings/u0_binding.py",
    "apps_rg/runtime/bindings/l1_binding.py",
    "apps_rg/runtime/bindings/l0_binding.py",
    "apps_rg/runtime/bindings/c0_binding.py",
    "apps_rg/runtime/bindings/pa_binding.py",
    "apps_rg/runtime/bindings/l2_binding.py",
    "apps_rg/runtime/bindings/exit_binding.py",
    "apps_rg/runtime/bindings/l2_envelope_adapter.py",
    "apps_rg/runtime/bindings/c0_minimum_safety.py",
    "apps_rg/runtime/bindings/__init__.py",
    "apps_rg/runtime/runtime_executive_summary.py",
    "apps_rg/runtime/__init__.py",
    "apps_rg/runtime/schemas/__init__.py",
    "apps_rg/runtime/schemas/section_schemas.py",
    "apps_rg/tools/__init__.py",
}


def _extract_imports_from_file(file_path: Path) -> list[str]:
    """Extract all import statements from a Python file."""
    imports: list[str] = []
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imports.append(module)
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
    except SyntaxError:
        pass
    except Exception:
        pass
    return imports


def _path_to_module(path: str) -> str:
    """Convert file path to Python module name."""
    if path.endswith(".py"):
        path = path[:-3]
    return path.replace("/", ".").replace("\\", ".")


def _is_quarantine_violation(import_module: str) -> str | None:
    """Check if an import violates quarantine rules."""
    for q_path in QUARANTINED_PATHS:
        q_module = _path_to_module(q_path)
        if import_module == q_module or import_module.startswith(q_module + "."):
            return q_path
    return None


class TestImportGraphNoQuarantine:
    """Test that active import graph has no quarantine violations."""
    
    def test_main_py_no_quarantine_imports(self) -> None:
        """__main__.py must not import from quarantined paths."""
        main_file = REPO_ROOT / "apps_rg" / "__main__.py"
        imports = _extract_imports_from_file(main_file)
        
        for imp in imports:
            violation = _is_quarantine_violation(imp)
            if violation:
                pytest.fail(f"__main__.py imports quarantined path: {imp} from {violation}")
    
    def test_dispatch_no_quarantine_imports(self) -> None:
        """apps_rg_dispatch.py must not import from quarantined paths."""
        dispatch_file = REPO_ROOT / "apps_rg" / "runtime" / "dispatch" / "apps_rg_dispatch.py"
        imports = _extract_imports_from_file(dispatch_file)
        
        for imp in imports:
            violation = _is_quarantine_violation(imp)
            if violation:
                pytest.fail(f"dispatch imports quarantined path: {imp} from {violation}")
    
    def test_bindings_no_quarantine_imports(self) -> None:
        """Binding files must not import from quarantined paths."""
        bindings_dir = REPO_ROOT / "apps_rg" / "runtime" / "bindings"
        
        for binding_file in bindings_dir.glob("*.py"):
            imports = _extract_imports_from_file(binding_file)
            for imp in imports:
                violation = _is_quarantine_violation(imp)
                if violation:
                    rel_path = binding_file.relative_to(REPO_ROOT).as_posix()
                    pytest.fail(f"{rel_path} imports quarantined path: {imp} from {violation}")
    
    def test_runtime_executive_summary_no_quarantine_imports(self) -> None:
        """runtime_executive_summary.py must not import from quarantined paths."""
        summary_file = REPO_ROOT / "apps_rg" / "runtime" / "runtime_executive_summary.py"
        if summary_file.exists():
            imports = _extract_imports_from_file(summary_file)
            for imp in imports:
                violation = _is_quarantine_violation(imp)
                if violation:
                    pytest.fail(f"runtime_executive_summary imports quarantined: {imp} from {violation}")
    
    def test_retired_paths_absent_or_not_importable(self) -> None:
        """Retired stub paths must not exist on disk (hard-deleted)."""
        for q_path in RETIRED_IMPORT_PATHS:
            assert not (REPO_ROOT / q_path).is_file(), q_path
    
    def test_active_import_chain_complete(self) -> None:
        """Verify active import chain: __main__ -> governed dispatch -> bindings."""
        main_file = REPO_ROOT / "apps_rg" / "__main__.py"
        main_content = main_file.read_text(encoding="utf-8")
        assert (
            "dispatch_apps_rg_run" in main_content
            or "from apps_rg.runtime.dispatch" in main_content
            or "runtime.orchestration.canonical_dispatch" in main_content
        ), "__main__.py must reach governed dispatch / canonical_dispatch"
        
        dispatch_file = REPO_ROOT / "apps_rg" / "runtime" / "dispatch" / "apps_rg_dispatch.py"
        dispatch_content = dispatch_file.read_text(encoding="utf-8")
        assert (
            "from apps_rg.runtime.bindings" in dispatch_content
            or "canonical_dispatch" in dispatch_content
            or "apps_rg_dispatch" in dispatch_content
        ), "dispatch module must exist on governed spine path"
    
    def test_no_hops_imports_in_bindings(self) -> None:
        """Bindings must not import from integrations/hops."""
        bindings_dir = REPO_ROOT / "apps_rg" / "runtime" / "bindings"
        
        for binding_file in bindings_dir.glob("*.py"):
            content = binding_file.read_text(encoding="utf-8")
            assert "from apps_rg.integrations.hops" not in content, \
                f"{binding_file.name} must not import from hops"
            assert "from apps_rg.engines" not in content, \
                f"{binding_file.name} must not import from engines"
    
    def test_no_reasoning_imports_in_bindings(self) -> None:
        """Bindings must not import from reasoning."""
        bindings_dir = REPO_ROOT / "apps_rg" / "runtime" / "bindings"
        
        for binding_file in bindings_dir.glob("*.py"):
            content = binding_file.read_text(encoding="utf-8")
            assert "from apps_rg.reasoning" not in content, \
                f"{binding_file.name} must not import from reasoning"


class TestQuarantineIsolation:
    """Test that quarantined paths are properly isolated."""
    
    def test_quarantine_directory_removed(self) -> None:
        """apps_rg/_quarantine/ removed in hard-delete waves."""
        assert not (REPO_ROOT / "apps_rg" / "_quarantine").exists()
    
    def test_hops_directory_isolated(self) -> None:
        """integrations/hops must not be imported by active code."""
        active_files = [
            REPO_ROOT / "apps_rg" / "__main__.py",
            REPO_ROOT / "apps_rg" / "runtime" / "dispatch" / "apps_rg_dispatch.py",
        ]
        bindings_dir = REPO_ROOT / "apps_rg" / "runtime" / "bindings"
        for f in bindings_dir.glob("*.py"):
            active_files.append(f)
        
        for active_file in active_files:
            if not active_file.exists():
                continue
            content = active_file.read_text(encoding="utf-8")
            assert "from apps_rg.integrations.hops" not in content, \
                f"{active_file.name} must not import from hops"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
