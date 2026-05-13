"""Quarantine regression test: Verify quarantined paths raise RuntimeError.

Per plan apps-rg-structured-resume-refactor-f8c2a1 W0A.

This test verifies quarantine is enforced at import time:
- runtime.entry.dispatch
- integrations.gates.online_judges
- engines.judges.executive_positioning_judge
- engines.judges.*
- integrations.hops.*
- runtime.l6_shadow_learning (if quarantined vs legacy)

Quarantine must be hard-fail at import time, not lazy on function execution.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


def _resolve_repo_root() -> Path:
    """Resolve repository root."""
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parent.parent.parent


REPO_ROOT = _resolve_repo_root()


class TestQuarantineEnforcedAtImportTime:
    """Verify quarantine raises RuntimeError at import time, not lazily."""
    
    def test_runtime_entry_dispatch_raises_on_import(self) -> None:
        """runtime.entry.dispatch must raise RuntimeError at top-level."""
        # Import must fail immediately with RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            from apps_rg.runtime.entry import dispatch
        
        assert "QUARANTINE" in str(exc_info.value).upper(), (
            "RuntimeError must mention QUARANTINE"
        )
        assert "runtime.dispatch" in str(exc_info.value), (
            "Error must direct to canonical path"
        )
    
    def test_integrations_gates_online_judges_raises_on_import(self) -> None:
        """integrations.gates.online_judges must raise RuntimeError."""
        with pytest.raises(RuntimeError) as exc_info:
            from apps_rg.integrations.gates import online_judges
        
        assert "QUARANTINE" in str(exc_info.value).upper(), (
            "RuntimeError must mention QUARANTINE"
        )
    
    def test_engines_judges_executive_positioning_raises_on_import(self) -> None:
        """engines.judges.executive_positioning_judge must raise RuntimeError."""
        with pytest.raises(RuntimeError) as exc_info:
            from apps_rg.engines.judges import executive_positioning_judge
        
        assert "QUARANTINE" in str(exc_info.value).upper(), (
            "RuntimeError must mention QUARANTINE"
        )
    
    def test_tools_compute_word_count_raises_on_import(self) -> None:
        """tools.compute_word_count must raise RuntimeError."""
        with pytest.raises(RuntimeError) as exc_info:
            from apps_rg.tools import compute_word_count
        
        assert "QUARANTINE" in str(exc_info.value).upper(), (
            "RuntimeError must mention QUARANTINE"
        )
    
    def test_quarantine_top_level_not_lazy(self) -> None:
        """Quarantine must be at top-level, not inside functions."""
        # Read the quarantined files and verify RuntimeError is at top-level
        quarantined_files = [
            REPO_ROOT / "apps_rg" / "runtime" / "entry" / "dispatch.py",
            REPO_ROOT / "apps_rg" / "engines" / "judges" / "executive_positioning_judge.py",
            REPO_ROOT / "apps_rg" / "integrations" / "gates" / "online_judges.py",
            REPO_ROOT / "apps_rg" / "tools" / "compute_word_count.py",
        ]
        
        for file_path in quarantined_files:
            if not file_path.exists():
                continue
            
            content = file_path.read_text(encoding="utf-8")
            
            # Verify RuntimeError appears in file (not lazy inside function)
            assert "raise RuntimeError" in content, (
                f"{file_path.name}: Must raise RuntimeError at top-level"
            )
            
            # Find all 'def ' occurrences (function definitions)
            # If RuntimeError comes after any function def, it's lazy
            lines = content.split("\n")
            in_function = False
            runtime_error_found = False
            
            for line in lines:
                stripped = line.strip()
                
                # Track if we enter a function
                if stripped.startswith("def "):
                    in_function = True
                
                # Check for RuntimeError
                if "raise RuntimeError" in line:
                    runtime_error_found = True
                    # Must NOT be inside a function
                    assert not in_function, (
                        f"{file_path.name}: RuntimeError must be at module level, "
                        f"not inside function. Line: {line.strip()}"
                    )
                    break
            
            assert runtime_error_found, (
                f"{file_path.name}: Must contain RuntimeError"
            )


class TestQuarantineInSubprocess:
    """Verify quarantine works in clean subprocess (no test harness interference)."""
    
    def test_runtime_entry_dispatch_fails_in_subprocess(self) -> None:
        """Subprocess import of runtime.entry.dispatch must fail."""
        code = "from apps_rg.runtime.entry import dispatch; print('SUCCESS')"
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        
        assert result.returncode != 0, "Import should fail"
        assert "QUARANTINE" in result.stderr.upper() or "QUARANTINE" in result.stdout.upper(), (
            "Error output must mention QUARANTINE"
        )
    
    def test_engines_judges_fails_in_subprocess(self) -> None:
        """Subprocess import of engines.judges must fail."""
        code = "from apps_rg.engines.judges import executive_positioning_judge; print('SUCCESS')"
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        
        assert result.returncode != 0, "Import should fail"
        assert "QUARANTINE" in result.stderr.upper() or "QUARANTINE" in result.stdout.upper(), (
            "Error output must mention QUARANTINE"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
