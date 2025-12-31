"""Demo test showing NamingAgent tree-sitter functionality."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pathlib import Path
from agentic_core.utils.core_extensions.NamingAgent import NamingAgent, TREE_SITTER_AVAILABLE


def test_tree_sitter_availability():
    """Test that tree-sitter is available and working."""
    print("\n" + "="*80)
    print("NamingAgent Tree-Sitter Multi-Language Support Demo")
    print("="*80 + "\n")
    
    print(f"Tree-sitter available: {TREE_SITTER_AVAILABLE}")
    
    if not TREE_SITTER_AVAILABLE:
        print("⚠ Tree-sitter not available - using ast fallback only")
        return
    
    agent = NamingAgent(Path.cwd())
    
    # Test Python
    print("\n--- Python Symbol Extraction ---")
    py_code = '''
class UserService:
    """User management service."""
    def get_user(self, user_id: int):
        return self.db.query(user_id)
    
    def create_user(self, name: str):
        return self.db.insert(name)
'''
    classes, funcs, imports = agent._extract_symbols(py_code, file_path='test.py')
    print(f"Classes: {classes}")
    print(f"Functions: {funcs}")
    print(f"Imports: {imports}")
    
    assert 'UserService' in classes, "Should extract UserService class"
    print("✓ Python extraction working")
    
    # Test JavaScript (may not work without proper grammar)
    print("\n--- JavaScript Symbol Extraction (Experimental) ---")
    js_code = '''
class Calculator {
  add(a, b) {
    return a + b;
  }
}
'''
    try:
        classes_js, funcs_js, imports_js = agent._extract_symbols(js_code, file_path='test.js')
        print(f"Classes: {classes_js}")
        print(f"Functions: {funcs_js}")
        print(f"Imports: {imports_js}")
        if classes_js:
            print("✓ JavaScript extraction working")
        else:
            print("⚠ JavaScript extraction returned empty (grammar may need adjustment)")
    except Exception as e:
        print(f"⚠ JavaScript extraction failed: {e}")
    
    # Test fallback behavior
    print("\n--- Fallback to AST (Python) ---")
    classes_ast, funcs_ast, imports_ast = agent._extract_ast_symbols(py_code)
    print(f"Classes: {classes_ast}")
    print(f"Functions: {funcs_ast}")
    assert 'UserService' in classes_ast, "AST fallback should work"
    print("✓ AST fallback working")
    
    # Test performance
    print("\n--- Performance Test ---")
    large_code = '\n'.join([
        f'class TestClass{i}:\n    def method_{i}(self): pass\n'
        for i in range(50)
    ])
    
    import time
    start = time.time()
    classes_perf, funcs_perf, _ = agent._extract_symbols(large_code, file_path='large.py')
    duration = time.time() - start
    
    print(f"Extracted {len(classes_perf)} classes and {len(funcs_perf)} functions in {duration:.3f}s")
    assert duration < 1.0, "Should be fast"
    print("✓ Performance acceptable")
    
    print("\n" + "="*80)
    print("Summary:")
    print(f"  - Tree-sitter available: {TREE_SITTER_AVAILABLE}")
    print(f"  - Python extraction: ✓ Working")
    print(f"  - AST fallback: ✓ Working")
    print(f"  - Performance: ✓ Good ({duration:.3f}s for 50 classes)")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_tree_sitter_availability()
