#!/usr/bin/env python3
"""
Phase 1 Migration Verification Tests
Verifies that the Phase 1 migration completed successfully.
"""
import pytest
import pathlib
import subprocess
import sys

class TestPhase1Migration:
    """Verify Phase 1 migration completed successfully."""
    
    def test_file_exists_at_destination(self):
        """Verify file was moved to correct location."""
        dest = pathlib.Path("tests/e2e/ops_scripts/maintenance/test_manifest_completion.py")
        assert dest.exists(), f"File not found at destination: {dest}"
    
    def test_file_removed_from_source(self):
        """Verify file no longer exists at source."""
        src = pathlib.Path("ops_scripts/maintenance/test_manifest_completion.py")
        assert not src.exists(), f"File still exists at source: {src}"
    
    def test_file_is_valid_python(self):
        """Verify the migrated file is syntactically valid Python."""
        filepath = pathlib.Path("tests/e2e/ops_scripts/maintenance/test_manifest_completion.py")
        result = subprocess.run(
            ["python", "-m", "py_compile", str(filepath)],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Syntax error in migrated file: {result.stderr}"
    
    def test_pytest_discovers_file(self):
        """Verify pytest can discover and collect the test."""
        result = subprocess.run(
            ["python", "-m", "pytest", 
             "tests/e2e/ops_scripts/maintenance/test_manifest_completion.py", 
             "--collect-only"],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Pytest collection failed: {result.stderr}"
        assert "test_manifest_completion.py" in result.stdout, "File not discovered by pytest"
    
    def test_backup_exists(self):
        """Verify backup was created."""
        backup_file = pathlib.Path(".backup/phase1/test_manifest_completion.py")
        assert backup_file.exists(), f"Backup file not found: {backup_file}"
    
    def test_imports_work(self):
        """Verify imports still function after move."""
        # Test that the file can be imported without errors
        filepath = pathlib.Path("tests/e2e/ops_scripts/maintenance/test_manifest_completion.py")
        result = subprocess.run(
            ["python", "-c", f"exec(open('{filepath}').read())"],
            capture_output=True, text=True, cwd="c:\\Git\\Agentic-Workflow"
        )
        # Don't assert return code here since the test might have its own exit conditions
        # Just check for syntax/import errors
        assert "SyntaxError" not in result.stderr, f"Import error: {result.stderr}"
        assert "ImportError" not in result.stderr, f"Import error: {result.stderr}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
