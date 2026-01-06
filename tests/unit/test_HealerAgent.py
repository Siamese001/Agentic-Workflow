"""Unit tests for HealerAgent AST-based diff application."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import unittest
import tempfile
import shutil
from pathlib import Path

from agentic_core.L5_safety.guardrails.StructuralHealerAgent import StructuralHealerAgent


class TestHealerAgentASTDiff(unittest.TestCase):
    """Test AST-based diff application for structural healing."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.agent = HealerAgent(self.temp_dir, dry_run=False)

    def tearDown(self):
        """Clean up test directory."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_ast_fingerprint_structural_match(self):
        """Test that structurally identical code has same fingerprint."""
        code1 = "def func(x): return x + 1"
        code2 = "def func(y): return y + 1"  # Renamed var, same structure
        
        fp1 = self.agent._compute_ast_fingerprint(code1)
        fp2 = self.agent._compute_ast_fingerprint(code2)
        
        # Should have same fingerprint (structural match)
        self.assertEqual(fp1, fp2, "Structurally identical code should have same fingerprint")

    def test_ast_fingerprint_structural_difference(self):
        """Test that structurally different code has different fingerprint."""
        code1 = "def func(x): return x + 1"
        code3 = "def func(x): return x * 2"  # Different operation
        
        fp1 = self.agent._compute_ast_fingerprint(code1)
        fp3 = self.agent._compute_ast_fingerprint(code3)
        
        # Should have different fingerprints
        self.assertNotEqual(fp1, fp3, "Structurally different code should have different fingerprints")

    def test_ast_fingerprint_class_structure(self):
        """Test fingerprinting for class structures."""
        code1 = """
class MyClass:
    def method1(self):
        pass
    def method2(self):
        pass
"""
        code2 = """
class MyClass:
    def method1(self):
        pass
    def method2(self):
        pass
"""
        
        fp1 = self.agent._compute_ast_fingerprint(code1)
        fp2 = self.agent._compute_ast_fingerprint(code2)
        
        self.assertEqual(fp1, fp2)

    def test_structural_patch_replace_function(self):
        """Test replacing a function with structural patch."""
        original = '''
def old_func():
    print("old")

# Comment
class MyClass:
    pass
'''
        patch = '''def new_func():
    print("new")'''
        
        # Apply: Replace old_func with new_func, preserve rest
        updated = self.agent._apply_structural_patch(
            original, 
            patch, 
            mode='replace', 
            anchor='def old_func'
        )
        
        self.assertIn('def new_func', updated)
        self.assertNotIn('def old_func', updated)
        self.assertIn('class MyClass', updated)

    def test_partial_parse_with_syntax_error(self):
        """Test that tree-sitter handles partial/broken code."""
        bad_code = '''
def func(  # syntax error
    return 1
'''
        # Should not crash
        fp = self.agent._compute_ast_fingerprint(bad_code)
        self.assertIsInstance(fp, str)

    def test_integrity_validation_valid(self):
        """Test AST integrity validation for valid code."""
        valid_code = "def func(): pass"
        self.assertTrue(self.agent._validate_ast_integrity(valid_code))

    def test_integrity_validation_invalid(self):
        """Test AST integrity validation for invalid code."""
        invalid_code = "def func(:"  # Syntax error
        self.assertFalse(self.agent._validate_ast_integrity(invalid_code))

    def test_string_fallback_on_invalid_ast(self):
        """Test fallback to string-based patching when AST fails."""
        original = "def func(: pass"  # Invalid
        patch = "def new_func(): pass"
        
        # Should use string fallback
        result = self.agent._apply_structural_patch(
            original,
            patch,
            mode='replace',
            anchor='def func'
        )
        
        # Should return something (fallback behavior)
        self.assertIsInstance(result, str)

    def test_find_block_end(self):
        """Test finding the end of a code block."""
        lines = [
            "def func():",
            "    line1",
            "    line2",
            "def next_func():",
            "    pass"
        ]
        
        end = self.agent._find_block_end(lines, 0)
        self.assertEqual(end, 3)  # Should stop at next_func

    def test_normalize_ast_tree_constants(self):
        """Test AST normalization handles constants correctly."""
        code1 = "x = 42"
        code2 = "x = 100"
        
        fp1 = self.agent._compute_ast_fingerprint(code1)
        fp2 = self.agent._compute_ast_fingerprint(code2)
        
        # Should be same (both are constant assignments)
        self.assertEqual(fp1, fp2)

    def test_normalize_ast_tree_variables(self):
        """Test AST normalization normalizes variable names."""
        code1 = "result = calculate(x, y)"
        code2 = "output = calculate(a, b)"
        
        fp1 = self.agent._compute_ast_fingerprint(code1)
        fp2 = self.agent._compute_ast_fingerprint(code2)
        
        # Should be same (same structure, different names)
        self.assertEqual(fp1, fp2)

    def test_structural_patch_preserves_comments(self):
        """Test that structural patching preserves comments."""
        original = '''
# Important comment
def old_func():
    pass

# Another comment
class MyClass:
    pass
'''
        patch = '''def new_func():
    pass'''
        
        updated = self.agent._apply_structural_patch(
            original,
            patch,
            mode='replace',
            anchor='def old_func'
        )
        
        # Comments should be preserved (not in replaced block)
        self.assertIn('# Another comment', updated)


class TestHealerAgentIntegration(unittest.TestCase):
    """Integration tests for AST-based healing."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.agent = HealerAgent(self.temp_dir, dry_run=False)

    def tearDown(self):
        """Clean up."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_heal_with_ast_validation(self):
        """Test that healing validates AST integrity."""
        # Create test file
        test_file = self.temp_dir / "test.py"
        test_file.write_text("""
def original_function():
    return "original"

class TestClass:
    pass
""")
        
        # Read and validate
        content = test_file.read_text()
        self.assertTrue(self.agent._validate_ast_integrity(content))

    def test_fingerprint_caching(self):
        """Test that fingerprinting is consistent."""
        code = """
class Calculator:
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
"""
        
        # Compute multiple times
        fp1 = self.agent._compute_ast_fingerprint(code)
        fp2 = self.agent._compute_ast_fingerprint(code)
        
        self.assertEqual(fp1, fp2)
        self.assertTrue(len(fp1) > 0)


class TestHealerAgentPerformance(unittest.TestCase):
    """Performance tests for AST operations."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.agent = HealerAgent(self.temp_dir, dry_run=False)

    def tearDown(self):
        """Clean up."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_fingerprint_performance(self):
        """Test that fingerprinting is reasonably fast."""
        # Generate moderately large code
        code = '\n'.join([
            f"def func_{i}(x):\n    return x + {i}"
            for i in range(100)
        ])
        
        import time
        start = time.time()
        fp = self.agent._compute_ast_fingerprint(code)
        duration = time.time() - start
        
        # Should complete quickly (< 100ms)
        self.assertLess(duration, 0.1)
        self.assertTrue(len(fp) > 0)


def heal_repository(dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path = None):
    """Test file - operational stub only."""
    if _call_path is None:
        _call_path = set()
    agent_name = "TestHealer"
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
    unittest.main()
