#!/usr/bin/env python3
"""
Unit Tests for Scan Guard

Verifies:
1. Dangerous directory blocking (prevents hangs)
2. DeprecationWarning for rglob usage
3. RuntimeWarning for backup directory scans

Opportunity #3: rglob Scan Proliferation - Phase 6 Hardening
"""
import sys
import tempfile
import shutil
import warnings
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.utils.scan_guard import guarded_rglob, DANGEROUS_DIRECTORIES


class TestScanGuardBlocksBackups:
    """Test Case 1: Dangerous Directory Blocking
    
    Verify that guarded_rglob blocks scans of dangerous directories
    and returns an empty iterator.
    """
    
    def test_blocks_sovereign_healing_backup(self):
        """Verify .sovereign_healing_backup is blocked."""
        backup_path = Path("/fake/path/.sovereign_healing_backup/subdir")
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = list(guarded_rglob(backup_path, "*.py"))
            
            # Should return empty list
            assert len(result) == 0, "Dangerous directory scan should return empty list"
            
            # Should issue RuntimeWarning
            runtime_warnings = [warning for warning in w if issubclass(warning.category, RuntimeWarning)]
            assert len(runtime_warnings) > 0, "Should issue RuntimeWarning for dangerous directory"
            assert "BLOCKED" in str(runtime_warnings[0].message)
    
    def test_blocks_healing_backups(self):
        """Verify healing_backups is blocked."""
        backup_path = Path("/fake/path/healing_backups/subdir")
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = list(guarded_rglob(backup_path, "*.py"))
            
            assert len(result) == 0, "healing_backups scan should return empty list"
            
            runtime_warnings = [warning for warning in w if issubclass(warning.category, RuntimeWarning)]
            assert len(runtime_warnings) > 0, "Should issue RuntimeWarning"
    
    def test_blocks_git_directory(self):
        """Verify .git is blocked."""
        git_path = Path("/fake/path/.git/objects")
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = list(guarded_rglob(git_path, "*"))
            
            assert len(result) == 0, ".git scan should return empty list"
            
            runtime_warnings = [warning for warning in w if issubclass(warning.category, RuntimeWarning)]
            assert len(runtime_warnings) > 0, "Should issue RuntimeWarning"
    
    def test_blocks_pycache(self):
        """Verify __pycache__ is blocked."""
        pycache_path = Path("/fake/path/__pycache__")
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = list(guarded_rglob(pycache_path, "*.pyc"))
            
            assert len(result) == 0, "__pycache__ scan should return empty list"
            
            runtime_warnings = [warning for warning in w if issubclass(warning.category, RuntimeWarning)]
            assert len(runtime_warnings) > 0, "Should issue RuntimeWarning"
    
    def test_allows_safe_directories(self):
        """Verify safe directories are not blocked."""
        # Create a real temporary directory for this test
        temp_dir = Path(tempfile.mkdtemp())
        try:
            # Create a test file
            test_file = temp_dir / "test.py"
            test_file.write_text("# test")
            
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                result = list(guarded_rglob(temp_dir, "*.py"))
                
                # Should find the file
                assert len(result) == 1, "Safe directory scan should find files"
                
                # Should only have DeprecationWarning, not RuntimeWarning
                runtime_warnings = [warning for warning in w if issubclass(warning.category, RuntimeWarning)]
                assert len(runtime_warnings) == 0, "Safe directory should not trigger RuntimeWarning"
                
                deprecation_warnings = [warning for warning in w if issubclass(warning.category, DeprecationWarning)]
                assert len(deprecation_warnings) > 0, "Should still issue DeprecationWarning for rglob usage"
        finally:
            shutil.rmtree(temp_dir)


class TestScanGuardDeprecationWarnings:
    """Test Case 2: DeprecationWarning for rglob Usage
    
    Verify that guarded_rglob issues deprecation warnings.
    """
    
    def test_issues_deprecation_warning(self):
        """Verify DeprecationWarning is issued for rglob usage."""
        temp_dir = Path(tempfile.mkdtemp())
        try:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                _ = list(guarded_rglob(temp_dir, "*.py"))
                
                deprecation_warnings = [warning for warning in w if issubclass(warning.category, DeprecationWarning)]
                assert len(deprecation_warnings) > 0, "Should issue DeprecationWarning"
                assert "FileCache" in str(deprecation_warnings[0].message), "Should mention FileCache"
        finally:
            shutil.rmtree(temp_dir)
    
    def test_warning_mentions_file_cache(self):
        """Verify warning message mentions FileCache."""
        temp_dir = Path(tempfile.mkdtemp())
        try:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                _ = list(guarded_rglob(temp_dir, "*.py"))
                
                deprecation_warnings = [warning for warning in w if issubclass(warning.category, DeprecationWarning)]
                message = str(deprecation_warnings[0].message)
                assert "file_cache" in message.lower(), "Should reference file_cache module"
        finally:
            shutil.rmtree(temp_dir)


class TestDangerousDirectoriesConstant:
    """Test Case 3: DANGEROUS_DIRECTORIES Constant
    
    Verify the DANGEROUS_DIRECTORIES set contains expected values.
    """
    
    def test_contains_sovereign_healing_backup(self):
        """Verify .sovereign_healing_backup is in DANGEROUS_DIRECTORIES."""
        assert '.sovereign_healing_backup' in DANGEROUS_DIRECTORIES
    
    def test_contains_healing_backups(self):
        """Verify healing_backups is in DANGEROUS_DIRECTORIES."""
        assert 'healing_backups' in DANGEROUS_DIRECTORIES
    
    def test_contains_git(self):
        """Verify .git is in DANGEROUS_DIRECTORIES."""
        assert '.git' in DANGEROUS_DIRECTORIES
    
    def test_contains_pycache(self):
        """Verify __pycache__ is in DANGEROUS_DIRECTORIES."""
        assert '__pycache__' in DANGEROUS_DIRECTORIES
    
    def test_contains_node_modules(self):
        """Verify node_modules is in DANGEROUS_DIRECTORIES."""
        assert 'node_modules' in DANGEROUS_DIRECTORIES


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
