#!/usr/bin/env python3
"""
Phase 2D_A: Import Graph Purification - Analyzer

Analyzes import statements across all 96 frozen agentic_core modules
to identify cross-layer violations and create a comprehensive import graph.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass
import networkx as nx


@dataclass
class ImportInfo:
    """Represents an import statement"""
    file_path: str
    import_type: str  # 'import' or 'from_import'
    module: str
    imported_names: List[str]
    line_number: int
    is_agentic_core: bool
    layer: Optional[str] = None


@dataclass
class ImportViolation:
    """Represents an import violation"""
    file_path: str
    line_number: int
    import_statement: str
    violation_type: str
    source_layer: str
    target_layer: str
    reason: str


class ImportGraphAnalyzer:
    """Analyzes import graph for agentic_core modules"""
    
    # Define allowed import relationships
    LAYER_RULES = {
        'plan-layer': {  # L1
            'allowed_imports': {'plan-layer'},  # L1 → L1 only
            'layer_name': 'L1 Cognitive Planning',
            'layer_code': 'L1'
        },
        'exec-layer': {  # L2
            'allowed_imports': {'exec-layer'},  # L2 → L2 only
            'layer_name': 'L2 Execution',
            'layer_code': 'L2'
        },
        'orc-layer': {  # L3
            'allowed_imports': {'plan-layer', 'exec-layer'},  # L3 → L1+L2
            'layer_name': 'L3 Orchestration',
            'layer_code': 'L3'
        },
        'mem-layer': {  # L4
            'allowed_imports': {'plan-layer', 'orc-layer'},  # L4 → L1+L3
            'layer_name': 'L4 Memory',
            'layer_code': 'L4'
        },
        'safe-layer': {  # L5
            'allowed_imports': {'plan-layer', 'exec-layer', 'orc-layer', 'mem-layer'},  # L5 → all layers
            'layer_name': 'L5 Safety/Policy',
            'layer_code': 'L5'
        }
    }
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.import_graph = nx.DiGraph()
        self.all_imports: List[ImportInfo] = []
        self.violations: List[ImportViolation] = []
        
    def get_all_agentic_files(self) -> List[Path]:
        """Get all agentic_core Python files (excluding __init__.py)"""
        agentic_core_dir = self.project_root / "agentic_core"
        files = []
        for file_path in agentic_core_dir.rglob("*.py"):
            if file_path.name != "__init__.py":
                files.append(file_path)
        return files
    
    def determine_layer_from_path(self, file_path: Path) -> Optional[str]:
        """Determine layer from file path"""
        path_str = str(file_path).lower()
        for layer_dir in self.LAYER_RULES.keys():
            if layer_dir in path_str:
                return layer_dir
        return None
    
    def extract_imports_from_file(self, file_path: Path) -> List[ImportInfo]:
        """Extract all import statements from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            imports = []
            source_layer = self.determine_layer_from_path(file_path)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        import_info = ImportInfo(
                            file_path=str(file_path.relative_to(self.project_root)),
                            import_type='import',
                            module=alias.name,
                            imported_names=[alias.asname or alias.name],
                            line_number=node.lineno,
                            is_agentic_core=alias.name.startswith('agentic_core'),
                            layer=source_layer
                        )
                        imports.append(import_info)
                        
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        import_info = ImportInfo(
                            file_path=str(file_path.relative_to(self.project_root)),
                            import_type='from_import',
                            module=node.module,
                            imported_names=[alias.asname or alias.name for alias in node.names],
                            line_number=node.lineno,
                            is_agentic_core=node.module.startswith('agentic_core'),
                            layer=source_layer
                        )
                        imports.append(import_info)
            
            return imports
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return []
    
    def analyze_cross_layer_imports(self) -> None:
        """Analyze imports for cross-layer violations"""
        for import_info in self.all_imports:
            if not import_info.is_agentic_core or not import_info.layer:
                continue
                
            # Extract target layer from import path
            target_layer = None
            import_parts = import_info.module.split('.')
            
            if len(import_parts) >= 2 and import_parts[0] == 'agentic_core':
                target_layer = import_parts[1]
                
            if target_layer and target_layer in self.LAYER_RULES:
                source_layer = import_info.layer
                source_rules = self.LAYER_RULES[source_layer]
                
                # Check if this import is allowed
                if target_layer not in source_rules['allowed_imports']:
                    violation = ImportViolation(
                        file_path=import_info.file_path,
                        line_number=import_info.line_number,
                        import_statement=f"from {import_info.module} import {', '.join(import_info.imported_names)}",
                        violation_type="CROSS_LAYER_VIOLATION",
                        source_layer=source_layer,
                        target_layer=target_layer,
                        reason=f"{source_rules['layer_code']} cannot import from {self.LAYER_RULES[target_layer]['layer_code']}"
                    )
                    self.violations.append(violation)
    
    def detect_cyclic_imports(self) -> List[Tuple[str, str]]:
        """Detect cyclic imports in the graph"""
        try:
            cycles = list(nx.simple_cycles(self.import_graph))
            return cycles
        except nx.NetworkXError:
            return []
    
    def build_import_graph(self) -> None:
        """Build the complete import graph"""
        files = self.get_all_agentic_files()
        
        print(f"Building import graph for {len(files)} files...")
        
        # Extract all imports
        for file_path in files:
            file_imports = self.extract_imports_from_file(file_path)
            self.all_imports.extend(file_imports)
            
            # Add file as node in graph
            file_id = str(file_path.relative_to(self.project_root))
            layer = self.determine_layer_from_path(file_path)
            self.import_graph.add_node(file_id, layer=layer, file_path=file_path)
        
        # Build edges based on imports
        for import_info in self.all_imports:
            if import_info.is_agentic_core:
                source_file = import_info.file_path
                target_module = import_info.module
                
                # Find target file(s)
                for node in self.import_graph.nodes():
                    if target_module in node or node.endswith(import_info.module.split('.')[-1] + '.py'):
                        self.import_graph.add_edge(source_file, node, import_info=import_info)
                        break
    
    def generate_violation_report(self) -> Dict[str, Any]:
        """Generate comprehensive violation report"""
        # Group violations by type
        cross_layer_violations = [v for v in self.violations if v.violation_type == "CROSS_LAYER_VIOLATION"]
        cycles = self.detect_cyclic_imports()
        
        # Group by source layer
        violations_by_layer = {}
        for violation in cross_layer_violations:
            source_layer = violation.source_layer
            if source_layer not in violations_by_layer:
                violations_by_layer[source_layer] = []
            violations_by_layer[source_layer].append(violation)
        
        return {
            'total_imports': len(self.all_imports),
            'total_violations': len(self.violations),
            'cross_layer_violations': len(cross_layer_violations),
            'cyclic_imports': len(cycles),
            'violations_by_layer': violations_by_layer,
            'cycle_details': cycles,
            'violation_details': cross_layer_violations
        }
    
    def generate_import_statistics(self) -> Dict[str, Any]:
        """Generate import statistics"""
        agentic_imports = [imp for imp in self.all_imports if imp.is_agentic_core]
        standard_imports = [imp for imp in self.all_imports if not imp.is_agentic_core]
        
        # Count imports by layer
        imports_by_layer = {}
        for import_info in agentic_imports:
            if import_info.layer:
                if import_info.layer not in imports_by_layer:
                    imports_by_layer[import_info.layer] = 0
                imports_by_layer[import_info.layer] += 1
        
        return {
            'total_files': len(self.get_all_agentic_files()),
            'total_imports': len(self.all_imports),
            'agentic_core_imports': len(agentic_imports),
            'standard_library_imports': len(standard_imports),
            'imports_by_layer': imports_by_layer,
            'graph_nodes': self.import_graph.number_of_nodes(),
            'graph_edges': self.import_graph.number_of_edges()
        }
    
    def run_analysis(self) -> Dict[str, Any]:
        """Run complete import graph analysis"""
        print("=== Phase 2D_A: Import Graph Analysis ===")
        
        # Build import graph
        self.build_import_graph()
        
        # Analyze violations
        self.analyze_cross_layer_imports()
        
        # Generate reports
        stats = self.generate_import_statistics()
        violations = self.generate_violation_report()
        
        print(f"\n=== Analysis Results ===")
        print(f"Total files analyzed: {stats['total_files']}")
        print(f"Total imports found: {stats['total_imports']}")
        print(f"Agentic Core imports: {stats['agentic_core_imports']}")
        print(f"Standard library imports: {stats['standard_library_imports']}")
        print(f"Cross-layer violations: {violations['cross_layer_violations']}")
        print(f"Cyclic imports: {violations['cyclic_imports']}")
        
        if violations['cross_layer_violations'] > 0:
            print(f"\n=== Violations by Layer ===")
            for layer, layer_violations in violations['violations_by_layer'].items():
                print(f"{layer}: {len(layer_violations)} violations")
                for violation in layer_violations[:3]:  # Show first 3
                    print(f"  - {violation.file_path}:{violation.line_number} - {violation.reason}")
        
        return {
            'statistics': stats,
            'violations': violations,
            'import_graph': self.import_graph
        }


def main():
    """Main analysis execution"""
    project_root = Path(__file__).parent
    
    analyzer = ImportGraphAnalyzer(project_root)
    results = analyzer.run_analysis()
    
    # Return exit code based on violations found
    violations_count = results['violations']['total_violations']
    return 0 if violations_count == 0 else 1


if __name__ == "__main__":
    exit(main())
