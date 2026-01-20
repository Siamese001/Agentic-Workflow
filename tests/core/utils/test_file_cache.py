#!/usr/bin/env python3
"""
Unit Tests for FileCache

Verifies:
1. Singleton behavior (two instances share data)
2. Exclusion logic (backup folders are ignored)
3. Invalidation logic (create file, invalidate, check if found)
4. Extension filtering
5. Lazy loading behavior

Opportunity #3: rglob Scan Proliferation

NOTE: Most tests use a temporary directory for speed.
Only exclusion tests use PROJECT_ROOT (with os.walk pruning, this is fast).
"""
import sys
import tempfile
import shutil
from pathlib import Path
from typing import List

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.utils.file_cache import FileCache, get_python_files, invalidate_cache


def create_test_directory() -> Path:
    """Create a temporary directory with test files."""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create Python files
    (temp_dir / "test1.py").write_text("# test1")
    (temp_dir / "test2.py").write_text("# test2")
    
    # Create markdown files
    (temp_dir / "README.md").write_text("# README")
    
    # Create subdirectory with files
    subdir = temp_dir / "subdir"
    subdir.mkdir()
    (subdir / "module.py").write_text("# module")
    
    # Create excluded directories (should be skipped)
    pycache = temp_dir / "__pycache__"
    pycache.mkdir()
    (pycache / "cached.pyc").write_text("cached")
    
    git_dir = temp_dir / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("git config")
    
    backup_dir = temp_dir / ".sovereign_healing_backup"
    backup_dir.mkdir()
    (backup_dir / "backup.py").write_text("# backup")
    
    return temp_dir


class TestFileCacheSingleton:
    """Test Case 1: Singleton Behavior
    
    Verify two instances share the same data.
    Uses temporary directory for fast execution.
    """
    
    def setup_method(self):
        """Reset singleton and create temp directory."""
        FileCache.reset_instance()
        self.temp_dir = create_test_directory()
    
    def teardown_method(self):
        """Reset singleton and cleanup temp directory."""
        FileCache.reset_instance()
        if hasattr(self, 'temp_dir') and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_singleton_same_instance(self):
        """Verify get_instance returns the same object."""
        instance1 = FileCache.get_instance(self.temp_dir)
        instance2 = FileCache.get_instance(self.temp_dir)
        
        assert instance1 is instance2, "Singleton should return same instance"
    
    def test_singleton_shared_data(self):
        """Verify instances share cached data."""
        instance1 = FileCache.get_instance(self.temp_dir)
        _ = instance1.get_all_files()  # Populate cache
        scan_count_1 = instance1.get_scan_count()
        
        instance2 = FileCache.get_instance(self.temp_dir)
        _ = instance2.get_all_files()  # Should use cache
        scan_count_2 = instance2.get_scan_count()
        
        assert scan_count_1 == scan_count_2, "Second instance should not trigger new scan"
        assert scan_count_1 == 1, "Should only scan once"
    
    def test_reset_instance(self):
        """Verify reset_instance creates new instance."""
        instance1 = FileCache.get_instance(self.temp_dir)
        FileCache.reset_instance()
        instance2 = FileCache.get_instance(self.temp_dir)
        
        assert instance1 is not instance2, "Reset should create new instance"


class TestFileCacheExclusion:
    """Test Case 2: Exclusion Logic
    
    Verify backup folders and other excluded directories are ignored.
    Uses temporary directory with excluded folders for testing.
    """
    
    def setup_method(self):
        """Reset singleton and create temp directory with exclusions."""
        FileCache.reset_instance()
        self.temp_dir = create_test_directory()
    
    def teardown_method(self):
        """Reset singleton and cleanup."""
        FileCache.reset_instance()
        if hasattr(self, 'temp_dir') and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_sovereign_healing_backup_excluded(self):
        """Verify .sovereign_healing_backup is excluded."""
        cache = FileCache.get_instance(self.temp_dir)
        all_files = cache.get_all_files()
        
        backup_files = [f for f in all_files if '.sovereign_healing_backup' in str(f)]
        assert len(backup_files) == 0, f"Backup files should be excluded: {backup_files}"
    
    def test_pycache_excluded(self):
        """Verify __pycache__ is excluded."""
        cache = FileCache.get_instance(self.temp_dir)
        all_files = cache.get_all_files()
        
        pycache_files = [f for f in all_files if '__pycache__' in str(f)]
        assert len(pycache_files) == 0, f"__pycache__ files should be excluded: {pycache_files}"
    
    def test_git_excluded(self):
        """Verify .git is excluded."""
        cache = FileCache.get_instance(self.temp_dir)
        all_files = cache.get_all_files()
        
        git_files = [f for f in all_files if '.git' in f.parts]
        assert len(git_files) == 0, f".git files should be excluded: {git_files}"
    
    def test_valid_files_found(self):
        """Verify valid files are found (not excluded)."""
        cache = FileCache.get_instance(self.temp_dir)
        py_files = cache.get_python_files()
        
        # Should find test1.py, test2.py, subdir/module.py (3 files)
        # Should NOT find __pycache__/cached.pyc or .sovereign_healing_backup/backup.py
        assert len(py_files) == 3, f"Should find 3 Python files, found {len(py_files)}: {py_files}"


class TestFileCacheInvalidation:
    """Test Case 3: Invalidation Logic
    
    Verify cache invalidation works correctly.
    """
    
    def setup_method(self):
        """Reset singleton and create temp directory."""
        FileCache.reset_instance()
        self.temp_dir = Path(tempfile.mkdtemp())
        # Create some test files
        (self.temp_dir / "test1.py").write_text("# test1")
        (self.temp_dir / "test2.py").write_text("# test2")
    
    def teardown_method(self):
        """Cleanup temp directory and reset singleton."""
        FileCache.reset_instance()
        if hasattr(self, 'temp_dir') and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_invalidation_clears_cache(self):
        """Verify invalidate() clears the cache."""
        cache = FileCache.get_instance(self.temp_dir)
        
        # Populate cache
        _ = cache.get_all_files()
        assert cache.is_cached(), "Cache should be populated"
        
        # Invalidate
        cache.invalidate()
        assert not cache.is_cached(), "Cache should be cleared after invalidation"
    
    def test_invalidation_triggers_rescan(self):
        """Verify invalidation triggers rescan on next access."""
        cache = FileCache.get_instance(self.temp_dir)
        
        # First scan
        _ = cache.get_all_files()
        scan_count_1 = cache.get_scan_count()
        
        # Invalidate and access again
        cache.invalidate()
        _ = cache.get_all_files()
        scan_count_2 = cache.get_scan_count()
        
        assert scan_count_2 == scan_count_1 + 1, "Invalidation should trigger rescan"
    
    def test_new_file_found_after_invalidation(self):
        """Verify new files are found after invalidation."""
        cache = FileCache.get_instance(self.temp_dir)
        
        # Initial scan
        files1 = cache.get_python_files()
        initial_count = len(files1)
        
        # Create new file
        new_file = self.temp_dir / "test3.py"
        new_file.write_text("# test3")
        
        # Without invalidation, new file not found
        files2 = cache.get_python_files()
        assert len(files2) == initial_count, "New file should not be found without invalidation"
        
        # After invalidation, new file found
        cache.invalidate()
        files3 = cache.get_python_files()
        assert len(files3) == initial_count + 1, "New file should be found after invalidation"
        assert new_file in files3, "Specific new file should be in results"


class TestFileCacheExtensionFiltering:
    """Test Case 4: Extension Filtering
    
    Verify extension-based filtering works correctly.
    Uses temporary directory for fast execution.
    """
    
    def setup_method(self):
        """Reset singleton and create temp directory."""
        FileCache.reset_instance()
        self.temp_dir = create_test_directory()
    
    def teardown_method(self):
        """Reset singleton and cleanup."""
        FileCache.reset_instance()
        if hasattr(self, 'temp_dir') and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_python_files_only_py(self):
        """Verify get_files_by_extension('.py') returns only .py files."""
        cache = FileCache.get_instance(self.temp_dir)
        py_files = cache.get_files_by_extension('.py')
        
        non_py = [f for f in py_files if f.suffix.lower() != '.py']
        assert len(non_py) == 0, f"Non-.py files found: {non_py}"
        assert len(py_files) == 3, f"Should find 3 .py files: {py_files}"
    
    def test_markdown_files_only_md(self):
        """Verify get_markdown_files returns only .md files."""
        cache = FileCache.get_instance(self.temp_dir)
        md_files = cache.get_markdown_files()
        
        valid_extensions = {'.md', '.markdown'}
        invalid = [f for f in md_files if f.suffix.lower() not in valid_extensions]
        assert len(invalid) == 0, f"Non-markdown files found: {invalid}"
        assert len(md_files) == 1, f"Should find 1 .md file: {md_files}"
    
    def test_extension_normalization(self):
        """Verify extension is normalized (with/without dot)."""
        cache = FileCache.get_instance(self.temp_dir)
        
        files_with_dot = cache.get_files_by_extension('.py')
        files_without_dot = cache.get_files_by_extension('py')
        
        assert files_with_dot == files_without_dot, "Extension should be normalized"


class TestFileCacheLazyLoading:
    """Test Case 5: Lazy Loading Behavior
    
    Verify cache only scans when needed.
    Uses temporary directory for fast execution.
    """
    
    def setup_method(self):
        """Reset singleton and create temp directory."""
        FileCache.reset_instance()
        self.temp_dir = create_test_directory()
    
    def teardown_method(self):
        """Reset singleton and cleanup."""
        FileCache.reset_instance()
        if hasattr(self, 'temp_dir') and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_no_scan_on_instantiation(self):
        """Verify no scan occurs on instantiation."""
        cache = FileCache.get_instance(self.temp_dir)
        
        assert cache.get_scan_count() == 0, "No scan should occur on instantiation"
        assert not cache.is_cached(), "Cache should not be populated on instantiation"
    
    def test_scan_on_first_access(self):
        """Verify scan occurs on first access."""
        cache = FileCache.get_instance(self.temp_dir)
        
        _ = cache.get_all_files()
        
        assert cache.get_scan_count() == 1, "Scan should occur on first access"
        assert cache.is_cached(), "Cache should be populated after access"
    
    def test_no_scan_on_subsequent_access(self):
        """Verify no additional scan on subsequent access."""
        cache = FileCache.get_instance(self.temp_dir)
        
        _ = cache.get_all_files()
        _ = cache.get_all_files()
        _ = cache.get_python_files()
        
        assert cache.get_scan_count() == 1, "Only one scan should occur"


class TestFileCacheConvenienceFunctions:
    """Test convenience functions using temporary directory."""
    
    def setup_method(self):
        """Reset singleton and create temp directory."""
        FileCache.reset_instance()
        self.temp_dir = create_test_directory()
    
    def teardown_method(self):
        """Reset singleton and cleanup."""
        FileCache.reset_instance()
        if hasattr(self, 'temp_dir') and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_get_python_files_function(self):
        """Verify get_python_files convenience function."""
        files = get_python_files(self.temp_dir)
        
        assert len(files) == 3, f"Should find 3 Python files: {files}"
        assert all(f.suffix == '.py' for f in files), "All should be .py files"
    
    def test_invalidate_cache_function(self):
        """Verify invalidate_cache convenience function."""
        cache = FileCache.get_instance(self.temp_dir)
        _ = cache.get_all_files()
        
        assert cache.is_cached(), "Cache should be populated"
        
        invalidate_cache()
        
        assert not cache.is_cached(), "Cache should be invalidated"


class TestFileCacheProjectRootIntegration:
    """Integration test with actual PROJECT_ROOT.
    
    These tests verify the cache works with the real codebase.
    With os.walk pruning, these should be fast.
    """
    
    def setup_method(self):
        """Reset singleton."""
        FileCache.reset_instance()
    
    def teardown_method(self):
        """Reset singleton."""
        FileCache.reset_instance()
    
    def test_project_root_scan_completes(self):
        """Verify scanning PROJECT_ROOT completes quickly with os.walk pruning."""
        cache = FileCache.get_instance(PROJECT_ROOT)
        files = cache.get_python_files()
        
        # Should find many Python files in the actual project
        assert len(files) > 100, f"Should find >100 Python files, found {len(files)}"
    
    def test_project_root_excludes_git(self):
        """Verify .git is excluded from PROJECT_ROOT scan."""
        cache = FileCache.get_instance(PROJECT_ROOT)
        all_files = cache.get_all_files()
        
        git_files = [f for f in all_files if '.git' in f.parts]
        assert len(git_files) == 0, f".git files should be excluded: {git_files[:5]}"
    
    def test_project_root_excludes_pycache(self):
        """Verify __pycache__ is excluded from PROJECT_ROOT scan."""
        cache = FileCache.get_instance(PROJECT_ROOT)
        all_files = cache.get_all_files()
        
        pycache_files = [f for f in all_files if '__pycache__' in f.parts]
        assert len(pycache_files) == 0, f"__pycache__ should be excluded: {pycache_files[:5]}"


class TestCacheRefreshOnDemand:
    """Test Case: Cache Invalidation and Refresh
    
    Verify that cache invalidation correctly refreshes file list.
    """
    
    def setup_method(self):
        """Reset singleton and create temp directory."""
        FileCache.reset_instance()
        self.temp_dir = Path(tempfile.mkdtemp())
        (self.temp_dir / "initial.py").write_text("# initial")
    
    def teardown_method(self):
        """Cleanup temp directory and reset singleton."""
        FileCache.reset_instance()
        if hasattr(self, 'temp_dir') and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_cache_refresh_on_demand(self):
        """Verify cache refresh after invalidation includes new files."""
        cache = FileCache.get_instance(self.temp_dir)
        
        # Initial scan
        files_before = cache.get_python_files()
        assert len(files_before) == 1, "Should find 1 initial file"
        
        # Add new file
        new_file = self.temp_dir / "added.py"
        new_file.write_text("# added")
        
        # Invalidate cache
        cache.invalidate()
        
        # Refresh and verify new file is found
        files_after = cache.get_python_files()
        assert len(files_after) == 2, "Should find 2 files after refresh"
        assert new_file in files_after, "New file should be in refreshed cache"


class TestCIRglobLimitEnforcement:
    """Test Case: CI Enforcement of rglob Limit
    
    Verify that the codebase does not exceed the rglob call limit.
    """
    
    def test_ci_rglob_limit_enforcement(self):
        """Verify rglob call count does not exceed limit of 92."""
        from agentic_core.utils.scan_guard import audit_rglob_usage
        
        # Run audit
        report = audit_rglob_usage(PROJECT_ROOT)
        
        total_calls = report['total_rglob_calls']
        
        # Enforce limit: fail if count exceeds 92
        assert total_calls <= 92, (
            f"rglob call count ({total_calls}) exceeds limit of 92. "
            f"New rglob calls detected in production code. "
            f"Use FileCache instead. Top offenders: {report['top_offenders'][:5]}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
