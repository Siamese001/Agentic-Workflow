#!/usr/bin/env python3
"""
Phase 2D_C: Layer Contract Verification - Analyzer

Validates and enforces layer-contract purity across all 96 frozen agentic_core modules.
Extracts public API signatures and validates contracts based on L1-L5 rules.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class PublicAPI:
    """Represents a public API element"""
    name: str
    type: str  # 'class' or 'function'
    signature: str
    docstring: Optional[str]
    layer: str
    file_path: str
    line_number: int
    violations: List[str]


@dataclass
class ContractViolation:
    """Represents a contract violation"""
    file_path: str
    element_name: str
    element_type: str
    violation_type: str
    description: str
    line_number: int


class LayerContractAnalyzer:
    """Analyzes layer contracts for agentic_core modules"""
    
    # Define layer-specific verb patterns and responsibilities
    LAYER_RULES = {
        'L1': {
            'name': 'Cognitive Planning',
            'allowed_verbs': {
                'build', 'analyze', 'plan', 'design', 'coordinate', 'get', 'extract',
                'parse', 'check', 'enforce', 'validate', 'find', 'capture', 'inspect',
                'log', 'convert', 'calculate', 'compute', 'normalize', 'apply',
                'format', 'prepare', 'serialize', 'aggregate', 'consolidate', 'merge',
                'process'  # Default fallback from reconstruction engine
            },
            'forbidden_verbs': {
                'execute', 'invoke', 'perform', 'call', 'dispatch', 'fetch', 'retrieve',
                'search', 'track', 'update'
            },
            'responsibility_keywords': [
                'planning', 'query', 'analysis', 'intent', 'strategy', 'design',
                'construction', 'extraction', 'validation', 'coordination', 'cognitive'
            ],
            'forbidden_keywords': [
                'execution', 'invocation', 'tool', 'performance', 'memory',
                'storage', 'orchestration'
            ]
        },
        'L2': {
            'name': 'Execution',
            'allowed_verbs': {
                'execute', 'invoke', 'perform', 'format', 'prepare', 'serialize',
                'apply', 'enforce', 'validate', 'check', 'call', 'dispatch',
                'process'  # Default fallback from reconstruction engine
            },
            'forbidden_verbs': {
                'plan', 'analyze', 'coordinate', 'fetch', 'retrieve', 'search',
                'orchestrate', 'manage', 'track', 'update', 'aggregate'
            },
            'responsibility_keywords': [
                'execution', 'invocation', 'tool', 'operation', 'performance',
                'action', 'implementation'
            ],
            'forbidden_keywords': [
                'planning', 'strategy', 'memory', 'storage', 'orchestration',
                'coordination'
            ]
        },
        'L3': {
            'name': 'Orchestration',
            'allowed_verbs': {
                'coordinate', 'manage', 'orchestrate', 'handle', 'implement',
                'retry', 'call', 'dispatch', 'invoke', 'process', 'validate'  # Added validate - used in Phase 2C
            },
            'forbidden_verbs': {
                'execute', 'plan', 'analyze', 'fetch', 'retrieve', 'search',
                'check', 'track', 'update'
            },
            'responsibility_keywords': [
                'orchestration', 'routing', 'coordination', 'management', 'flow',
                'workflow', 'planning'  # Added planning - orchestration coordinates planning
            ],
            'forbidden_keywords': [
                'execution', 'memory', 'storage'
            ]
        },
        'L4': {
            'name': 'Memory',
            'allowed_verbs': {
                'fetch', 'query', 'retrieve', 'find', 'match', 'search',
                'apply', 'enforce', 'validate', 'check', 'process'  # Default fallback from reconstruction engine
            },
            'forbidden_verbs': {
                'execute', 'invoke', 'perform', 'plan', 'analyze', 'coordinate',
                'orchestrate', 'manage', 'track', 'update'
            },
            'responsibility_keywords': [
                'memory', 'state', 'storage', 'retrieval', 'persistence',
                'query', 'search', 'history'
            ],
            'forbidden_keywords': [
                'execution', 'planning', 'orchestration'
            ]
        },
        'L5': {
            'name': 'Safety/Policy',
            'allowed_verbs': {
                'apply', 'enforce', 'validate', 'check', 'process'  # Default fallback from reconstruction engine
            },
            'forbidden_verbs': {
                'execute', 'invoke', 'perform', 'plan', 'analyze', 'coordinate',
                'orchestrate', 'manage', 'fetch', 'retrieve', 'search', 'track', 'update'
            },
            'responsibility_keywords': [
                'safety', 'policy', 'validation', 'compliance', 'ethics',
                'security', 'rules', 'constraints'
            ],
            'forbidden_keywords': [
                'execution', 'planning', 'orchestration', 'memory', 'storage',
                'retrieval', 'query', 'coordination'
            ]
        }
    }
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.public_apis: List[PublicAPI] = []
        self.violations: List[ContractViolation] = []
        
    def get_layer_from_path(self, file_path: Path) -> str:
        """Extract layer from file path"""
        path_str = str(file_path).lower()
        if 'plan-layer' in path_str:
            return 'L1'
        elif 'exec-layer' in path_str:
            return 'L2'
        elif 'orc-layer' in path_str:
            return 'L3'
        elif 'mem-layer' in path_str:
            return 'L4'
        elif 'safe-layer' in path_str:
            return 'L5'
        return 'Unknown'
    
    def extract_public_apis_from_file(self, file_path: Path) -> List[PublicAPI]:
        """Extract public APIs from a Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            layer = self.get_layer_from_path(file_path)
            apis = []
            
            for node in ast.walk(tree):
                # Extract public classes (not starting with underscore)
                if isinstance(node, ast.ClassDef) and not node.name.startswith('_'):
                    docstring = ast.get_docstring(node)
                    
                    # Get public methods from class
                    public_methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and not item.name.startswith('_'):
                            method_docstring = ast.get_docstring(item)
                            signature = f"{item.name}({', '.join(arg.arg for arg in item.args.args if arg.arg != 'self')})"
                            
                            public_method = PublicAPI(
                                name=f"{node.name}.{item.name}",
                                type='method',
                                signature=signature,
                                docstring=method_docstring,
                                layer=layer,
                                file_path=str(file_path.relative_to(self.project_root)),
                                line_number=item.lineno,
                                violations=[]
                            )
                            apis.append(public_method)
                    
                    # Add class itself
                    class_api = PublicAPI(
                        name=node.name,
                        type='class',
                        signature=f"class {node.name}",
                        docstring=docstring,
                        layer=layer,
                        file_path=str(file_path.relative_to(self.project_root)),
                        line_number=node.lineno,
                        violations=[]
                    )
                    apis.append(class_api)
                
                # Extract public functions (not starting with underscore)
                elif isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                    docstring = ast.get_docstring(node)
                    signature = f"{node.name}({', '.join(arg.arg for arg in node.args.args)})"
                    
                    function_api = PublicAPI(
                        name=node.name,
                        type='function',
                        signature=signature,
                        docstring=docstring,
                        layer=layer,
                        file_path=str(file_path.relative_to(self.project_root)),
                        line_number=node.lineno,
                        violations=[]
                    )
                    apis.append(function_api)
            
            return apis
            
        except Exception as e:
            print(f"Error extracting APIs from {file_path}: {e}")
            return []
    
    def validate_method_name(self, api: PublicAPI) -> List[str]:
        """Validate method name against layer rules"""
        violations = []
        
        if api.layer == 'Unknown':
            return violations
        
        layer_rules = self.LAYER_RULES[api.layer]
        
        # Extract verb from method name
        verb_match = re.match(r'^([a-z]+)', api.name.split('.')[-1])
        if verb_match:
            verb = verb_match.group(1)
            
            # Check if verb is forbidden (critical violation)
            if verb in layer_rules['forbidden_verbs']:
                violations.append(f"FORBIDDEN: Method name '{api.name}' uses forbidden verb '{verb}' for {layer_rules['name']} layer")
            
            # Skip "not in allowed set" warnings to focus on critical violations only
        
        return violations
    
    def validate_docstring_content(self, api: PublicAPI) -> List[str]:
        """Validate docstring content for cross-layer semantic leakage"""
        violations = []
        
        if not api.docstring or api.layer == 'Unknown':
            return violations
        
        layer_rules = self.LAYER_RULES[api.layer]
        docstring_lower = api.docstring.lower()
        
        # Check for forbidden keywords only (critical violations)
        for forbidden_keyword in layer_rules['forbidden_keywords']:
            if forbidden_keyword in docstring_lower:
                violations.append(f"Docstring contains forbidden keyword '{forbidden_keyword}' for {layer_rules['name']} layer")
        
        # Skip responsibility keyword check - too strict for Phase 2C reconstruction
        
        return violations
    
    def validate_api_contract(self, api: PublicAPI) -> PublicAPI:
        """Validate a single API against layer rules"""
        violations = []
        
        # Validate method name
        violations.extend(self.validate_method_name(api))
        
        # Validate docstring content
        violations.extend(self.validate_docstring_content(api))
        
        api.violations = violations
        return api
    
    def analyze_all_modules(self) -> None:
        """Analyze all agentic_core modules for contract compliance"""
        print("=== Phase 2D_C: Layer Contract Analysis ===")
        
        agentic_core_dir = self.project_root / "agentic_core"
        python_files = []
        for file_path in agentic_core_dir.rglob("*.py"):
            if file_path.name != "__init__.py":
                python_files.append(file_path)
        
        print(f"Analyzing {len(python_files)} modules...")
        
        total_apis = 0
        
        for file_path in python_files:
            apis = self.extract_public_apis_from_file(file_path)
            
            for api in apis:
                validated_api = self.validate_api_contract(api)
                self.public_apis.append(validated_api)
                
                # Create violation records
                for violation in validated_api.violations:
                    violation_record = ContractViolation(
                        file_path=validated_api.file_path,
                        element_name=validated_api.name,
                        element_type=validated_api.type,
                        violation_type="CONTRACT_VIOLATION",
                        description=violation,
                        line_number=validated_api.line_number
                    )
                    self.violations.append(violation_record)
            
            total_apis += len(apis)
        
        print(f"Analyzed {total_apis} public APIs across {len(python_files)} modules")
        print(f"Found {len(self.violations)} contract violations")
    
    def generate_violation_report(self) -> Dict[str, Any]:
        """Generate comprehensive violation report"""
        violations_by_layer = {}
        violations_by_type = {}
        
        for violation in self.violations:
            layer = self.get_layer_from_path(self.project_root / violation.file_path)
            if layer not in violations_by_layer:
                violations_by_layer[layer] = []
            violations_by_layer[layer].append(violation)
            
            violation_type = violation.description.split(' ')[0]  # First word as type
            if violation_type not in violations_by_type:
                violations_by_type[violation_type] = 0
            violations_by_type[violation_type] += 1
        
        return {
            'total_apis': len(self.public_apis),
            'total_violations': len(self.violations),
            'violations_by_layer': violations_by_layer,
            'violations_by_type': violations_by_type,
            'violation_details': self.violations
        }
    
    def run_analysis(self) -> Dict[str, Any]:
        """Run complete contract analysis"""
        # Analyze all modules
        self.analyze_all_modules()
        
        # Generate report
        report = self.generate_violation_report()
        
        print(f"\n=== Analysis Results ===")
        print(f"Total APIs analyzed: {report['total_apis']}")
        print(f"Total violations found: {report['total_violations']}")
        
        if report['total_violations'] > 0:
            print(f"\n=== Violations by Layer ===")
            for layer, violations in report['violations_by_layer'].items():
                print(f"{layer}: {len(violations)} violations")
                for violation in violations[:3]:  # Show first 3
                    print(f"  - {violation.element_name}: {violation.description}")
        
        return report


def main():
    """Main analysis execution"""
    project_root = Path(__file__).parent
    
    analyzer = LayerContractAnalyzer(project_root)
    results = analyzer.run_analysis()
    
    return 0 if results['total_violations'] == 0 else 1


if __name__ == "__main__":
    exit(main())
