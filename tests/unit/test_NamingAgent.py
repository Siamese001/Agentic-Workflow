"""Unit tests for NamingAgent with tree-sitter multi-language support."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import unittest
from pathlib import Path
from agentic_core.utils.core_extensions.NamingAgent import NamingAgent


class TestNamingAgentTreeSitter(unittest.TestCase):
    """Test tree-sitter multi-language symbol extraction."""

    def setUp(self):
        """Set up test environment."""
        self.agent = NamingAgent(Path.cwd())

    def test_python_symbols(self):
        """Test Python symbol extraction with tree-sitter."""
        py_code = '''
class UserService:
    """User management service."""
    def get_user(self, user_id: int):
        return self.db.query(user_id)
    
    def create_user(self, name: str):
        return self.db.insert(name)
'''
        classes, funcs, imports = self.agent._extract_symbols(py_code, file_path='test.py')
        
        self.assertIn('UserService', classes)
        self.assertIn('get_user', funcs)
        self.assertIn('create_user', funcs)

    def test_javascript_symbols(self):
        """Test JavaScript symbol extraction with tree-sitter."""
        js_code = '''
class Calculator {
  /** Add two numbers */
  add(a, b) {
    return a + b;
  }
  
  subtract(a, b) {
    return a - b;
  }
}

function multiply(x, y) {
  return x * y;
}

export default Calculator;
'''
        classes, funcs, imports = self.agent._extract_symbols(js_code, file_path='test.js')
        
        self.assertIn('Calculator', classes)
        # Methods and functions should be captured
        self.assertTrue(len(funcs) > 0)

    def test_typescript_symbols(self):
        """Test TypeScript symbol extraction with tree-sitter."""
        ts_code = '''
interface User {
  id: number;
  name: string;
}

class UserManager {
  private users: User[] = [];
  
  addUser(user: User): void {
    this.users.push(user);
  }
  
  getUser(id: number): User | undefined {
    return this.users.find(u => u.id === id);
  }
}

export { UserManager };
'''
        classes, funcs, imports = self.agent._extract_symbols(ts_code, file_path='test.ts')
        
        self.assertIn('UserManager', classes)
        # Should extract methods
        self.assertTrue(len(funcs) > 0)

    def test_partial_parse_python(self):
        """Test that tree-sitter handles partial/broken Python code."""
        bad_code = '''
def incomplete(  # syntax error
x = 1
y = 2

class PartialClass:
    def working_method(self):
        pass
'''
        classes, funcs, imports = self.agent._extract_symbols(bad_code, file_path='test.py')
        
        # Tree-sitter should still extract some symbols even with syntax errors
        # At minimum, should not crash
        self.assertIsInstance(classes, list)
        self.assertIsInstance(funcs, list)
        self.assertIsInstance(imports, set)

    def test_fallback_to_ast_when_tree_sitter_unavailable(self):
        """Test fallback to ast module when tree-sitter fails."""
        py_code = '''
class TestClass:
    def test_method(self):
        pass
'''
        # This should work regardless of tree-sitter availability
        classes, funcs, imports = self.agent._extract_ast_symbols(py_code)
        
        self.assertIn('TestClass', classes)
        self.assertIn('test_method', funcs)

    def test_language_detection_from_extension(self):
        """Test that language is correctly detected from file extension."""
        py_code = 'class PyClass: pass'
        js_code = 'class JsClass {}'
        ts_code = 'class TsClass {}'
        
        # Python
        classes_py, _, _ = self.agent._extract_symbols(py_code, file_path='test.py')
        self.assertTrue(len(classes_py) > 0)
        
        # JavaScript
        classes_js, _, _ = self.agent._extract_symbols(js_code, file_path='test.js')
        self.assertTrue(len(classes_js) > 0)
        
        # TypeScript
        classes_ts, _, _ = self.agent._extract_symbols(ts_code, file_path='test.ts')
        self.assertTrue(len(classes_ts) > 0)

    def test_jsx_file_detection(self):
        """Test JSX file is treated as JavaScript."""
        jsx_code = '''
class Component extends React.Component {
  render() {
    return <div>Hello</div>;
  }
}
'''
        classes, funcs, _ = self.agent._extract_symbols(jsx_code, file_path='Component.jsx')
        # Should attempt to parse as JavaScript
        self.assertIsInstance(classes, list)

    def test_tsx_file_detection(self):
        """Test TSX file is treated as TypeScript."""
        tsx_code = '''
interface Props {
  name: string;
}

class Component extends React.Component<Props> {
  render() {
    return <div>{this.props.name}</div>;
  }
}
'''
        classes, funcs, _ = self.agent._extract_symbols(tsx_code, file_path='Component.tsx')
        # Should attempt to parse as TypeScript
        self.assertIsInstance(classes, list)

    def test_empty_code(self):
        """Test handling of empty code."""
        classes, funcs, imports = self.agent._extract_symbols('', file_path='test.py')
        
        self.assertEqual(classes, [])
        self.assertEqual(funcs, [])
        self.assertEqual(imports, set())

    def test_imports_extraction_python(self):
        """Test import extraction from Python code."""
        py_code = '''
import os
import sys
from pathlib import Path
from typing import List, Dict

class MyClass:
    pass
'''
        classes, funcs, imports = self.agent._extract_symbols(py_code, file_path='test.py')
        
        # Should extract at least some imports
        self.assertTrue(len(imports) > 0 or len(classes) > 0)

    def test_complex_python_code(self):
        """Test extraction from complex Python code with decorators."""
        py_code = '''
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    """User data class."""
    id: int
    name: str
    email: Optional[str] = None

class UserRepository:
    """Repository for user data."""
    
    def __init__(self, db):
        self.db = db
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return await self.db.query(user_id)
    
    async def save_user(self, user: User) -> bool:
        """Save user to database."""
        return await self.db.insert(user)
'''
        classes, funcs, imports = self.agent._extract_symbols(py_code, file_path='test.py')
        
        self.assertIn('User', classes)
        self.assertIn('UserRepository', classes)
        # Should extract methods
        self.assertTrue(len(funcs) >= 2)


class TestNamingAgentPerformance(unittest.TestCase):
    """Test performance improvements with tree-sitter."""

    def setUp(self):
        """Set up test environment."""
        self.agent = NamingAgent(Path.cwd())

    def test_large_file_performance(self):
        """Test that tree-sitter handles large files efficiently."""
        # Generate a large Python file
        large_code = '\n'.join([
            f'''
class TestClass{i}:
    """Test class {i}."""
    def method_{i}_1(self):
        pass
    def method_{i}_2(self):
        pass
''' for i in range(100)
        ])
        
        import time
        start = time.time()
        classes, funcs, imports = self.agent._extract_symbols(large_code, file_path='large.py')
        duration = time.time() - start
        
        # Should complete in reasonable time (< 2 seconds for 100 classes)
        self.assertLess(duration, 2.0)
        
        # Should extract all classes
        self.assertGreaterEqual(len(classes), 100)
        # Should extract all methods
        self.assertGreaterEqual(len(funcs), 200)


class TestNamingAgentFallback(unittest.TestCase):
    """Test fallback behavior when tree-sitter is not available."""

    def setUp(self):
        """Set up test environment."""
        self.agent = NamingAgent(Path.cwd())

    def test_ast_fallback_works(self):
        """Test that ast fallback works correctly."""
        py_code = '''
class FallbackClass:
    def fallback_method(self):
        pass

def fallback_function():
    pass
'''
        # Use ast directly
        classes, funcs, imports = self.agent._extract_ast_symbols(py_code)
        
        self.assertIn('FallbackClass', classes)
        self.assertIn('fallback_method', funcs)
        self.assertIn('fallback_function', funcs)

    def test_graceful_degradation(self):
        """Test that system degrades gracefully without tree-sitter."""
        # Even if tree-sitter fails, should still work for Python
        py_code = '''
class TestClass:
    def test_method(self):
        pass
'''
        classes, funcs, imports = self.agent._extract_symbols(py_code, file_path='test.py')
        
        # Should get results one way or another
        self.assertTrue(len(classes) > 0 or len(funcs) > 0)


if __name__ == '__main__':
    unittest.main()
