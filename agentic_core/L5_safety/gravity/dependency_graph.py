"""
Dependency Graph - Code structure analysis and impact tracking.
Extracted from BudgetManagerAgent.py for single responsibility.
"""
from __future__ import annotations
import ast
from typing import Dict, List, Any
from agentic_core.utils.file_utils import safe_read_file, safe_write_file


class DependencyGraph:
    """Builds a directed graph of imports and class hierarchies."""

    def __init__(self):
        """Initialize empty dependency graph."""
        self.graph: Dict[str, Dict[str, List[str]]] = {}
        self.reverse_graph: Dict[str, List[str]] = {}

    def build(self, files: List[str]) -> None:
        """Build the dependency graph from a list of Python files.
        
        Args:
            files: List of Python file paths to analyze
        """
        print('🕸️ Building Holistic Code Graph...')
        
        for file_path in files:
            self.graph[file_path] = {'imports': [], 'classes': []}
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for n in node.names:
                            self.graph[file_path]['imports'].append(n.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self.graph[file_path]['imports'].append(node.module)
                    elif isinstance(node, ast.ClassDef):
                        self.graph[file_path]['classes'].append(node.name)
            except Exception:
                # Skip files that can't be parsed
                pass
        
        # Build reverse graph for impact analysis
        for file, data in self.graph.items():
            for imp in data['imports']:
                if imp not in self.reverse_graph:
                    self.reverse_graph[imp] = []
                self.reverse_graph[imp].append(file)

    def get_impact_radius(self, file_path: str) -> List[str]:
        """Returns files that import modules defined in file_path.
        
        Args:
            file_path: Path to file to analyze
            
        Returns:
            List of file paths that would be impacted by changes
        """
        impacted = set()
        module_name = file_path.replace('/', '.').replace('\\', '.').replace('.py', '')
        
        if module_name in self.reverse_graph:
            impacted.update(self.reverse_graph[module_name])
        
        return list(impacted)
    
    def get_imports(self, file_path: str) -> List[str]:
        """Get all imports for a specific file.
        
        Args:
            file_path: Path to file
            
        Returns:
            List of imported module names
        """
        return self.graph.get(file_path, {}).get('imports', [])
    
    def get_classes(self, file_path: str) -> List[str]:
        """Get all class definitions in a specific file.
        
        Args:
            file_path: Path to file
            
        Returns:
            List of class names defined in the file
        """
        return self.graph.get(file_path, {}).get('classes', [])
    
    def get_all_files(self) -> List[str]:
        """Get all files in the dependency graph.
        
        Returns:
            List of all analyzed file paths
        """
        return list(self.graph.keys())
    
    def clear(self) -> None:
        """Clear all graph data."""
        self.graph.clear()
        self.reverse_graph.clear()
