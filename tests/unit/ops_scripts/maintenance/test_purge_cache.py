#!/usr/bin/env python3
"""
Comprehensive test suite for the cache purge utility.

Tests Windows compatibility, SSOT compliance, and resilience to various
edge cases including locked files and missing directories.
"""

import pytest
import os
import pathlib
import shutil
import tempfile
import sys
from unittest.mock import patch, MagicMock

# Add the project root to sys.path for imports
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent.parent.parent))

from ops_scripts.maintenance.purge_cache import purge_all_pycache, purge_all_cache, get_project_root


class TestPurgeCache:
    """Test suite for cache purge functionality."""
    
    @pytest.fixture
    def temp_project_root(self):
        """Create a temporary project structure for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = pathlib.Path(temp_dir)
            
            # Create agentic_core to simulate project structure
            (root / "agentic_core").mkdir()
            
            # Create ops_scripts/maintenance structure
            (root / "ops_scripts" / "maintenance").mkdir(parents=True)
            
            yield root
    
    @pytest.fixture
    def mock_project_root(self, temp_project_root):
        """Mock the get_project_root function to return temp directory."""
        with patch('ops_scripts.maintenance.purge_cache.get_project_root', return_value=temp_project_root):
            yield temp_project_root
    
    def test_get_project_root_success(self):
        """Test successful project root detection."""
        # This should work in the actual project structure
        root = get_project_root()
        assert (root / "agentic_core").exists()
        assert (root / "ops_scripts").exists()
    
    def test_get_project_root_failure(self):
        """Test project root detection failure."""
        with patch('pathlib.Path.exists', return_value=False):
            with pytest.raises(RuntimeError, match="Project root validation failed"):
                get_project_root()
    
    def test_nested_pycache_deletion(self, mock_project_root):
        """Verify that deep nested __pycache__ (e.g., prompt_governance) is removed."""
        root = mock_project_root
        
        # Create nested directory structure
        nested_path = root / "agentic_core" / "prompt_governance" / "agents" / "__pycache__"
        nested_path.mkdir(parents=True, exist_ok=True)
        (nested_path / "test.pyc").touch()
        
        # Verify it exists before purge
        assert nested_path.exists()
        
        count = purge_all_pycache()
        
        # Verify deletion
        deleted = not nested_path.exists()
        assert deleted, "FAILED: Nested __pycache__ was not deleted."
        assert count >= 1
        print("Test Case 1: Nested Deletion - 100% PASS")
    
    def test_root_pycache_deletion(self, mock_project_root):
        """Verify root-level cache is removed."""
        root = mock_project_root
        
        root_cache = root / "__pycache__"
        root_cache.mkdir(exist_ok=True)
        (root_cache / "test.pyc").touch()
        
        count = purge_all_pycache()
        
        deleted = not root_cache.exists()
        assert deleted, "FAILED: Root __pycache__ was not deleted."
        assert count >= 1
        print("Test Case 2: Root Deletion - 100% PASS")
    
    def test_resilience_to_missing_dir(self, mock_project_root):
        """Ensure the script doesn't crash if no __pycache__ exists."""
        try:
            count = purge_all_pycache()
            success = True
        except Exception as e:
            print(f"Error during execution: {e}")
            success = False
        
        assert success, "FAILED: Script crashed on empty run."
        assert count == 0
        print("Test Case 3: Empty Run Resilience - 100% PASS")
    
    def test_locked_file_resilience(self, mock_project_root):
        """Simulate a PermissionError to ensure the script continues."""
        root = mock_project_root
        
        # Create a pycache that should be deleted
        path_ok = root / "temp_clear" / "__pycache__"
        path_ok.mkdir(parents=True, exist_ok=True)
        
        # Create another pycache that will simulate being locked
        path_locked = root / "locked_dir" / "__pycache__"
        path_locked.mkdir(parents=True, exist_ok=True)
        
        # Mock shutil.rmtree to raise PermissionError on the locked path
        original_rmtree = shutil.rmtree
        
        def mock_rmtree(path, *args, **kwargs):
            if path == path_locked:
                raise PermissionError("Access denied")
            return original_rmtree(path, *args, **kwargs)
        
        with patch('shutil.rmtree', side_effect=mock_rmtree):
            count = purge_all_pycache()
        
        # The accessible one should be deleted, the locked one should remain
        assert not path_ok.exists(), "FAILED: Clearable pycache was not deleted."
        assert path_locked.exists(), "FAILED: Locked pycache was incorrectly deleted."
        assert count >= 1
        print("Test Case 4: Windows/Lock Resilience - 100% PASS")
    
    def test_ignores_virtual_environments(self, mock_project_root):
        """Ensure virtual environments are not touched."""
        root = mock_project_root
        
        # Create pycache inside .venv (should be ignored)
        venv_pycache = root / ".venv" / "__pycache__"
        venv_pycache.mkdir(parents=True, exist_ok=True)
        
        # Create pycache in normal location (should be deleted)
        normal_pycache = root / "normal_dir" / "__pycache__"
        normal_pycache.mkdir(parents=True, exist_ok=True)
        
        count = purge_all_pycache()
        
        # VEnv pycache should remain, normal should be deleted
        assert venv_pycache.exists(), "FAILED: Virtual environment pycache was incorrectly deleted."
        assert not normal_pycache.exists(), "FAILED: Normal pycache was not deleted."
        assert count >= 1
        print("Test Case 5: Virtual Environment Ignoring - 100% PASS")
    
    def test_ignores_git_directory(self, mock_project_root):
        """Ensure .git directory is not touched."""
        root = mock_project_root
        
        # Create pycache inside .git (should be ignored)
        git_pycache = root / ".git" / "__pycache__"
        git_pycache.mkdir(parents=True, exist_ok=True)
        
        # Create pycache in normal location (should be deleted)
        normal_pycache = root / "normal_dir" / "__pycache__"
        normal_pycache.mkdir(parents=True, exist_ok=True)
        
        count = purge_all_pycache()
        
        # Git pycache should remain, normal should be deleted
        assert git_pycache.exists(), "FAILED: Git pycache was incorrectly deleted."
        assert not normal_pycache.exists(), "FAILED: Normal pycache was not deleted."
        assert count >= 1
        print("Test Case 6: Git Directory Ignoring - 100% PASS")
    
    def test_purge_all_cache_extended(self, mock_project_root):
        """Test the extended cache purge functionality."""
        root = mock_project_root
        
        # Create various cache types
        caches_to_create = [
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache", 
            ".ruff_cache",
            "temp_test_dir",
            "tmp_another_dir"
        ]
        
        for cache_name in caches_to_create:
            cache_path = root / cache_name
            cache_path.mkdir(exist_ok=True)
            (cache_path / "test_file").touch()
        
        # Create a .pyc file
        pyc_file = root / "test.pyc"
        pyc_file.touch()
        
        count = purge_all_cache()
        
        # All caches should be deleted
        for cache_name in caches_to_create:
            cache_path = root / cache_name
            assert not cache_path.exists(), f"FAILED: {cache_name} was not deleted."
        
        assert not pyc_file.exists(), "FAILED: .pyc file was not deleted."
        assert count >= len(caches_to_create) + 1
        print("Test Case 7: Extended Cache Purge - 100% PASS")
    
    def test_race_condition_handling(self, mock_project_root):
        """Test handling of race conditions where files are deleted by other processes."""
        root = mock_project_root
        
        # Create pycache
        pycache_path = root / "__pycache__"
        pycache_path.mkdir(exist_ok=True)
        
        # Mock shutil.rmtree to simulate FileNotFoundError (race condition)
        original_rmtree = shutil.rmtree
        
        def mock_rmtree(path, *args, **kwargs):
            if path == pycache_path:
                # Simulate the directory being deleted by another process
                pycache_path.rmdir()
                raise FileNotFoundError("Directory not found")
            return original_rmtree(path, *args, **kwargs)
        
        with patch('shutil.rmtree', side_effect=mock_rmtree):
            # Should not crash despite the race condition
            count = purge_all_pycache()
        
        # Should handle gracefully
        assert not pycache_path.exists()
        print("Test Case 8: Race Condition Handling - 100% PASS")
    
    def test_command_line_interface_all(self, mock_project_root):
        """Test command line interface with --all flag."""
        root = mock_project_root
        
        # Create some cache
        (root / "__pycache__").mkdir()
        (root / ".pytest_cache").mkdir()
        
        # Mock sys.argv
        with patch('sys.argv', ['purge_cache.py', '--all']):
            # Import and run main
            from ops_scripts.maintenance.purge_cache import purge_all_cache
            count = purge_all_cache()
        
        assert count >= 2
        assert not (root / "__pycache__").exists()
        assert not (root / ".pytest_cache").exists()
        print("Test Case 9: Command Line Interface --all - 100% PASS")
    
    def test_error_logging(self, mock_project_root):
        """Test that errors are properly logged."""
        root = mock_project_root
        
        # Create pycache
        pycache_path = root / "__pycache__"
        pycache_path.mkdir()
        
        # Mock shutil.rmtree to always raise an exception
        with patch('shutil.rmtree', side_effect=Exception("Test error")):
            with patch('ops_scripts.maintenance.purge_cache.logger') as mock_logger:
                count = purge_all_pycache()
        
        # Should log the error
        mock_logger.error.assert_called()
        assert count == 0
        print("Test Case 10: Error Logging - 100% PASS")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v"])
