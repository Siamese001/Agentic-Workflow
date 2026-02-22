"""Tests for tooling/apps_* boundary guard."""

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Add ops_scripts/ci to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ops_scripts" / "ci"))

from check_tooling_apps_boundary import ToolingAppsBoundaryChecker


@pytest.mark.unit_min_deps
def test_clean_tooling_imports_allowed():
    """Tooling modules with no apps_* imports should pass."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        tooling_dir = repo_root / "tools" / "evidence"
        tooling_dir.mkdir(parents=True)
        
        # Create a clean tooling file
        clean_file = tooling_dir / "clean_runner.py"
        clean_file.write_text("""
import sys
from pathlib import Path

def main():
    print("Clean tooling")
""", encoding="utf-8")
        
        checker = ToolingAppsBoundaryChecker(repo_root)
        violations = checker.check()
        
        assert len(violations) == 0


@pytest.mark.unit_min_deps
def test_apps_lic_import_forbidden():
    """Importing apps_lic should trigger violation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        tooling_dir = repo_root / "tools" / "evidence"
        tooling_dir.mkdir(parents=True)
        
        # Create a file with forbidden import
        bad_file = tooling_dir / "bad_runner.py"
        bad_file.write_text("""
import apps_lic.engines.lic_spine_adapter

def main():
    pass
""", encoding="utf-8")
        
        checker = ToolingAppsBoundaryChecker(repo_root)
        violations = checker.check()
        
        assert len(violations) == 1
        assert "apps_lic" in violations[0]
        assert "Forbidden import" in violations[0]


@pytest.mark.unit_min_deps
def test_apps_rg_from_import_forbidden():
    """from apps_rg import should trigger violation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        tooling_dir = repo_root / "ops_scripts" / "ci"
        tooling_dir.mkdir(parents=True)
        
        # Create a file with forbidden from import
        bad_file = tooling_dir / "bad_checker.py"
        bad_file.write_text("""
from apps_rg.engines import rg_spine_adapter

def check():
    pass
""", encoding="utf-8")
        
        checker = ToolingAppsBoundaryChecker(repo_root)
        violations = checker.check()
        
        assert len(violations) == 1
        assert "apps_rg" in violations[0]
        assert "Forbidden import" in violations[0]


@pytest.mark.unit_min_deps
def test_apps_shared_import_forbidden():
    """Importing apps_shared should trigger violation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        tooling_dir = repo_root / "tools" / "evidence"
        tooling_dir.mkdir(parents=True)
        
        # Create a file with forbidden import
        bad_file = tooling_dir / "bad_util.py"
        bad_file.write_text("""
from apps_shared.utils import determinism_util

def helper():
    pass
""", encoding="utf-8")
        
        checker = ToolingAppsBoundaryChecker(repo_root)
        violations = checker.check()
        
        assert len(violations) == 1
        assert "apps_shared" in violations[0]


@pytest.mark.unit_min_deps
def test_string_references_allowed():
    """String references to apps_* (e.g., in INSPECTED_FILES) should be allowed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        tooling_dir = repo_root / "tools" / "evidence"
        tooling_dir.mkdir(parents=True)
        
        # Create a file with string references (allowed)
        ok_file = tooling_dir / "ok_runner.py"
        ok_file.write_text("""
inspected = [
    "apps_lic/engines/lic_spine_adapter.py",
    "apps_rg/engines/rg_spine_adapter.py",
    "apps_shared/spine/base_spine_adapter.py",
]

def main():
    for path in inspected:
        print(path)
""", encoding="utf-8")
        
        checker = ToolingAppsBoundaryChecker(repo_root)
        violations = checker.check()
        
        assert len(violations) == 0


@pytest.mark.unit_min_deps
def test_multiple_violations_reported():
    """Multiple violations in same file should all be reported."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        tooling_dir = repo_root / "tools" / "evidence"
        tooling_dir.mkdir(parents=True)
        
        # Create a file with multiple violations
        bad_file = tooling_dir / "multi_bad.py"
        bad_file.write_text("""
import apps_lic.engines
from apps_rg.engines import something
import apps_shared.utils

def main():
    pass
""", encoding="utf-8")
        
        checker = ToolingAppsBoundaryChecker(repo_root)
        violations = checker.check()
        
        assert len(violations) == 3


@pytest.mark.unit_min_deps
def test_syntax_error_reported():
    """Files with syntax errors should be reported."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        tooling_dir = repo_root / "tools" / "evidence"
        tooling_dir.mkdir(parents=True)
        
        # Create a file with syntax error
        bad_file = tooling_dir / "syntax_error.py"
        bad_file.write_text("""
def main(
    # Missing closing paren
""", encoding="utf-8")
        
        checker = ToolingAppsBoundaryChecker(repo_root)
        violations = checker.check()
        
        assert len(violations) == 1
        assert "Syntax error" in violations[0]
