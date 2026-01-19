#!/usr/bin/env python3
"""
Test Suite: Import and AST Utilities

Tests for:
- agentic_core/utils/import_utils.py
- agentic_core/utils/ast_utils.py

All tests must pass 100% before proceeding to Phase 3.3.
"""
import sys
import ast
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from archives.location_violations.import_utils import (
    path_to_module,
    module_to_path,
    safe_import_module,
    safe_import_class,
    safe_import_function,
    get_module_from_file,
    get_class_from_file,
)
from archives.location_violations.ast_utils import (
    safe_parse_file,
    safe_parse_source,
    extract_classes,
    extract_functions,
    extract_imports,
    get_class_methods,
    get_class_attributes,
    find_class_by_name,
    has_method,
    get_docstring,
)


class TestPathToModule:
    """Tests for path_to_module function."""
    
    def test_unix_path(self):
        """Test Case 1: Path Conversion - Unix style."""
        result = path_to_module("agentic_core/L5/Agent.py")
        assert result == "agentic_core.L5.Agent"
    
    def test_windows_path(self):
        """Test Case 2: Windows Path - backslashes."""
        result = path_to_module("agentic_core\\L5\\Agent.py")
        assert result == "agentic_core.L5.Agent"
    
    def test_path_object(self):
        """Test with Path object."""
        result = path_to_module(Path("agentic_core/utils/file_utils.py"))
        assert result == "agentic_core.utils.file_utils"
    
    def test_no_py_extension(self):
        """Test path without .py extension."""
        result = path_to_module("agentic_core/utils/file_utils")
        assert result == "agentic_core.utils.file_utils"
    
    def test_nested_path(self):
        """Test deeply nested path."""
        result = path_to_module("agentic_core/L5_safety/validators/LocationAgent.py")
        assert result == "agentic_core.L5_safety.validators.LocationAgent"
    
    def test_mixed_separators(self):
        """Test path with mixed separators."""
        result = path_to_module("agentic_core/L5\\validators/Agent.py")
        assert result == "agentic_core.L5.validators.Agent"
    
    def test_with_project_root(self, tmp_path):
        """Test with project root for relative path."""
        abs_path = tmp_path / "agentic_core" / "utils" / "test.py"
        result = path_to_module(abs_path, project_root=tmp_path)
        assert result == "agentic_core.utils.test"


class TestModuleToPath:
    """Tests for module_to_path function."""
    
    def test_simple_module(self):
        """Test simple module path."""
        result = module_to_path("agentic_core.utils.file_utils")
        # Path separator is OS-dependent
        assert result.name == "file_utils.py"
        assert "agentic_core" in str(result)
        assert "utils" in str(result)
    
    def test_without_extension(self):
        """Test without .py extension."""
        result = module_to_path("agentic_core.utils", add_py_extension=False)
        assert not str(result).endswith(".py")
    
    def test_with_project_root(self, tmp_path):
        """Test with project root."""
        result = module_to_path("agentic_core.utils.test", project_root=tmp_path)
        assert result.is_absolute()
        assert str(tmp_path) in str(result)


class TestSafeImportModule:
    """Tests for safe_import_module function."""
    
    def test_import_existing_module(self):
        """Test importing an existing module."""
        module = safe_import_module("os")
        assert module is not None
        assert hasattr(module, "path")
    
    def test_import_nested_module(self):
        """Test importing a nested module."""
        module = safe_import_module("os.path")
        assert module is not None
    
    def test_import_nonexistent_module(self):
        """Test importing a non-existent module."""
        module = safe_import_module("nonexistent_module_xyz123")
        assert module is None
    
    def test_import_with_suppress_errors(self):
        """Test import with suppressed errors."""
        module = safe_import_module("nonexistent", suppress_errors=True)
        assert module is None


class TestSafeImportClass:
    """Tests for safe_import_class function."""
    
    def test_import_existing_class(self):
        """Test importing an existing class."""
        cls = safe_import_class("pathlib", "Path")
        assert cls is not None
        assert cls.__name__ == "Path"
    
    def test_import_nonexistent_class(self):
        """Test importing a non-existent class."""
        cls = safe_import_class("os", "NonExistentClass")
        assert cls is None
    
    def test_import_from_nonexistent_module(self):
        """Test importing from non-existent module."""
        cls = safe_import_class("nonexistent_module", "SomeClass")
        assert cls is None


class TestSafeImportFunction:
    """Tests for safe_import_function function."""
    
    def test_import_existing_function(self):
        """Test importing an existing function."""
        func = safe_import_function("os.path", "exists")
        assert func is not None
        assert callable(func)
    
    def test_import_nonexistent_function(self):
        """Test importing a non-existent function."""
        func = safe_import_function("os", "nonexistent_function")
        assert func is None


class TestSafeParseFile:
    """Tests for safe_parse_file function."""
    
    def test_parse_valid_file(self, tmp_path):
        """Test parsing a valid Python file."""
        test_file = tmp_path / "valid.py"
        test_file.write_text("class TestClass:\n    pass\n")
        
        tree = safe_parse_file(test_file)
        
        assert tree is not None
        assert isinstance(tree, ast.Module)
    
    def test_parse_missing_file(self, tmp_path):
        """Test parsing a missing file."""
        missing_file = tmp_path / "missing.py"
        
        tree = safe_parse_file(missing_file)
        
        assert tree is None
    
    def test_parse_bad_syntax(self, tmp_path):
        """Test Case 3: Bad Syntax AST - should return None, NO crash."""
        bad_file = tmp_path / "bad.py"
        bad_file.write_text("def broken_code(:\n    pass\n")
        
        tree = safe_parse_file(bad_file)
        
        assert tree is None  # Should return None, not crash


class TestSafeParseSource:
    """Tests for safe_parse_source function."""
    
    def test_parse_valid_source(self):
        """Test parsing valid source code."""
        source = "class TestClass:\n    pass\n"
        
        tree = safe_parse_source(source)
        
        assert tree is not None
        assert isinstance(tree, ast.Module)
    
    def test_parse_invalid_source(self):
        """Test parsing invalid source code."""
        source = "def broken(:\n    pass\n"
        
        tree = safe_parse_source(source)
        
        assert tree is None


class TestExtractClasses:
    """Tests for extract_classes function."""
    
    def test_extract_simple_class(self, tmp_path):
        """Test Case 4: Valid AST - extract class."""
        test_file = tmp_path / "simple.py"
        test_file.write_text("""
class SimpleAgent:
    def __init__(self):
        pass
    
    def run(self):
        pass
""")
        tree = safe_parse_file(test_file)
        classes = extract_classes(tree)
        
        assert len(classes) == 1
        assert classes[0]["name"] == "SimpleAgent"
        assert "__init__" in classes[0]["methods"]
        assert "run" in classes[0]["methods"]
    
    def test_extract_class_with_bases(self, tmp_path):
        """Test extracting class with base classes."""
        test_file = tmp_path / "inherited.py"
        test_file.write_text("""
class ChildAgent(BaseAgent, Mixin):
    pass
""")
        tree = safe_parse_file(test_file)
        classes = extract_classes(tree)
        
        assert len(classes) == 1
        assert "BaseAgent" in classes[0]["bases"]
        assert "Mixin" in classes[0]["bases"]
    
    def test_extract_decorated_class(self, tmp_path):
        """Test extracting decorated class."""
        test_file = tmp_path / "decorated.py"
        test_file.write_text("""
@dataclass
class DataAgent:
    name: str
""")
        tree = safe_parse_file(test_file)
        classes = extract_classes(tree)
        
        assert len(classes) == 1
        assert "dataclass" in classes[0]["decorators"]
    
    def test_extract_multiple_classes(self, tmp_path):
        """Test extracting multiple classes."""
        test_file = tmp_path / "multiple.py"
        test_file.write_text("""
class Agent1:
    pass

class Agent2:
    pass

class Agent3:
    pass
""")
        tree = safe_parse_file(test_file)
        classes = extract_classes(tree)
        
        assert len(classes) == 3
        names = [c["name"] for c in classes]
        assert "Agent1" in names
        assert "Agent2" in names
        assert "Agent3" in names
    
    def test_none_tree(self):
        """Test with None tree."""
        classes = extract_classes(None)
        assert classes == []


class TestExtractFunctions:
    """Tests for extract_functions function."""
    
    def test_extract_functions(self, tmp_path):
        """Test extracting functions."""
        test_file = tmp_path / "funcs.py"
        test_file.write_text("""
def func1(a, b):
    pass

def func2(x):
    pass
""")
        tree = safe_parse_file(test_file)
        functions = extract_functions(tree)
        
        assert len(functions) >= 2
        names = [f["name"] for f in functions]
        assert "func1" in names
        assert "func2" in names
    
    def test_extract_async_function(self, tmp_path):
        """Test extracting async functions."""
        test_file = tmp_path / "async_funcs.py"
        test_file.write_text("""
async def async_func():
    pass
""")
        tree = safe_parse_file(test_file)
        functions = extract_functions(tree, include_async=True)
        
        async_funcs = [f for f in functions if f["is_async"]]
        assert len(async_funcs) >= 1


class TestExtractImports:
    """Tests for extract_imports function."""
    
    def test_extract_imports(self, tmp_path):
        """Test extracting import statements."""
        test_file = tmp_path / "imports.py"
        test_file.write_text("""
import os
import sys
from pathlib import Path
from typing import List, Dict
""")
        tree = safe_parse_file(test_file)
        imports = extract_imports(tree)
        
        assert "os" in imports["imports"]
        assert "sys" in imports["imports"]
        
        from_modules = [i["module"] for i in imports["from_imports"]]
        assert "pathlib" in from_modules
        assert "typing" in from_modules
    
    def test_none_tree(self):
        """Test with None tree."""
        imports = extract_imports(None)
        assert imports == {"imports": [], "from_imports": []}


class TestGetClassMethods:
    """Tests for get_class_methods function."""
    
    def test_get_methods(self, tmp_path):
        """Test getting class methods."""
        test_file = tmp_path / "methods.py"
        test_file.write_text("""
class TestClass:
    def method1(self):
        pass
    
    def method2(self):
        pass
    
    async def async_method(self):
        pass
""")
        tree = safe_parse_file(test_file)
        class_node = find_class_by_name(tree, "TestClass")
        methods = get_class_methods(class_node)
        
        assert "method1" in methods
        assert "method2" in methods
        assert "async_method" in methods


class TestFindClassByName:
    """Tests for find_class_by_name function."""
    
    def test_find_existing_class(self, tmp_path):
        """Test finding an existing class."""
        test_file = tmp_path / "find.py"
        test_file.write_text("""
class TargetClass:
    pass

class OtherClass:
    pass
""")
        tree = safe_parse_file(test_file)
        node = find_class_by_name(tree, "TargetClass")
        
        assert node is not None
        assert node.name == "TargetClass"
    
    def test_find_nonexistent_class(self, tmp_path):
        """Test finding a non-existent class."""
        test_file = tmp_path / "find.py"
        test_file.write_text("class SomeClass:\n    pass\n")
        
        tree = safe_parse_file(test_file)
        node = find_class_by_name(tree, "NonExistent")
        
        assert node is None


class TestHasMethod:
    """Tests for has_method function."""
    
    def test_has_existing_method(self, tmp_path):
        """Test checking for existing method."""
        test_file = tmp_path / "has.py"
        test_file.write_text("""
class TestClass:
    def target_method(self):
        pass
""")
        tree = safe_parse_file(test_file)
        class_node = find_class_by_name(tree, "TestClass")
        
        assert has_method(class_node, "target_method") is True
        assert has_method(class_node, "nonexistent") is False


class TestGetDocstring:
    """Tests for get_docstring function."""
    
    def test_get_class_docstring(self, tmp_path):
        """Test getting class docstring."""
        test_file = tmp_path / "doc.py"
        test_file.write_text('''
class DocClass:
    """This is the docstring."""
    pass
''')
        tree = safe_parse_file(test_file)
        class_node = find_class_by_name(tree, "DocClass")
        docstring = get_docstring(class_node)
        
        assert docstring == "This is the docstring."
    
    def test_no_docstring(self, tmp_path):
        """Test class without docstring."""
        test_file = tmp_path / "nodoc.py"
        test_file.write_text("class NoDocClass:\n    pass\n")
        
        tree = safe_parse_file(test_file)
        class_node = find_class_by_name(tree, "NoDocClass")
        docstring = get_docstring(class_node)
        
        assert docstring is None


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "#" * 60)
    print("# Code Utils Test Suite (Import + AST)")
    print("#" * 60)
    
    # Run with pytest
    exit_code = pytest.main([__file__, "-v", "--tb=short"])
    
    if exit_code == 0:
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED (100%)")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(run_all_tests())
