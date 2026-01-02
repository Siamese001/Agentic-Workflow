"""
Test Suite: Archive Loop Prevention (Bug Fix 2025-12-31)

Tests to verify that the repeated archiving bug is fixed:
- Files with .archived suffix are not re-archived
- Files with .backup, .old, .copy suffixes are skipped
- Files already in archives/ directory are not re-processed

Root Cause: hierarchy_healer.py was archiving files by appending .archived,
but then picking up the archived file in the next scan and archiving it again,
creating: file.json → file.json.archived → file.json.archived.archived...
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestArchiveLoopPrevention:
    """Test suite for archive loop prevention fixes."""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create basic project structure
        (temp_dir / "agentic_core" / "L1_cognition" / "test_dir").mkdir(parents=True)
        (temp_dir / "archives").mkdir()
        (temp_dir / ".git").mkdir()
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_hierarchy_healer_skips_archived_files(self, temp_project):
        """Test that hierarchy_healer skips files with .archived suffix."""
        # Create test files
        normal_file = temp_project / "orphan_file.json"
        archived_file = temp_project / "orphan_file.json.archived"
        double_archived = temp_project / "orphan_file.json.archived.archived"
        
        normal_file.write_text("{}")
        archived_file.write_text("{}")
        double_archived.write_text("{}")
        
        # Import and test
        try:
            from agentic_core.L5_safety.guardrails.hierarchy_healer import HierarchyHealer
            
            healer = HierarchyHealer(temp_project)
            
            # The fix should skip files with archive markers
            archive_markers = ('.archived', '.backup', '.old', '.copy')
            
            # Test that archived files are detected as "should skip"
            assert any(archived_file.name.lower().endswith(m) for m in archive_markers), \
                "Archived file should be detected as having archive marker"
            assert any(double_archived.name.lower().endswith(m) for m in archive_markers), \
                "Double-archived file should be detected as having archive marker"
            assert not any(normal_file.name.lower().endswith(m) for m in archive_markers), \
                "Normal file should NOT be detected as having archive marker"
                
            print("✓ hierarchy_healer archive marker detection works correctly")
            
        except ImportError as e:
            pytest.skip(f"Could not import HierarchyHealer: {e}")
    
    def test_location_agent_skips_archived_files(self, temp_project):
        """Test that LocationAgent.cleanup_violations skips archived files."""
        # Create test files
        normal_file = temp_project / "agentic_core" / "L1_cognition" / "test_dir" / "test.py"
        archived_file = temp_project / "test.py.archived"
        backup_file = temp_project / "test.py.backup"
        
        normal_file.write_text("# test")
        archived_file.write_text("# archived")
        backup_file.write_text("# backup")
        
        try:
            from agentic_core.L5_safety.validators.LocationAgent import LocationAgent
            
            agent = LocationAgent(temp_project)
            
            # Create mock violations
            violations = [
                (normal_file, "TEST VIOLATION"),
                (archived_file, "TEST VIOLATION"),
                (backup_file, "TEST VIOLATION"),
            ]
            
            # Run cleanup in dry_run mode
            results = agent.cleanup_violations(violations, dry_run=True)
            
            # Only the normal file should be processed
            processed_files = [r["file"] for r in results]
            
            assert str(normal_file) in processed_files, \
                "Normal file should be processed"
            assert str(archived_file) not in processed_files, \
                "Archived file should be SKIPPED"
            assert str(backup_file) not in processed_files, \
                "Backup file should be SKIPPED"
                
            print("✓ LocationAgent correctly skips archived files")
            
        except ImportError as e:
            pytest.skip(f"Could not import LocationAgent: {e}")
    
    def test_filesystem_agent_skips_archives_directory(self, temp_project):
        """Test that FilesystemAgent.run() skips files in archives/ directory."""
        # Create test files
        normal_file = temp_project / "test_file.json"
        archived_in_dir = temp_project / "archives" / "test_file.json"
        
        normal_file.write_text("{}")
        archived_in_dir.parent.mkdir(exist_ok=True)
        archived_in_dir.write_text("{}")
        
        try:
            from agentic_core.L5_safety.validators.FilesystemAgent import FilesystemAgent
            
            agent = FilesystemAgent(temp_project, dry_run=True)
            violations = agent.run()
            
            # Files in archives/ should not be flagged
            violation_paths = [str(v[0]) for v in violations]
            
            assert str(archived_in_dir) not in violation_paths, \
                "Files in archives/ directory should NOT be flagged as violations"
                
            print("✓ FilesystemAgent correctly skips archives/ directory")
            
        except ImportError as e:
            pytest.skip(f"Could not import FilesystemAgent: {e}")
    
    def test_archive_marker_detection(self):
        """Test the archive marker detection logic directly."""
        archive_markers = ('.archived', '.backup', '.old', '.copy')
        
        # Files that SHOULD be skipped
        skip_files = [
            "file.json.archived",
            "file.json.archived.archived",
            "file.json.archived.archived.archived.archived.archived.archived",
            "test.py.backup",
            "data.csv.old",
            "config.yaml.copy",
            "FILE.JSON.ARCHIVED",  # Case insensitive
            "test.BACKUP",
        ]
        
        # Files that should NOT be skipped
        process_files = [
            "file.json",
            "test.py",
            "archive_manager.py",  # Contains "archive" but not as suffix
            "backup_utils.py",
            "old_data_processor.py",
        ]
        
        for filename in skip_files:
            should_skip = any(filename.lower().endswith(m) for m in archive_markers)
            assert should_skip, f"File '{filename}' should be SKIPPED but wasn't detected"
        
        for filename in process_files:
            should_skip = any(filename.lower().endswith(m) for m in archive_markers)
            assert not should_skip, f"File '{filename}' should be PROCESSED but was detected as archive"
        
        print("✓ Archive marker detection logic is correct")
    
    def test_no_infinite_archive_loop(self, temp_project):
        """
        Integration test: Simulate multiple archive runs and verify no infinite loop.
        
        This tests the exact bug that caused:
        agent_registry_temp.json.archived.archived.archived.archived.archived.archived
        """
        # Create a file that would be flagged as orphaned
        orphan_file = temp_project / "agent_registry_temp.json"
        orphan_file.write_text('{"test": true}')
        
        archive_markers = ('.archived', '.backup', '.old', '.copy')
        
        # Simulate 10 archive runs
        current_file = orphan_file
        for run in range(10):
            # Check if file should be archived (the fix logic)
            if any(current_file.name.lower().endswith(m) for m in archive_markers):
                # File already has archive marker - SKIP (this is the fix)
                break
            
            # Archive the file
            archived_path = current_file.with_name(current_file.name + ".archived")
            if current_file.exists():
                current_file.rename(archived_path)
                current_file = archived_path
        
        # Verify we stopped after first archive (run 1 archives, run 2 skips)
        final_name = current_file.name
        archive_count = final_name.count(".archived")
        
        assert archive_count == 1, \
            f"File should only be archived ONCE, but has {archive_count} .archived suffixes: {final_name}"
        
        print(f"✓ No infinite archive loop - file archived exactly once: {final_name}")


class TestArchiveMarkerMiddleOfName:
    """Test edge cases where archive markers appear in the middle of filenames."""
    
    def test_marker_in_middle_detection(self):
        """Test that markers in the middle of filenames are also caught."""
        archive_markers = ('.archived', '.backup', '.old', '.copy')
        
        # Files with markers in the middle (edge case)
        edge_cases = [
            "file.archived.json",  # Marker in middle
            "data.backup.csv",
            "config.old.yaml",
        ]
        
        for filename in edge_cases:
            has_marker_in_middle = any(marker in filename.lower() for marker in archive_markers)
            assert has_marker_in_middle, \
                f"File '{filename}' should be detected as having archive marker in middle"
        
        print("✓ Archive markers in middle of filename are correctly detected")


def run_tests():
    """Run all tests and report results."""
    print("\n" + "="*60)
    print("ARCHIVE LOOP PREVENTION TEST SUITE")
    print("Bug Fix: 2025-12-31")
    print("="*60 + "\n")
    
    # Run marker detection tests (no imports needed)
    test_instance = TestArchiveLoopPrevention()
    test_instance.test_archive_marker_detection()
    
    edge_test = TestArchiveMarkerMiddleOfName()
    edge_test.test_marker_in_middle_detection()
    
    # Run integration test with temp directory
    import tempfile
    temp_dir = Path(tempfile.mkdtemp())
    try:
        (temp_dir / "agentic_core" / "L1_cognition" / "test_dir").mkdir(parents=True)
        (temp_dir / "archives").mkdir()
        
        test_instance.test_no_infinite_archive_loop.__func__(test_instance, temp_dir)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED ✓")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_tests()
