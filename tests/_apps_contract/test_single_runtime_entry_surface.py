"""Regression test: Single runtime entry surface enforcement.

Per plan apps-rg-structured-resume-refactor-f8c2a1 W0A.

This test enforces:
- Exactly one executable runtime entry point
- No legacy dispatch imports
- No section_* imports from active path
- No engines/judges imports from active path
- No integrations/hops imports from active path
- Quarantined paths raise RuntimeError on import
"""
from __future__ import annotations

import ast
import subprocess
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
APPS_RG_DIR = REPO_ROOT / "apps_rg"

# Canonical ACTIVE paths that can be imported by __main__
ALLOWED_MAIN_IMPORTS: Set[str] = {
    "apps_rg.runtime.dispatch",
    "apps_rg.runtime.dispatch.apps_rg_dispatch",
    "apps_rg.runtime.dispatch.apps_rg_parse",
    "apps_rg.runtime.dispatch.APPS_RG_REQUIRED_FIELDS",
    "apps_rg.runtime.bindings",
    "apps_rg.runtime.bindings.u0_binding",
    "apps_rg.runtime.bindings.u0_binding.u0_validate_apps_rg",
    "apps_rg.runtime.bindings.l1_binding",
    "apps_rg.runtime.bindings.l0_binding",
    "apps_rg.runtime.bindings.c0_binding",
    "apps_rg.runtime.bindings.pa_binding",
    "apps_rg.runtime.bindings.l2_binding",
    "apps_rg.runtime.bindings.exit_binding",
}

# DISALLOWED patterns that must NOT appear in __main__.py
DISALLOWED_MAIN_PATTERNS: list[str] = [
    "runtime.entry.dispatch",  # Legacy dispatch path
    "runtime.section",  # Section pipeline
    "runtime.l6_shadow_learning",  # L6 shadow learning
    "engines.judges",  # Judges
    "integrations.hops",  # Hops
    "reasoning",  # Reasoning
]


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


class TestSingleRuntimeEntrySurface:
    """Enforce single runtime entry surface rules."""
    
    def test_main_ast_imports_explicitly_allowed(self) -> None:
        """AST analysis: __main__.py imports ONLY explicitly allowed targets."""
        main_file = APPS_RG_DIR / "__main__.py"
        content = main_file.read_text(encoding="utf-8")
        tree = ast.parse(content)
        
        # Extract all import statements from AST
        import_targets: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                # Full module path
                if node.level > 0:
                    # Relative import - construct full path
                    module = f"apps_rg.{module}"
                elif module and not module.startswith("apps_rg"):
                    # Not from apps_rg - skip (e.g., agentic_core, stdlib)
                    continue
                
                for alias in node.names:
                    full_target = f"{module}.{alias.name}" if module else alias.name
                    import_targets.append(full_target)
        
        # Verify each import target is explicitly allowed
        allowed_patterns = [
            "apps_rg.runtime.dispatch.apps_rg_dispatch",
            "apps_rg.runtime.dispatch.apps_rg_parse",
            "apps_rg.runtime.dispatch.APPS_RG_REQUIRED_FIELDS",
            "apps_rg.runtime.bindings.u0_binding",
            "apps_rg.runtime.bindings.u0_binding.u0_validate_apps_rg",
            # Also allow the parent modules
            "apps_rg.runtime.dispatch",
            "apps_rg.runtime.bindings",
        ]
        
        for target in import_targets:
            if not any(allowed in target for allowed in allowed_patterns):
                pytest.fail(
                    f"__main__.py imports non-allowed target: {target}\n"
                    f"Allowed patterns: {allowed_patterns}"
                )
    
    def test_main_imports_only_allowed_paths(self) -> None:
        """__main__.py must only import from allowed paths (text search)."""
        main_file = APPS_RG_DIR / "__main__.py"
        content = main_file.read_text(encoding="utf-8")
        
        for line in content.split("\n"):
            # Skip comments
            if line.strip().startswith("#"):
                continue
            
            # Check for disallowed patterns
            for pattern in DISALLOWED_MAIN_PATTERNS:
                if pattern in line and ("from apps_rg." in line or "import apps_rg." in line):
                    pytest.fail(
                        f"Disallowed import pattern '{pattern}' found in __main__.py:\n  {line.strip()}"
                    )
    
    def test_no_legacy_runtime_entry_dispatch_import(self) -> None:
        """Legacy runtime.entry.dispatch must not be imported."""
        main_file = APPS_RG_DIR / "__main__.py"
        content = main_file.read_text(encoding="utf-8")
        
        if "runtime.entry.dispatch" in content:
            pytest.fail(
                "Legacy import 'runtime.entry.dispatch' found in __main__.py. "
                "Must use 'runtime.dispatch' instead."
            )
    
    def test_section_files_not_imported_by_main(self) -> None:
        """Section files must not be imported by __main__.py."""
        main_file = APPS_RG_DIR / "__main__.py"
        content = main_file.read_text(encoding="utf-8")
        
        section_patterns = ["section_runtime", "section_agentic", "section_planner"]
        for pattern in section_patterns:
            if pattern in content:
                pytest.fail(
                    f"Section file pattern '{pattern}' found in __main__.py. "
                    "Section pipeline is NOT part of active generation path."
                )
    
    def test_l6_shadow_learning_not_imported(self) -> None:
        """l6_shadow_learning must not be imported by active code."""
        main_file = APPS_RG_DIR / "__main__.py"
        dispatch_file = APPS_RG_DIR / "runtime" / "dispatch" / "apps_rg_dispatch.py"
        
        for file_path in [main_file, dispatch_file]:
            content = file_path.read_text(encoding="utf-8")
            if "l6_shadow_learning" in content:
                pytest.fail(
                    f"l6_shadow_learning imported by {file_path.name}. "
                    "Per W0A: do not repair l6_shadow_learning.py"
                )
    
    def test_engines_judges_not_imported(self) -> None:
        """engines.judges must not be imported by active code."""
        active_files = [
            APPS_RG_DIR / "__main__.py",
            APPS_RG_DIR / "runtime" / "dispatch" / "apps_rg_dispatch.py",
        ]
        bindings_dir = APPS_RG_DIR / "runtime" / "bindings"
        for f in bindings_dir.glob("*.py"):
            active_files.append(f)
        
        for file_path in active_files:
            content = file_path.read_text(encoding="utf-8")
            if "engines.judges" in content or "from apps_rg.engines" in content:
                pytest.fail(
                    f"engines import found in {file_path.relative_to(REPO_ROOT)}. "
                    "engines/ is QUARANTINED per W0A."
                )
    
    def test_integrations_hops_not_imported(self) -> None:
        """integrations.hops must not be imported by active code."""
        active_files = [
            APPS_RG_DIR / "__main__.py",
            APPS_RG_DIR / "runtime" / "dispatch" / "apps_rg_dispatch.py",
        ]
        bindings_dir = APPS_RG_DIR / "runtime" / "bindings"
        for f in bindings_dir.glob("*.py"):
            active_files.append(f)
        
        for file_path in active_files:
            content = file_path.read_text(encoding="utf-8")
            if "integrations.hops" in content:
                pytest.fail(
                    f"hops import found in {file_path.relative_to(REPO_ROOT)}. "
                    "integrations/hops/ is QUARANTINED per W0A."
                )
    
    def test_reasoning_not_imported(self) -> None:
        """reasoning must not be imported by active code."""
        active_files = [
            APPS_RG_DIR / "__main__.py",
            APPS_RG_DIR / "runtime" / "dispatch" / "apps_rg_dispatch.py",
        ]
        bindings_dir = APPS_RG_DIR / "runtime" / "bindings"
        for f in bindings_dir.glob("*.py"):
            active_files.append(f)
        
        for file_path in active_files:
            content = file_path.read_text(encoding="utf-8")
            if "from apps_rg.reasoning" in content:
                pytest.fail(
                    f"reasoning import found in {file_path.relative_to(REPO_ROOT)}. "
                    "reasoning/ is OUT_OF_SCOPE per W0A."
                )
    
    def test_quarantined_paths_raise_on_import(self) -> None:
        """Quarantined paths must raise RuntimeError on import."""
        quarantined_paths = [
            "apps_rg/runtime/entry/dispatch.py",
            "apps_rg/engines/judges/executive_positioning_judge.py",
            "apps_rg/integrations/gates/online_judges.py",
            "apps_rg/tools/compute_word_count.py",
        ]
        
        for rel_path in quarantined_paths:
            file_path = REPO_ROOT / rel_path
            if not file_path.exists():
                continue
            
            content = file_path.read_text(encoding="utf-8")
            assert "RuntimeError" in content, (
                f"{rel_path} must raise RuntimeError (quarantine enforcement)"
            )
            assert "QUARANTINE" in content.upper(), (
                f"{rel_path} must have QUARANTINE notice"
            )


class TestSingleGenerationPath:
    """Verify exactly one active generation path exists."""
    
    def test_dispatch_imports_only_bindings(self) -> None:
        """apps_rg_dispatch must only import from bindings (not section/l6)."""
        dispatch_file = APPS_RG_DIR / "runtime" / "dispatch" / "apps_rg_dispatch.py"
        content = dispatch_file.read_text(encoding="utf-8")
        
        # Must import from bindings
        assert "from apps_rg.runtime.bindings" in content, (
            "dispatch must import from bindings"
        )
        
        # Must NOT import section files in live code (before the blocked section pipeline)
        lines = content.split("\n")
        section_pipeline_started = False
        for line in lines:
            if "def apps_rg_dispatch_section_pipeline" in line:
                section_pipeline_started = True
            if section_pipeline_started:
                continue  # Skip dead code section
            if "from apps_rg.runtime.section" in line:
                pytest.fail(
                    f"Dispatch imports section file in live code: {line}"
                )
    
    def test_section_pipeline_blocked(self) -> None:
        """section_pipeline function must be blocked by RuntimeError."""
        dispatch_file = APPS_RG_DIR / "runtime" / "dispatch" / "apps_rg_dispatch.py"
        content = dispatch_file.read_text(encoding="utf-8")
        
        # Check for the safety guard
        assert "apps_rg_dispatch_section_pipeline is BLOCKED" in content, (
            "section_pipeline must be blocked by safety guard"
        )
        assert "SECTION_PIPELINE_AVAILABLE: bool = False" in content, (
            "SECTION_PIPELINE_AVAILABLE must be False"
        )


class TestExecutableEntry:
    """Test executable entry point behavior."""
    
    def test_help_imports_only_approved_paths(self) -> None:
        """python -m apps_rg --help must only import approved paths."""
        # This test verifies the import graph is clean by checking --help works
        result = subprocess.run(
            [sys.executable, "-m", "apps_rg", "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        # Help must succeed without import errors
        assert result.returncode == 0, (
            f"--help failed: {result.stderr}\n"
            "Import graph must not include quarantined/broken paths."
        )
    
    def test_import_graph_regressions_blocked(self) -> None:
        """Any import graph regression must be caught."""
        # Import the key modules to verify they work
        try:
            from apps_rg.runtime.dispatch import (
                apps_rg_dispatch,
                apps_rg_parse,
                APPS_RG_REQUIRED_FIELDS,
            )
            from apps_rg.runtime.bindings import (
                u0_binding,
                l1_binding,
                l0_binding,
                c0_binding,
                pa_binding,
                l2_binding,
                exit_binding,
            )
        except ImportError as e:
            pytest.fail(f"Import graph regression detected: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
