#!/usr/bin/env python3
"""
Test Suite for CodeDeduplicationAgent - Non-Python File Support

Tests that the deduplication agent can detect and handle duplicates in:
- JSON files
- YAML files
- Markdown files
- Text files
- Configuration files

MANDATORY: 100% pass rate required
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestNonPythonFileDeduplication(unittest.TestCase):
    """Test non-Python file deduplication capabilities."""
    
    def setUp(self):
        """Create temporary directory with test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_json_file_duplicate_detection(self):
        """Test detection of duplicate JSON files."""
        # Create two identical JSON files
        json_content = '{"name": "test", "value": 123}'
        
        file1 = self.temp_path / "config1.json"
        file2 = self.temp_path / "config2.json"
        
        file1.write_text(json_content)
        file2.write_text(json_content)
        
        from agentic_core.L5_safety.validators.CodeDeduplicationAgent import CodeDeduplicationAgent
        
        agent = CodeDeduplicationAgent()
        
        # Should detect these as duplicates
        hash1 = agent._hash_entire_file(file1)
        hash2 = agent._hash_entire_file(file2)
        
        self.assertEqual(hash1, hash2, "Identical JSON files should have same hash")
    
    def test_yaml_file_duplicate_detection(self):
        """Test detection of duplicate YAML files."""
        yaml_content = """
name: test
value: 123
nested:
  key: value
"""
        
        file1 = self.temp_path / "config1.yaml"
        file2 = self.temp_path / "config2.yml"
        
        file1.write_text(yaml_content)
        file2.write_text(yaml_content)
        
        from agentic_core.L5_safety.validators.CodeDeduplicationAgent import CodeDeduplicationAgent
        
        agent = CodeDeduplicationAgent()
        
        hash1 = agent._hash_entire_file(file1)
        hash2 = agent._hash_entire_file(file2)
        
        self.assertEqual(hash1, hash2, "Identical YAML files should have same hash")
    
    def test_markdown_file_duplicate_detection(self):
        """Test detection of duplicate Markdown files."""
        md_content = """
# Test Document

This is a test document with some content.

## Section 1

Content here.
"""
        
        file1 = self.temp_path / "doc1.md"
        file2 = self.temp_path / "doc2.md"
        
        file1.write_text(md_content)
        file2.write_text(md_content)
        
        from agentic_core.L5_safety.validators.CodeDeduplicationAgent import CodeDeduplicationAgent
        
        agent = CodeDeduplicationAgent()
        
        hash1 = agent._hash_entire_file(file1)
        hash2 = agent._hash_entire_file(file2)
        
        self.assertEqual(hash1, hash2, "Identical Markdown files should have same hash")
    
    def test_text_file_duplicate_detection(self):
        """Test detection of duplicate text files."""
        text_content = "This is a test file\nWith multiple lines\nOf text content"
        
        file1 = self.temp_path / "notes1.txt"
        file2 = self.temp_path / "notes2.txt"
        
        file1.write_text(text_content)
        file2.write_text(text_content)
        
        from agentic_core.L5_safety.validators.CodeDeduplicationAgent import CodeDeduplicationAgent
        
        agent = CodeDeduplicationAgent()
        
        hash1 = agent._hash_entire_file(file1)
        hash2 = agent._hash_entire_file(file2)
        
        self.assertEqual(hash1, hash2, "Identical text files should have same hash")
    
    def test_mixed_file_types_scan(self):
        """Test scanning directory with mixed file types."""
        # Create various duplicate files
        files_to_create = {
            "config.json": '{"test": true}',
            "config_copy.json": '{"test": true}',
            "readme.md": "# Test\nContent",
            "readme_backup.md": "# Test\nContent",
            "data.txt": "Sample data",
            "data_old.txt": "Sample data",
        }
        
        for filename, content in files_to_create.items():
            (self.temp_path / filename).write_text(content)
        
        from agentic_core.L5_safety.validators.CodeDeduplicationAgent import CodeDeduplicationAgent
        
        agent = CodeDeduplicationAgent()
        
        # Get all files
        all_files = list(self.temp_path.glob("*"))
        
        # Scan for duplicates
        agent.scan_file_level_duplicates(all_files)
        
        # Should detect 3 duplicate groups
        self.assertEqual(len(agent.file_duplicate_groups), 3, 
                        "Should detect 3 groups of duplicate files")
    
    def test_whitespace_normalization(self):
        """Test that whitespace differences don't affect duplicate detection."""
        content1 = "Line 1\nLine 2\nLine 3"
        content2 = "Line 1\n\nLine 2\n\n\nLine 3"  # Extra blank lines
        
        file1 = self.temp_path / "file1.txt"
        file2 = self.temp_path / "file2.txt"
        
        file1.write_text(content1)
        file2.write_text(content2)
        
        from agentic_core.L5_safety.validators.CodeDeduplicationAgent import CodeDeduplicationAgent
        
        agent = CodeDeduplicationAgent()
        
        # Normalized hashes should be equal
        hash1 = agent._hash_entire_file(file1)
        hash2 = agent._hash_entire_file(file2)
        
        # After normalization (removing blank lines), should match
        self.assertEqual(hash1, hash2, 
                        "Files with different whitespace should normalize to same hash")
    
    def test_filename_duplicate_detection_non_python(self):
        """Test filename duplicate detection for non-Python files."""
        # Create files with same name in different directories
        dir1 = self.temp_path / "dir1"
        dir2 = self.temp_path / "dir2"
        dir1.mkdir()
        dir2.mkdir()
        
        content = "Shared content"
        (dir1 / "config.json").write_text(content)
        (dir2 / "config.json").write_text(content)
        
        from agentic_core.L5_safety.validators.CodeDeduplicationAgent import CodeDeduplicationAgent
        
        agent = CodeDeduplicationAgent()
        
        all_files = list(self.temp_path.rglob("*.json"))
        
        agent.scan_filename_duplicates(all_files, self.temp_path)
        
        # Should detect filename duplicate
        self.assertIn("config.json", agent.filename_duplicates,
                     "Should detect duplicate filename across directories")


class TestNonPythonFileExtensions(unittest.TestCase):
    """Test that agent properly handles various file extensions."""
    
    def test_supported_extensions(self):
        """Verify agent can process common non-Python extensions."""
        from agentic_core.L5_safety.validators.CodeDeduplicationAgent import CodeDeduplicationAgent
        
        agent = CodeDeduplicationAgent()
        
        # These should all be processable
        test_extensions = [
            ".json", ".yaml", ".yml", ".md", ".txt", 
            ".toml", ".ini", ".cfg", ".conf"
        ]
        
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir)
        
        try:
            for ext in test_extensions:
                test_file = temp_path / f"test{ext}"
                test_file.write_text("test content")
                
                # Should not raise exception
                file_hash = agent._hash_entire_file(test_file)
                self.assertIsNotNone(file_hash, 
                                    f"Should be able to hash {ext} files")
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    print("=" * 70)
    print("CODE DEDUPLICATION AGENT - NON-PYTHON FILE TESTS")
    print("=" * 70)
    print()
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestNonPythonFileDeduplication))
    suite.addTests(loader.loadTestsFromTestCase(TestNonPythonFileExtensions))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 70)
    passed = result.testsRun - len(result.failures) - len(result.errors)
    total = result.testsRun
    
    if result.wasSuccessful():
        print(f"ALL {total} TESTS PASSED - Non-Python file support verified")
    else:
        print(f"{passed}/{total} TESTS PASSED - Issues found")
    print("=" * 70)
    
    sys.exit(0 if result.wasSuccessful() else 1)
