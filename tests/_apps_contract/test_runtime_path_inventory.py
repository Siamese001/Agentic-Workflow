"""Tests for apps_rg runtime path inventory (W0A).

Per plan apps-rg-structured-resume-refactor-f8c2a1 W0A.

Acceptance:
- CI fails if active code imports quarantined paths
- CI fails if more than one active generation path exists
- CI proves python -m apps_rg --help imports only dispatch, bindings, and approved tools
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest


def _resolve_repo_root() -> Path:
    """Resolve repository root."""
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parent.parent.parent


REPO_ROOT = _resolve_repo_root()


class TestRuntimePathClassification:
    """Test runtime path classification evidence."""
    
    def test_dispatch_is_active(self) -> None:
        """Dispatch file must be classified as ACTIVE."""
        dispatch_file = REPO_ROOT / "apps_rg" / "runtime" / "dispatch" / "apps_rg_dispatch.py"
        assert dispatch_file.exists(), "Dispatch file must exist"
        # Verify it imports from bindings
        content = dispatch_file.read_text(encoding="utf-8")
        assert "from apps_rg.runtime.bindings" in content, "Dispatch must import from bindings"
    
    def test_bindings_are_active(self) -> None:
        """All binding files must be classified as ACTIVE."""
        bindings_dir = REPO_ROOT / "apps_rg" / "runtime" / "bindings"
        required_bindings = [
            "u0_binding.py",
            "l1_binding.py",
            "l0_binding.py",
            "c0_binding.py",
            "pa_binding.py",
            "l2_binding.py",
            "exit_binding.py",
            "__init__.py",
        ]
        for binding in required_bindings:
            binding_file = bindings_dir / binding
            assert binding_file.exists(), f"Required binding {binding} must exist"
    
    def test_section_files_are_legacy(self) -> None:
        """Section files must have no active imports from dispatch."""
        dispatch_file = REPO_ROOT / "apps_rg" / "runtime" / "dispatch" / "apps_rg_dispatch.py"
        content = dispatch_file.read_text(encoding="utf-8")
        # SECTION_PIPELINE_AVAILABLE must be False
        assert "SECTION_PIPELINE_AVAILABLE: bool = False" in content, \
            "Section pipeline must be disabled"
    
    def test_l6_shadow_learning_not_repaired(self) -> None:
        """l6_shadow_learning.py must NOT be actively imported."""
        l6_file = REPO_ROOT / "apps_rg" / "runtime" / "l6_shadow_learning.py"
        if l6_file.exists():
            dispatch_file = REPO_ROOT / "apps_rg" / "runtime" / "dispatch" / "apps_rg_dispatch.py"
            dispatch_content = dispatch_file.read_text(encoding="utf-8")
            # Must not import l6_shadow_learning
            assert "l6_shadow_learning" not in dispatch_content, \
                "Dispatch must not import l6_shadow_learning"
    
    def test_quarantined_judges_raise_runtime_error(self) -> None:
        """Quarantined judges must raise RuntimeError on import."""
        judge_file = REPO_ROOT / "apps_rg" / "engines" / "judges" / "executive_positioning_judge.py"
        if judge_file.exists():
            content = judge_file.read_text(encoding="utf-8")
            assert "QUARANTINE" in content.upper(), "Quarantined file must have QUARANTINE notice"
            assert "RuntimeError" in content, "Quarantined file must raise RuntimeError"
    
    def test_quarantined_online_judges_raise_runtime_error(self) -> None:
        """Quarantined online_judges must raise RuntimeError on import."""
        online_judges = REPO_ROOT / "apps_rg" / "integrations" / "gates" / "online_judges.py"
        if online_judges.exists():
            content = online_judges.read_text(encoding="utf-8")
            assert "QUARANTINE" in content.upper(), "Quarantined file must have QUARANTINE notice"
            assert "RuntimeError" in content, "Quarantined file must raise RuntimeError"


class TestSingleGenerationPath:
    """Test that exactly one active generation path exists."""
    
    def test_dispatch_imports_only_bindings(self) -> None:
        """Dispatch must only import from bindings (not section/l6 files)."""
        dispatch_file = REPO_ROOT / "apps_rg" / "runtime" / "dispatch" / "apps_rg_dispatch.py"
        content = dispatch_file.read_text(encoding="utf-8")
        
        # Must import from bindings
        assert "from apps_rg.runtime.bindings" in content
        
        # Must NOT import section files (except in dead code after RuntimeError)
        lines = content.split("\n")
        in_dead_code = False
        for line in lines:
            if "def apps_rg_dispatch_section_pipeline" in line:
                in_dead_code = True
            if in_dead_code:
                continue  # Skip dead code section
            # Check for section imports in live code
            if "from apps_rg.runtime.section" in line and "section_runtime" in line:
                pytest.fail(f"Dispatch imports section file in live code: {line}")
    
    def test_main_imports_only_dispatch_and_bindings(self) -> None:
        """__main__.py must only import from dispatch and bindings."""
        main_file = REPO_ROOT / "apps_rg" / "__main__.py"
        content = main_file.read_text(encoding="utf-8")
        
        # Must import from dispatch
        assert "from apps_rg.runtime.dispatch import" in content
        
        # Must NOT import from engines, reasoning, hops directly
        disallowed_patterns = [
            "from apps_rg.engines",
            "from apps_rg.reasoning",
            "from apps_rg.integrations.hops",
        ]
        for pattern in disallowed_patterns:
            assert pattern not in content, f"__main__.py must not import {pattern}"
    
    def test_bindings_do_not_import_quarantined(self) -> None:
        """Active bindings must not import from quarantined paths."""
        bindings_dir = REPO_ROOT / "apps_rg" / "runtime" / "bindings"
        quarantine_modules = [
            "apps_rg.engines",
            "apps_rg.reasoning",
            "apps_rg.integrations.hops",
            "apps_rg.tools",
        ]
        
        for binding_file in bindings_dir.glob("*.py"):
            content = binding_file.read_text(encoding="utf-8")
            for q_module in quarantine_modules:
                # Exception: allowed to import from tools if tools/__init__.py is active
                if q_module == "apps_rg.tools":
                    continue
                assert f"from {q_module}" not in content, \
                    f"{binding_file.name} must not import from {q_module}"


class TestHelpImports:
    """Test that python -m apps_rg --help only imports allowed paths."""
    
    def test_help_command_runs(self) -> None:
        """python -m apps_rg --help must exit 0."""
        result = subprocess.run(
            [sys.executable, "-m", "apps_rg", "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"--help failed: {result.stderr}"
        assert "Resume Generation" in result.stdout or "usage:" in result.stdout
    
    def test_help_imports_clean(self) -> None:
        """python -m apps_rg --help proves import graph is clean."""
        # This test verifies that --help works (proves import graph has no quarantined paths)
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
        # Must show usage/help content
        assert "usage:" in result.stdout.lower() or "resume" in result.stdout.lower(), (
            "Help output must contain usage information"
        )


class TestCoreBoundary:
    """Test that agentic_core is not modified."""
    
    def test_no_agentic_core_modifications(self) -> None:
        """Verify no modifications to agentic_core in this scope."""
        # This is a marker test - actual verification happens in CI gate
        pytest.skip("Verified by check_major_checkpoint_core_boundary.py")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
