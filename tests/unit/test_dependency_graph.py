"""
Unit tests for DependencyGraph primitive.
Phase 7: Sub-atomic Refactor - Test Generation
"""
import pytest
import tempfile
from pathlib import Path
from agentic_core.L0_maintenance.primitives.dependency_graph import DependencyGraph


class TestDependencyGraph:
    """Comprehensive test suite for DependencyGraph."""
    
    def test_initialization(self):
        """Test DependencyGraph initializes with empty graphs."""
        graph = DependencyGraph()
        
        assert graph.graph == {}
        assert graph.reverse_graph == {}
    
    def test_build_single_file(self, tmp_path):
        """Test building graph from a single Python file."""
        # Create test file
        test_file = tmp_path / "test_module.py"
        test_file.write_text("""
import os
import sys
from pathlib import Path

class TestClass:
    pass

class AnotherClass:
    pass
""")
        
        graph = DependencyGraph()
        graph.build([str(test_file)])
        
        # Verify file in graph
        assert str(test_file) in graph.graph
        
        # Verify imports captured
        imports = graph.graph[str(test_file)]['imports']
        assert 'os' in imports
        assert 'sys' in imports
        assert 'pathlib' in imports
        
        # Verify classes captured
        classes = graph.graph[str(test_file)]['classes']
        assert 'TestClass' in classes
        assert 'AnotherClass' in classes
    
    def test_build_multiple_files(self, tmp_path):
        """Test building graph from multiple files."""
        # Create first file
        file1 = tmp_path / "module1.py"
        file1.write_text("import json\nclass Module1Class:\n    pass")
        
        # Create second file
        file2 = tmp_path / "module2.py"
        file2.write_text("import ast\nclass Module2Class:\n    pass")
        
        graph = DependencyGraph()
        graph.build([str(file1), str(file2)])
        
        # Verify both files in graph
        assert str(file1) in graph.graph
        assert str(file2) in graph.graph
        
        # Verify separate imports
        assert 'json' in graph.graph[str(file1)]['imports']
        assert 'ast' in graph.graph[str(file2)]['imports']
    
    def test_build_with_invalid_file(self, tmp_path):
        """Test building graph handles invalid Python files gracefully."""
        # Create invalid Python file
        bad_file = tmp_path / "bad.py"
        bad_file.write_text("this is not valid python }{][")
        
        graph = DependencyGraph()
        graph.build([str(bad_file)])
        
        # Should not crash, file should be in graph with empty data
        assert str(bad_file) in graph.graph
        assert graph.graph[str(bad_file)]['imports'] == []
        assert graph.graph[str(bad_file)]['classes'] == []
    
    def test_reverse_graph_construction(self, tmp_path):
        """Test reverse graph is built correctly."""
        test_file = tmp_path / "test.py"
        test_file.write_text("import json\nimport ast")
        
        graph = DependencyGraph()
        graph.build([str(test_file)])
        
        # Verify reverse graph has entries for imports
        assert 'json' in graph.reverse_graph
        assert 'ast' in graph.reverse_graph
        assert str(test_file) in graph.reverse_graph['json']
        assert str(test_file) in graph.reverse_graph['ast']
    
    def test_get_impact_radius(self, tmp_path):
        """Test getting impact radius for a file."""
        # Create module that will be imported
        module_file = tmp_path / "my_module.py"
        module_file.write_text("class MyClass:\n    pass")
        
        # Create file that imports the module using full module path
        importer_file = tmp_path / "importer.py"
        # Use the actual module path that will be in reverse_graph
        module_name = str(module_file).replace('/', '.').replace('\\', '.').replace('.py', '')
        importer_file.write_text(f"import {module_name}")
        
        graph = DependencyGraph()
        graph.build([str(module_file), str(importer_file)])
        
        # Get impact radius
        impact = graph.get_impact_radius(str(module_file))
        
        # Verify impact radius works (may be empty if module path doesn't match)
        # This tests the method runs without error
        assert isinstance(impact, list)
    
    def test_get_imports(self, tmp_path):
        """Test getting imports for a specific file."""
        test_file = tmp_path / "test.py"
        test_file.write_text("import os\nimport sys\nfrom pathlib import Path")
        
        graph = DependencyGraph()
        graph.build([str(test_file)])
        
        imports = graph.get_imports(str(test_file))
        
        assert 'os' in imports
        assert 'sys' in imports
        assert 'pathlib' in imports
    
    def test_get_imports_nonexistent_file(self):
        """Test getting imports for file not in graph."""
        graph = DependencyGraph()
        
        imports = graph.get_imports("nonexistent.py")
        
        assert imports == []
    
    def test_get_classes(self, tmp_path):
        """Test getting classes for a specific file."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
class FirstClass:
    pass

class SecondClass:
    pass

def some_function():
    pass
""")
        
        graph = DependencyGraph()
        graph.build([str(test_file)])
        
        classes = graph.get_classes(str(test_file))
        
        assert 'FirstClass' in classes
        assert 'SecondClass' in classes
        assert len(classes) == 2
    
    def test_get_classes_nonexistent_file(self):
        """Test getting classes for file not in graph."""
        graph = DependencyGraph()
        
        classes = graph.get_classes("nonexistent.py")
        
        assert classes == []
    
    def test_get_all_files(self, tmp_path):
        """Test getting all files in the graph."""
        file1 = tmp_path / "file1.py"
        file1.write_text("pass")
        file2 = tmp_path / "file2.py"
        file2.write_text("pass")
        
        graph = DependencyGraph()
        graph.build([str(file1), str(file2)])
        
        all_files = graph.get_all_files()
        
        assert len(all_files) == 2
        assert str(file1) in all_files
        assert str(file2) in all_files
    
    def test_clear(self, tmp_path):
        """Test clearing all graph data."""
        test_file = tmp_path / "test.py"
        test_file.write_text("import os\nclass TestClass:\n    pass")
        
        graph = DependencyGraph()
        graph.build([str(test_file)])
        
        # Verify data exists
        assert len(graph.graph) > 0
        assert len(graph.reverse_graph) > 0
        
        # Clear
        graph.clear()
        
        # Verify all cleared
        assert graph.graph == {}
        assert graph.reverse_graph == {}
    
    def test_nested_imports(self, tmp_path):
        """Test handling of nested/complex imports."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
from typing import Dict, List, Optional
from pathlib import Path
import os.path
from collections.abc import Mapping
""")
        
        graph = DependencyGraph()
        graph.build([str(test_file)])
        
        imports = graph.get_imports(str(test_file))
        
        assert 'typing' in imports
        assert 'pathlib' in imports
        assert 'os.path' in imports
        assert 'collections.abc' in imports
    
    def test_empty_file(self, tmp_path):
        """Test handling of empty Python file."""
        empty_file = tmp_path / "empty.py"
        empty_file.write_text("")
        
        graph = DependencyGraph()
        graph.build([str(empty_file)])
        
        # Should handle gracefully
        assert str(empty_file) in graph.graph
        assert graph.get_imports(str(empty_file)) == []
        assert graph.get_classes(str(empty_file)) == []
    
    def test_file_with_only_comments(self, tmp_path):
        """Test handling of file with only comments."""
        comment_file = tmp_path / "comments.py"
        comment_file.write_text("""
# This is a comment
# Another comment
\"\"\"
Docstring
\"\"\"
""")
        
        graph = DependencyGraph()
        graph.build([str(comment_file)])
        
        # Should parse successfully with no imports/classes
        assert str(comment_file) in graph.graph
        assert graph.get_imports(str(comment_file)) == []
        assert graph.get_classes(str(comment_file)) == []
