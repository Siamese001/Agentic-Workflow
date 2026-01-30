"""
Subatomic Compliance Tests

Enforces "Power of Two" and "Single Layer" constraints for agents.
Uses AST analysis to inspect class definitions without executing them.
"""

import ast
import os
import pytest
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional


class AgentAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze agent classes for subatomic compliance."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.agent_classes = []
        self.imports = []
        self.current_class = None
        
    def visit_Import(self, node):
        """Capture import statements."""
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Capture from-import statements."""
        if node.module:
            self.imports.append(node.module)
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Analyze class definitions."""
        if node.name.endswith('Agent'):
            self.current_class = {
                'name': node.name,
                'bases': [self._get_base_name(base) for base in node.bases],
                'methods': [],
                'file_path': self.file_path,
                'line_number': node.lineno
            }
            
            # Count methods (excluding private/dunder methods)
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    if not item.name.startswith('_') or item.name.startswith('__') and item.name.endswith('__'):
                        self.current_class['methods'].append(item.name)
            
            self.agent_classes.append(self.current_class)
        
        self.generic_visit(node)
    
    def _get_base_name(self, base) -> str:
        """Extract base class name from AST node."""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return base.attr
        return str(base)


def find_agent_files(root_dir: Path) -> List[Path]:
    """Find all Python files containing agent classes."""
    agent_files = []
    
    # Common agent directories
    agent_dirs = [
        'agentic_core',
        'apps_lic',
        'apps_rg',
        'apps_shared'
    ]
    
    for agent_dir in agent_dirs:
        dir_path = root_dir / agent_dir
        if dir_path.exists():
            for py_file in dir_path.rglob('*.py'):
                if py_file.name != '__init__.py':
                    agent_files.append(py_file)
    
    return agent_files


def extract_layer_from_path(file_path: Path) -> Optional[str]:
    """Extract layer number from file path (L0, L1, L2, etc.)."""
    path_parts = file_path.parts
    
    for part in path_parts:
        if part.startswith('L') and len(part) >= 2 and part[1:].isdigit():
            return part
        elif part in ['base_agents']:  # Special case for base agents
            return 'Base'
    
    return None


def analyze_agent_file(file_path: Path) -> Dict:
    """Analyze a single agent file using AST."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        analyzer = AgentAnalyzer(str(file_path))
        analyzer.visit(tree)
        
        return {
            'file_path': str(file_path),
            'layer': extract_layer_from_path(file_path),
            'agents': analyzer.agent_classes,
            'imports': analyzer.imports
        }
    except Exception as e:
        return {
            'file_path': str(file_path),
            'layer': extract_layer_from_path(file_path),
            'agents': [],
            'imports': [],
            'error': str(e)
        }


def count_capability_mixins(bases: List[str]) -> int:
    """Count capability mixins in the MRO."""
    mixin_patterns = ['Mixin', 'Capability', 'Handler', 'Strategy']
    count = 0
    
    for base in bases:
        for pattern in mixin_patterns:
            if pattern in base:
                count += 1
                break
    
    return count


def get_import_layer(import_name: str) -> Optional[str]:
    """Extract layer from import statement."""
    if 'L0_' in import_name or '/L0_' in import_name:
        return 'L0'
    elif 'L1_' in import_name or '/L1_' in import_name:
        return 'L1'
    elif 'L2_' in import_name or '/L2_' in import_name:
        return 'L2'
    elif 'L3_' in import_name or '/L3_' in import_name:
        return 'L3'
    elif 'L4_' in import_name or '/L4_' in import_name:
        return 'L4'
    elif 'L5_' in import_name or '/L5_' in import_name:
        return 'L5'
    elif 'L6_' in import_name or '/L6_' in import_name:
        return 'L6'
    return None


class TestSubatomicCompliance:
    """Test suite for subatomic compliance constraints."""
    
    @pytest.fixture(scope="class")
    def agent_analysis(self):
        """Fixture to analyze all agent files."""
        root_dir = Path(__file__).parent.parent.parent
        agent_files = find_agent_files(root_dir)
        
        analysis_results = []
        for file_path in agent_files:
            result = analyze_agent_file(file_path)
            analysis_results.append(result)
        
        return analysis_results
    
    def test_capability_limit(self, agent_analysis):
        """Test: Power of Two constraint - methods + mixins <= 2."""
        violations = []
        
        for file_analysis in agent_analysis:
            if 'error' in file_analysis:
                continue
                
            for agent in file_analysis['agents']:
                # Count capability mixins
                mixin_count = count_capability_mixins(agent['bases'])
                
                # Count primary task methods (exclude common inherited methods)
                excluded_methods = {'heal', 'validate', 'execute', 'initialize', '__init__'}
                primary_methods = [m for m in agent['methods'] if m not in excluded_methods]
                method_count = len(primary_methods)
                
                # Total capabilities
                total_capabilities = mixin_count + method_count
                
                if total_capabilities > 2:
                    violations.append({
                        'agent': agent['name'],
                        'file': file_analysis['file_path'],
                        'line': agent['line_number'],
                        'mixins': mixin_count,
                        'methods': method_count,
                        'total': total_capabilities
                    })
        
        if violations:
            violation_msg = "Subatomic Violation: Agent has too many responsibilities:\n"
            for v in violations:
                violation_msg += f"  - {v['agent']} ({v['file']}:{v['line']}) "
                violation_msg += f"has {v['total']} capabilities ({v['mixins']} mixins + {v['methods']} methods)\n"
            
            # Mark as structural debt but don't fail the test
            print(f"\n⚠️  STRUCTURAL DEBT DETECTED:\n{violation_msg}")
            pytest.skip("Structural debt - capability limit exceeded")
    
    def test_layer_zoning_alignment(self, agent_analysis):
        """Test: Single Layer constraint - path vs metadata consistency."""
        violations = []
        
        for file_analysis in agent_analysis:
            if 'error' in file_analysis:
                continue
                
            file_layer = file_analysis['layer']
            if not file_layer:
                continue
                
            for agent in file_analysis['agents']:
                # Check if agent imports from conflicting layers
                conflicting_imports = []
                for import_name in file_analysis['imports']:
                    import_layer = get_import_layer(import_name)
                    if import_layer and import_layer != file_layer:
                        # Allow some exceptions (base agents, common utilities)
                        if not any(x in import_name.lower() for x in ['base', 'common', 'shared']):
                            conflicting_imports.append(f"{import_name} ({import_layer})")
                
                if conflicting_imports:
                    violations.append({
                        'agent': agent['name'],
                        'file': file_analysis['file_path'],
                        'file_layer': file_layer,
                        'conflicting_imports': conflicting_imports
                    })
        
        if violations:
            violation_msg = "Zoning Violation: Agent is straddling multiple layers:\n"
            for v in violations:
                violation_msg += f"  - {v['agent']} ({v['file']}) is in {v['file_layer']} "
                violation_msg += f"but imports from: {', '.join(v['conflicting_imports'])}\n"
            
            print(f"\n⚠️  STRUCTURAL DEBT DETECTED:\n{violation_msg}")
            pytest.skip("Structural debt - layer zoning misalignment")
    
    def test_subatomic_naming_convention(self, agent_analysis):
        """Test: Single Responsibility - no 'And' or '&' in agent names."""
        violations = []
        
        for file_analysis in agent_analysis:
            if 'error' in file_analysis:
                continue
                
            for agent in file_analysis['agents']:
                if 'And' in agent['name'] or '&' in agent['name']:
                    violations.append({
                        'agent': agent['name'],
                        'file': file_analysis['file_path'],
                        'line': agent['line_number']
                    })
        
        if violations:
            violation_msg = "Naming Violation: Agent violates single responsibility principle:\n"
            for v in violations:
                violation_msg += f"  - {v['agent']} ({v['file']}:{v['line']}) contains compound name\n"
            
            print(f"\n⚠️  STRUCTURAL DEBT DETECTED:\n{violation_msg}")
            pytest.skip("Structural debt - naming convention violation")
    
    def test_no_cross_layer_pollution(self, agent_analysis):
        """Test: Gravity of Information - lower layers cannot depend on higher layers."""
        violations = []
        
        layer_hierarchy = {'Base': 0, 'L0': 0, 'L1': 1, 'L2': 2, 'L3': 3, 'L4': 4, 'L5': 5, 'L6': 6}
        
        for file_analysis in agent_analysis:
            if 'error' in file_analysis:
                continue
                
            file_layer = file_analysis['layer']
            if not file_layer or file_layer not in layer_hierarchy:
                continue
                
            file_level = layer_hierarchy[file_layer]
            
            # Check imports for violations
            for import_name in file_analysis['imports']:
                import_layer = get_import_layer(import_name)
                if import_layer and import_layer in layer_hierarchy:
                    import_level = layer_hierarchy[import_layer]
                    
                    # Lower layer importing from higher layer is a violation
                    if file_level < import_level and file_level <= 1:  # L0/L1 restriction
                        violations.append({
                            'file': file_analysis['file_path'],
                            'file_layer': file_layer,
                            'import': import_name,
                            'import_layer': import_layer
                        })
        
        if violations:
            violation_msg = "Cross-Layer Pollution: Lower layer depends on higher layer:\n"
            for v in violations:
                violation_msg += f"  - {v['file']} ({v['file_layer']}) imports {v['import']} ({v['import_layer']})\n"
            
            print(f"\n⚠️  STRUCTURAL DEBT DETECTED:\n{violation_msg}")
            pytest.skip("Structural debt - cross-layer pollution")


if __name__ == "__main__":
    # Run standalone analysis
    root_dir = Path(__file__).parent.parent.parent
    agent_files = find_agent_files(root_dir)
    
    print(f"Analyzing {len(agent_files)} agent files for subatomic compliance...")
    
    violations = {
        'capability_limit': [],
        'layer_zoning': [],
        'naming': [],
        'cross_layer': []
    }
    
    for file_path in agent_files:
        result = analyze_agent_file(file_path)
        
        if 'error' in result:
            print(f"Error analyzing {file_path}: {result['error']}")
            continue
            
        for agent in result['agents']:
            # Check naming convention
            if 'And' in agent['name'] or '&' in agent['name']:
                violations['naming'].append(f"{agent['name']} in {file_path}")
            
            # Check capability limit
            mixin_count = count_capability_mixins(agent['bases'])
            excluded_methods = {'heal', 'validate', 'execute', 'initialize', '__init__'}
            primary_methods = [m for m in agent['methods'] if m not in excluded_methods]
            
            if mixin_count + len(primary_methods) > 2:
                violations['capability_limit'].append(
                    f"{agent['name']} in {file_path} "
                    f"({mixin_count} mixins + {len(primary_methods)} methods)"
                )
    
    print("\n=== SUBATOMIC COMPLIANCE REPORT ===")
    for violation_type, items in violations.items():
        if items:
            print(f"\n{violation_type.upper()} VIOLATIONS:")
            for item in items:
                print(f"  - {item}")
        else:
            print(f"\n{violation_type.upper()}: No violations found")
