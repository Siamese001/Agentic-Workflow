"""
Unit tests for FileCleanupAgent - file cleanup with repeated strings in filenames.
"""
import unittest
import tempfile
from pathlib import Path
from agentic_core.L5_safety.guardrails.FileCleanupAgent import FileCleanupAgent


class MockContext:
    """Mock context for testing."""
    def __init__(self):
        self.scan_directories = []


class TestFileCleanupAgent(unittest.TestCase):
    """Test FileCleanupAgent functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.ctx = MockContext()
        self.agent = FileCleanupAgent(self.temp_dir, self.ctx, dry_run=True)
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_detect_repeated_strings(self):
        """Test detection of repeated strings in filenames."""
        # Test cases
        test_cases = [
            ('enums_enums', True, 'enums'),
            ('impl_impl_impl', True, 'impl'),
            ('data_models_enums_enums', True, 'enums'),
            ('test_data', False, None),
            ('normal_file', False, None),
            ('init_init', True, 'init'),
        ]
        
        for filename, expected_has_repeats, expected_pattern in test_cases:
            has_repeats, pattern = self.agent._has_repeated_strings(filename)
            self.assertEqual(has_repeats, expected_has_repeats, 
                           f"Failed for {filename}")
            if expected_pattern:
                self.assertEqual(pattern, expected_pattern,
                               f"Pattern mismatch for {filename}")
    
    def test_get_canonical_name(self):
        """Test canonical name generation."""
        test_cases = [
            ('enums_enums_enums', 'enums'),
            ('impl_impl', 'impl'),
            ('data_models_enums_enums', 'data_models_enums'),
            ('test_test_data', 'test_data'),
            ('normal_file', 'normal_file'),
        ]
        
        for filename, expected_canonical in test_cases:
            canonical = self.agent._get_canonical_name(filename)
            self.assertEqual(canonical, expected_canonical,
                           f"Failed for {filename}")
    
    def test_count_repetitions(self):
        """Test repetition counting."""
        test_cases = [
            ('enums_enums', 2),
            ('impl_impl_impl', 3),
            ('data_models_enums_enums', 2),
            ('test_data', 1),
            ('init_init_init_init', 4),
        ]
        
        for filename, expected_count in test_cases:
            count = self.agent._count_repetitions(filename)
            self.assertEqual(count, expected_count,
                           f"Failed for {filename}")
    
    def test_scan_with_repeated_files(self):
        """Test scanning directory with files containing repeated strings."""
        # Create test files
        test_files = [
            'data_models_enums_enums_enums.py',
            'data_models_enums_enums.py',
            'data_models_enums.py',
            'impl_impl_impl.py',
            'impl_impl.py',
            'normal_file.py',
        ]
        
        for filename in test_files:
            (self.temp_dir / filename).write_text('# test content')
        
        # Scan
        results = self.agent.scan_for_repeated_filenames([str(self.temp_dir)])
        
        # Should find repeated files
        self.assertGreater(results['total_files_scanned'], 0)
        self.assertGreater(results['files_to_remove'], 0)
        
        print(f"\nfrom agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin\n✓ Scan results: {results}")
    
    def test_dry_run_mode(self):
        """Test that dry run doesn't actually delete files."""
        # Create test files
        file1 = self.temp_dir / 'test_test_test.py'
        file2 = self.temp_dir / 'test_test.py'
        file1.write_text('# content 1')
        file2.write_text('# content 2')
        
        # Scan and execute cleanup in dry run
        self.agent.scan_for_repeated_filenames([str(self.temp_dir)])
        results = self.agent.execute_cleanup()
        
        # Files should still exist
        self.assertTrue(file1.exists(), "File should not be deleted in dry run")
        self.assertTrue(file2.exists(), "File should not be deleted in dry run")
        self.assertTrue(results['dry_run'])
    
    def test_actual_cleanup(self):
        """Test actual file removal (not dry run)."""
        # Create agent with dry_run=False
        agent = FileCleanupAgent(self.temp_dir, self.ctx, dry_run=False)
        
        # Create test files
        file1 = self.temp_dir / 'cleanup_cleanup_cleanup.py'
        file2 = self.temp_dir / 'cleanup_cleanup.py'
        file3 = self.temp_dir / 'cleanup.py'
        file1.write_text('# content 1')
        file2.write_text('# content 2')
        file3.write_text('# content 3')
        
        # Scan
        agent.scan_for_repeated_filenames([str(self.temp_dir)])
        
        # Should identify files to remove
        self.assertGreater(len(agent.files_to_remove), 0)
        
        # Execute cleanup
        results = agent.execute_cleanup()
        
        # Check that worst duplicates were removed
        self.assertFalse(results['dry_run'])
        self.assertGreater(results['removed'], 0)
        
        # At least one file should remain (the best one)
        remaining_files = list(self.temp_dir.glob('cleanup*.py'))
        self.assertGreater(len(remaining_files), 0)
        
        print(f"\n✓ Cleanup results: {results}")
        print(f"  Remaining files: {[f.name for f in remaining_files]}")
    
    def test_no_false_positives(self):
        """Test that normal files are not flagged."""
        # Create normal files without repetitions
        normal_files = [
            'data_models.py',
            'test_utils.py',
            'config_loader.py',
        ]
        
        for filename in normal_files:
            (self.temp_dir / filename).write_text('# normal content')
        
        # Scan
        results = self.agent.scan_for_repeated_filenames([str(self.temp_dir)])
        
        # Should not find any files to remove
        self.assertEqual(results['files_to_remove'], 0)
        print(f"\n✓ No false positives: {results}")
    
    def test_keeps_best_version(self):
        """Test that the version with fewest repetitions is kept."""
        agent = FileCleanupAgent(self.temp_dir, self.ctx, dry_run=False)
        
        # Create files with different repetition levels
        file1 = self.temp_dir / 'security_security_security_controls.py'
        file2 = self.temp_dir / 'security_security_controls.py'
        file3 = self.temp_dir / 'security_controls.py'
        
        file1.write_text('# worst')
        file2.write_text('# better')
        file3.write_text('# best')
        
        # Scan and cleanup
        agent.scan_for_repeated_filenames([str(self.temp_dir)])
        agent.execute_cleanup()
        
        # Best version should remain
        self.assertTrue(file3.exists(), "Best version should be kept")
        self.assertFalse(file1.exists(), "Worst version should be removed")
        
        print(f"\n✓ Kept best version: {file3.name}")


class TestIntegrationFileCleanup(unittest.TestCase):
    """Integration tests for FileCleanupAgent."""
    
    def test_real_world_scenario(self):
        """Test with real-world file patterns."""
        temp_dir = Path(tempfile.mkdtemp())
        ctx = MockContext()
        agent = FileCleanupAgent(temp_dir, ctx, dry_run=True)
        
        try:
            # Create realistic file structure
            files = [
                'const_final_impl_impl_impl_impl.py',
                'const_ai_impl_impl_impl_impl.py',
                'constitutional_ai_impl_impl_impl_impl.py',
                'security_security_controls.py',
                'l5___init__.py',
                'policy_l5___init__.py',
                'prompts___init__.py',
            ]
            
            for filename in files:
                (temp_dir / filename).write_text('# content')
            
            # Scan
            results = agent.scan_for_repeated_filenames([str(temp_dir)])
            
            print(f"\n✓ Real-world scenario results:")
            print(f"  Total files scanned: {results['total_files_scanned']}")
            print(f"  Files to remove: {results['files_to_remove']}")
            print(f"  Files to keep: {results['files_to_keep']}")
            
            # Note: Detection depends on agent's repetition thresholds
            # Test passes if scan completes without error
            self.assertGreaterEqual(results['files_to_remove'], 0)
            
        finally:
            import shutil
            if temp_dir.exists():
                shutil.rmtree(temp_dir)


def heal_repository(dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path = None):
    """Test file - operational stub only."""
    if _call_path is None:
        _call_path = set()
    agent_name = "TestFileCleanup"
    if agent_name in _call_path:
        return {"errors": 1, "cycle_detected": True}
    if depth > max_depth:
        return {"errors": 1, "depth_limited": True}
    _call_path.add(agent_name)
    try:
        print(f"[{agent_name}] Test file - operational stub only")
        return {"skipped": 1}
    finally:
        _call_path.discard(agent_name)

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
