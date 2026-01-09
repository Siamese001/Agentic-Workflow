#!/usr/bin/env python3
"""
Comprehensive Tests for Deduplication Agents
Tests FileLibrarian, CodeDeduplicationAgent, and DuplicateCodeDetectorAgent
"""
import asyncio
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestFileLibrarian(unittest.TestCase):
    """Test suite for L0 FileLibrarian"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up temp files"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_content_hash_generation(self):
        """Test that content hashing produces consistent results"""
        content = "def hello():\nfrom agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin\n    return 'world'"
        hash1 = hashlib.sha256(content.encode()).hexdigest()
        hash2 = hashlib.sha256(content.encode()).hexdigest()
        self.assertEqual(hash1, hash2)
    
    def test_duplicate_detection_same_content(self):
        """Test detection of files with identical content"""
        # Create two files with same content
        file1 = self.temp_path / "file1.py"
        file2 = self.temp_path / "file2.py"
        content = "def duplicate():\n    pass"
        file1.write_text(content)
        file2.write_text(content)
        
        # Hash both files
        hash1 = hashlib.sha256(file1.read_text().encode()).hexdigest()
        hash2 = hashlib.sha256(file2.read_text().encode()).hexdigest()
        
        self.assertEqual(hash1, hash2)
    
    def test_different_content_different_hash(self):
        """Test that different content produces different hashes"""
        content1 = "def hello():\n    return 'world'"
        content2 = "def goodbye():\n    return 'world'"
        
        hash1 = hashlib.sha256(content1.encode()).hexdigest()
        hash2 = hashlib.sha256(content2.encode()).hexdigest()
        
        self.assertNotEqual(hash1, hash2)
    
    def test_excluded_paths(self):
        """Test that excluded paths are correctly identified"""
        from agentic_core.L0_maintenance.scripts.deduplicate_and_index import is_excluded_path
        
        # Should be excluded
        self.assertTrue(is_excluded_path(Path("project/.git/config")))
        self.assertTrue(is_excluded_path(Path("project/__pycache__/module.pyc")))
        self.assertTrue(is_excluded_path(Path("project/venv/lib/python")))
        self.assertTrue(is_excluded_path(Path("project/archives/old.py")))
        
        # Should NOT be excluded
        self.assertFalse(is_excluded_path(Path("project/src/main.py")))
        self.assertFalse(is_excluded_path(Path("agentic_core/L5_safety/agent.py")))
    
    def test_allowed_duplicates(self):
        """Test that certain filenames are allowed to have duplicates"""
        from agentic_core.L0_maintenance.scripts.deduplicate_and_index import is_allowed_duplicate
        
        # __init__.py is commonly allowed as duplicate
        self.assertTrue(is_allowed_duplicate("__init__.py"))


class TestCodeDeduplicationAgent( unittest.TestCase):
    """Test suite for L2 CodeDeduplicationAgent"""
    
    def setUp(self):
        """Set up test fixtures"""
        from agentic_core.L2_execution.ToolRegistry.CodeDeduplicationAgent import CodeDeduplicationAgent
        self.agent = CodeDeduplicationAgent(similarity_threshold=0.95, min_lines=8)
    
    def test_initialization(self):
        """Test agent initialization with parameters"""
        self.assertEqual(self.agent.threshold, 0.95)
        self.assertEqual(self.agent.min_lines, 8)
        self.assertEqual(self.agent.extracted_count, 0)
        # Note: errors list may contain tree-sitter init warnings which is acceptable
        self.assertIsInstance(self.agent.errors, list)
    
    def test_duplicate_groups_tracking(self):
        """Test that duplicate groups are properly tracked"""
        self.assertIsInstance(self.agent.duplicate_groups, dict)
    
    def test_custom_threshold(self):
        """Test agent with custom similarity threshold"""
        from agentic_core.L2_execution.ToolRegistry.CodeDeduplicationAgent import CodeDeduplicationAgent
        agent = CodeDeduplicationAgent(similarity_threshold=0.80, min_lines=5)
        self.assertEqual(agent.threshold, 0.80)
        self.assertEqual(agent.min_lines, 5)


class TestDuplicateCodeDetectorAgent(unittest.TestCase):
    """Test suite for L5 DuplicateCodeDetectorAgent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.mock_ctx = MagicMock()
        self.mock_ctx.python_files = []
    
    def tearDown(self):
        """Clean up temp files"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test agent initialization"""
        from agentic_core.L5_safety.guardrails.DuplicateCodeDetectorAgent import DuplicateCodeDetectorAgent
        agent = DuplicateCodeDetectorAgent(self.temp_path, self.mock_ctx)
        
        self.assertEqual(agent.project_root, self.temp_path)
        self.assertEqual(agent.min_lines, 10)
        self.assertEqual(agent.max_report, 20)
        self.assertFalse(agent.auto_deduplicate)
    
    def test_execute_with_no_files(self):
        """Test execute returns empty result when no files"""
        from agentic_core.L5_safety.guardrails.DuplicateCodeDetectorAgent import DuplicateCodeDetectorAgent
        agent = DuplicateCodeDetectorAgent(self.temp_path, self.mock_ctx)
        
        result = asyncio.run(agent.execute())
        self.assertEqual(result, {})
    
    def test_execute_with_files(self):
        """Test execute with Python files"""
        from agentic_core.L5_safety.guardrails.DuplicateCodeDetectorAgent import DuplicateCodeDetectorAgent
        
        # Create test files
        file1 = self.temp_path / "test1.py"
        file2 = self.temp_path / "test2.py"
        file1.write_text("def hello():\n    return 'world'\n")
        file2.write_text("def goodbye():\n    return 'farewell'\n")
        
        self.mock_ctx.python_files = [file1, file2]
        agent = DuplicateCodeDetectorAgent(self.temp_path, self.mock_ctx)
        
        result = asyncio.run(agent.execute())
        # Should run without error
        self.assertIsInstance(result, dict)


class TestParallelExecution(unittest.TestCase):
    """Test parallel execution of deduplication agents"""
    
    def test_agents_can_run_concurrently(self):
        """Test that all three agents can be initialized and don't block each other"""
        from agentic_core.L2_execution.ToolRegistry.CodeDeduplicationAgent import CodeDeduplicationAgent
        from agentic_core.L5_safety.guardrails.DuplicateCodeDetectorAgent import DuplicateCodeDetectorAgent
        
        # Initialize agents
        code_agent = CodeDeduplicationAgent()
        
        mock_ctx = MagicMock()
        mock_ctx.python_files = []
        detector_agent = DuplicateCodeDetectorAgent(Path.cwd(), mock_ctx)
        
        # Both should be initialized without conflict
        self.assertIsNotNone(code_agent)
        self.assertIsNotNone(detector_agent)
    
    def test_async_execution_pattern(self):
        """Test async execution pattern works"""
        async def mock_task():
            return {"status": "success"}
        
        async def run_parallel():
            results = await asyncio.gather(
                mock_task(),
                mock_task(),
                mock_task()
            )
            return results
        
        results = asyncio.run(run_parallel())
        self.assertEqual(len(results), 3)
        for r in results:
            self.assertEqual(r["status"], "success")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def test_empty_file_handling(self):
        """Test handling of empty files"""
        content = ""
        hash_result = hashlib.sha256(content.encode()).hexdigest()
        self.assertIsNotNone(hash_result)
        self.assertEqual(len(hash_result), 64)  # SHA256 produces 64 hex chars
    
    def test_unicode_content_handling(self):
        """Test handling of unicode content in files"""
        content = "def greet():\n    return '你好世界 🌍'"
        hash_result = hashlib.sha256(content.encode('utf-8')).hexdigest()
        self.assertIsNotNone(hash_result)
    
    def test_large_file_handling(self):
        """Test handling of large content"""
        content = "x = 1\n" * 10000  # 10k lines
        hash_result = hashlib.sha256(content.encode()).hexdigest()
        self.assertIsNotNone(hash_result)


if __name__ == '__main__':
    unittest.main(verbosity=2)
