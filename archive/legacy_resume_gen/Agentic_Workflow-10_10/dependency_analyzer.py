#!/usr/bin/env python3
"""
Dependency analyzer for Agentic Workflow reorganization.
Builds a comprehensive import dependency graph to identify circular dependencies
 and plan safe migration phases.
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, deque
import json


class ImportVisitor(ast.NodeVisitor):
    """AST visitor to extract import statements from Python files."""
    
    def __init__(self, filepath: Path, root_dir: Path):
        self.filepath = filepath
        self.root_dir = root_dir
        self.imports = set()
        self.relative_imports = set()
        
    def visit_Import(self, node):
        """Handle 'import module' statements."""
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node):
        """Handle 'from module import name' statements."""
        if node.module:
            # Handle relative imports
            if node.level > 0:
                # Calculate relative path
                parts = self.filepath.relative_to(self.root_dir).parts
                # Go up directories based on level
                up_parts = parts[:-node.level] if node.level <= len(parts) else []
                base_path = Path(*up_parts)
                module_path = base_path / Path(*node.module.split('.'))
                self.relative_imports.add(str(module_path))
            else:
                self.imports.add(node.module)
        self.generic_visit(node)


class DependencyAnalyzer:
    """Analyzes Python import dependencies across the codebase."""
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.dependencies = defaultdict(set)  # module -> set of imported modules
        self.reverse_dependencies = defaultdict(set)  # module -> set of modules that import it
        self.module_files = {}  # module name -> filepath
        self.file_modules = {}  # filepath -> module name
        self.circular_dependencies = []
        
    def get_module_name(self, filepath: Path) -> str:
        """Convert filepath to module name."""
        relative_path = filepath.relative_to(self.root_dir)
        parts = list(relative_path.parts)
        if parts[-1] == '__init__.py':
            parts = parts[:-1]
        else:
            parts[-1] = parts[-1][:-3]  # Remove .py extension
        return '.'.join(parts) if parts else ''
        
    def resolve_import_path(self, import_name: str, source_file: Path) -> Optional[str]:
        """Resolve import name to actual module path in the codebase."""
        # Try direct resolution
        import_path_str = '/'.join(import_name.split('.'))
        potential_paths = [
            self.root_dir / import_path_str / '__init__.py',
            self.root_dir / (import_path_str + '.py'),
        ]
        
        for path in potential_paths:
            if path.exists():
                return self.get_module_name(path)
                
        # Try resolving relative to source file's location
        source_dir = source_file.parent
        relative_path_str = '/'.join(import_name.split('.'))
        relative_path = source_dir / relative_path_str
        
        potential_relative = [
            relative_path / '__init__.py',
            relative_path.with_suffix('.py'),
        ]
        
        for path in potential_relative:
            if path.exists():
                return self.get_module_name(path)
                
        return None
        
    def analyze_file(self, filepath: Path) -> List[str]:
        """Analyze a single Python file for imports."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            visitor = ImportVisitor(filepath, self.root_dir)
            visitor.visit(tree)
            
            imports = []
            module_name = self.get_module_name(filepath)
            
            for import_name in visitor.imports:
                resolved = self.resolve_import_path(import_name, filepath)
                if resolved and resolved != module_name:  # Skip self-imports
                    imports.append(resolved)
                    
            for import_name in visitor.relative_imports:
                resolved = self.resolve_import_path(import_name, filepath)
                if resolved and resolved != module_name:
                    imports.append(resolved)
                    
            return imports
            
        except Exception as e:
            print(f"Error analyzing {filepath}: {e}")
            return []
            
    def find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies using DFS."""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node: str, path: List[str]):
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
                
            if node in visited:
                return
                
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.dependencies[node]:
                dfs(neighbor, path)
                
            path.pop()
            rec_stack.remove(node)
            
        for module in self.dependencies:
            if module not in visited:
                dfs(module, [])
                
        return cycles
        
    def analyze(self) -> Dict:
        """Analyze the entire codebase."""
        print("Analyzing Python files...")
        
        # Find all Python files
        python_files = []
        for filepath in self.root_dir.rglob("*.py"):
            # Skip cache, test directories, and .git
            if any(skip in str(filepath) for skip in ['__pycache__', '.pytest_cache', '.venv', '.git']):
                continue
            python_files.append(filepath)
            
        print(f"Found {len(python_files)} Python files")
        
        # Analyze each file
        for filepath in python_files:
            module_name = self.get_module_name(filepath)
            self.module_files[module_name] = filepath
            self.file_modules[filepath] = module_name
            imports = self.analyze_file(filepath)
            self.dependencies[module_name] = set(imports)
            
            # Build reverse dependencies
            for imported_module in imports:
                self.reverse_dependencies[imported_module].add(module_name)
                
        print(f"Analyzed {len(self.module_files)} modules")
        
        # Find circular dependencies
        self.circular_dependencies = self.find_circular_dependencies()
        
        return self.generate_report()
        
    def generate_report(self) -> Dict:
        """Generate a comprehensive dependency report."""
        report = {
            'summary': {
                'total_modules': len(self.module_files),
                'total_dependencies': sum(len(deps) for deps in self.dependencies.values()),
                'circular_dependencies': len(self.circular_dependencies)
            },
            'modules': {},
            'circular_dependencies': self.circular_dependencies,
            'orphaned_modules': [],
            'root_modules': []
        }
        
        # Module details
        for module, deps in self.dependencies.items():
            report['modules'][module] = {
                'filepath': str(self.module_files[module]),
                'imports': sorted(list(deps)),
                'imported_by': sorted(list(self.reverse_dependencies[module])),
                'dependency_count': len(deps),
                'reverse_dependency_count': len(self.reverse_dependencies[module])
            }
            
        # Find orphaned modules (no imports and no one imports them)
        for module in self.module_files:
            if (len(self.dependencies[module]) == 0 and 
                len(self.reverse_dependencies[module]) == 0):
                report['orphaned_modules'].append(module)
                
        # Find root modules (no imports from within the project)
        for module in self.module_files:
            internal_imports = [dep for dep in self.dependencies[module] 
                              if dep in self.module_files]
            if len(internal_imports) == 0:
                report['root_modules'].append(module)
                
        return report
        
    def save_report(self, report: Dict, output_path: Path):
        """Save the dependency report to a JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"Dependency report saved to {output_path}")
        
    def print_summary(self, report: Dict):
        """Print a summary of the dependency analysis."""
        summary = report['summary']
        print(f"\n=== DEPENDENCY ANALYSIS SUMMARY ===")
        print(f"Total modules: {summary['total_modules']}")
        print(f"Total dependencies: {summary['total_dependencies']}")
        print(f"Circular dependencies: {summary['circular_dependencies']}")
        
        if report['circular_dependencies']:
            print(f"\n⚠️  CIRCULAR DEPENDENCIES FOUND:")
            for i, cycle in enumerate(report['circular_dependencies'], 1):
                print(f"  {i}. {' -> '.join(cycle)}")
                
        print(f"\n📊 MODULE STATISTICS:")
        print(f"  Orphaned modules: {len(report['orphaned_modules'])}")
        print(f"  Root modules: {len(report['root_modules'])}")
        
        # Show most connected modules
        module_stats = [(name, data['dependency_count'] + data['reverse_dependency_count'])
                       for name, data in report['modules'].items()]
        module_stats.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n🔗 MOST CONNECTED MODULES:")
        for name, connections in module_stats[:10]:
            print(f"  {name}: {connections} connections")


def main():
    """Run the dependency analyzer."""
    root_dir = Path(__file__).parent
    analyzer = DependencyAnalyzer(root_dir)
    
    print("Starting dependency analysis...")
    report = analyzer.analyze()
    
    # Save detailed report
    output_path = root_dir / "dependency_report.json"
    analyzer.save_report(report, output_path)
    
    # Print summary
    analyzer.print_summary(report)
    
    # Return exit code based on circular dependencies
    if report['circular_dependencies']:
        print(f"\n❌ Found {len(report['circular_dependencies'])} circular dependencies!")
        return 1
    else:
        print(f"\n✅ No circular dependencies found!")
        return 0


if __name__ == "__main__":
    exit(main())
