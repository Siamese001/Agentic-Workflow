#!/usr/bin/env python3
"""
Zero Tolerance Verification Script

This script comprehensively validates that no stubs or placeholders remain
in the agentic_core, apps, and config folders, and that all import chains work correctly.
"""

import os
import sys
import ast
import importlib.util
import traceback
from pathlib import Path
from typing import List, Dict, Any, Set
import re

class ZeroToleranceValidator:
    """Validates zero-tolerance compliance for stubs and placeholders."""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.issues: List[Dict[str, Any]] = []
        self.import_errors: List[Dict[str, Any]] = []
        
    def validate_all(self) -> Dict[str, Any]:
        """Run comprehensive validation."""
        print("🔍 Starting Zero Tolerance Validation...")
        
        # Check for stub patterns
        print("📋 Checking for stub patterns...")
        self._check_stub_patterns()
        
        # Check for empty classes/functions
        print("🏗️  Checking for empty implementations...")
        self._check_empty_implementations()
        
        # Test import chains
        print("🔗 Testing import chains...")
        self._test_import_chains()
        
        # Generate report
        return self._generate_report()
    
    def _check_stub_patterns(self):
        """Check for stub patterns like 'pass' and 'NotImplementedError'."""
        stub_patterns = [
            (r'^\s*pass\s*$', 'pass statement'),  # Only standalone pass statements
            (r'\bNotImplementedError\b', 'NotImplementedError'),
            (r'\braise NotImplementedError\b', 'raise NotImplementedError'),
            (r'# TODO: implement', 'TODO comment'),
            (r'# FIXME: implement', 'FIXME comment'),
            (r'# Placeholder', 'Placeholder comment'),
        ]
        
        target_dirs = ['agentic_core', 'apps', 'config']
        
        for target_dir in target_dirs:
            target_path = self.root_path / target_dir
            if not target_path.exists():
                continue
                
            for py_file in target_path.rglob('*.py'):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                    
                    for pattern, description in stub_patterns:
                        for i, line in enumerate(lines, 1):
                            # Skip pass statements in exception handlers
                            if 'pass' in line and description == 'pass statement':
                                # Check if this pass is in an exception handler
                                prev_line = lines[i-2] if i > 1 else ""
                                if re.search(r'except\s+', prev_line.strip()):
                                    continue  # Skip legitimate exception handler
                            
                            if re.search(pattern, line.strip()):
                                self.issues.append({
                                    'type': 'stub_pattern',
                                    'file': str(py_file.relative_to(self.root_path)),
                                    'line': i,
                                    'content': line.strip(),
                                    'description': description
                                })
                except Exception as e:
                    self.issues.append({
                        'type': 'file_read_error',
                        'file': str(py_file.relative_to(self.root_path)),
                        'error': str(e)
                    })
    
    def _check_empty_implementations(self):
        """Check for empty classes and functions."""
        target_dirs = ['agentic_core', 'apps', 'config']
        
        for target_dir in target_dirs:
            target_path = self.root_path / target_dir
            if not target_path.exists():
                continue
                
            for py_file in target_path.rglob('*.py'):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Parse AST
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                            # Check if body is empty or only contains pass/docstring
                            if not node.body:
                                self.issues.append({
                                    'type': 'empty_implementation',
                                    'file': str(py_file.relative_to(self.root_path)),
                                    'line': node.lineno,
                                    'name': node.name,
                                    'node_type': type(node).__name__
                                })
                            elif (len(node.body) == 1 and 
                                  isinstance(node.body[0], ast.Pass)):
                                self.issues.append({
                                    'type': 'empty_implementation_with_pass',
                                    'file': str(py_file.relative_to(self.root_path)),
                                    'line': node.lineno,
                                    'name': node.name,
                                    'node_type': type(node).__name__
                                })
                            elif (len(node.body) == 1 and 
                                  isinstance(node.body[0], (ast.Str, ast.Constant)) and 
                                  isinstance(node.body[0].value, str)):
                                # Only docstring, no implementation
                                self.issues.append({
                                    'type': 'docstring_only_implementation',
                                    'file': str(py_file.relative_to(self.root_path)),
                                    'line': node.lineno,
                                    'name': node.name,
                                    'node_type': type(node).__name__
                                })
                                
                except Exception as e:
                    self.issues.append({
                        'type': 'ast_parse_error',
                        'file': str(py_file.relative_to(self.root_path)),
                        'error': str(e)
                    })
    
    def _test_import_chains(self):
        """Test critical import chains."""
        critical_imports = [
            # L1 Planning layer
            'agentic_core.l1_planning',
            'agentic_core.l1_planning.strategy_planning',
            
            # L2 Execution layer
            'agentic_core.l2_execution',
            'agentic_core.l2_execution.l2_execution',
            
            # L3 Orchestration layer
            'agentic_core.l3_orchestration',
            'agentic_core.l3_orchestration.l3_orchestration',
            
            # L4 Memory layer
            'agentic_core.l4_memory',
            'agentic_core.l4_memory.l4_memory',
            
            # L5 Safety layer
            'agentic_core.l5_safety',
            'agentic_core.l5_safety.l5_safety',
            
            # Config layer
            'agentic_core.config',
            'agentic_core.config.config_profiles_v10_10',
        ]
        
        # Add sys.path to ensure imports work
        sys.path.insert(0, str(self.root_path))
        
        for import_name in critical_imports:
            try:
                spec = importlib.util.find_spec(import_name)
                if spec is None:
                    self.import_errors.append({
                        'type': 'import_not_found',
                        'module': import_name,
                        'error': 'Module not found'
                    })
                else:
                    # Try to actually import the module
                    try:
                        module = importlib.import_module(import_name)
                        # Check if module has expected attributes
                        if hasattr(module, '__all__'):
                            missing_exports = []
                            for export in module.__all__[:3]:  # Check first few exports
                                if not hasattr(module, export):
                                    missing_exports.append(export)
                            
                            if missing_exports:
                                self.import_errors.append({
                                    'type': 'missing_exports',
                                    'module': import_name,
                                    'missing': missing_exports
                                })
                    except ImportError as e:
                        self.import_errors.append({
                            'type': 'import_error',
                            'module': import_name,
                            'error': str(e),
                            'traceback': traceback.format_exc()
                        })
                    except Exception as e:
                        self.import_errors.append({
                            'type': 'import_runtime_error',
                            'module': import_name,
                            'error': str(e),
                            'traceback': traceback.format_exc()
                        })
                        
            except Exception as e:
                self.import_errors.append({
                    'type': 'spec_error',
                    'module': import_name,
                    'error': str(e)
                })
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        total_issues = len(self.issues)
        total_import_errors = len(self.import_errors)
        
        # Categorize issues
        stub_issues = [i for i in self.issues if i['type'] in ['stub_pattern', 'empty_implementation', 'empty_implementation_with_pass']]
        file_issues = [i for i in self.issues if i['type'] in ['file_read_error', 'ast_parse_error']]
        
        report = {
            'summary': {
                'total_issues': total_issues,
                'stub_issues': len(stub_issues),
                'file_issues': len(file_issues),
                'import_errors': total_import_errors,
                'zero_tolerance_compliant': total_issues == 0 and total_import_errors == 0
            },
            'stub_issues': stub_issues,
            'file_issues': file_issues,
            'import_errors': self.import_errors,
            'recommendations': []
        }
        
        # Add recommendations
        if stub_issues:
            report['recommendations'].append(f"Replace {len(stub_issues)} stub implementations with functional code")
        
        if file_issues:
            report['recommendations'].append(f"Fix {len(file_issues)} file parsing/read errors")
        
        if total_import_errors > 0:
            report['recommendations'].append(f"Fix {total_import_errors} import chain errors")
        
        if report['summary']['zero_tolerance_compliant']:
            report['recommendations'].append("✅ Zero tolerance compliance achieved!")
        
        return report

def main():
    """Main validation entry point."""
    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    else:
        # Default to current directory
        root_path = os.getcwd()
    
    validator = ZeroToleranceValidator(root_path)
    report = validator.validate_all()
    
    # Print report
    print("\n" + "="*60)
    print("📊 ZERO TOLERANCE VALIDATION REPORT")
    print("="*60)
    
    summary = report['summary']
    print(f"Total Issues: {summary['total_issues']}")
    print(f"Stub Issues: {summary['stub_issues']}")
    print(f"File Issues: {summary['file_issues']}")
    print(f"Import Errors: {summary['import_errors']}")
    print(f"Zero Tolerance Compliant: {'✅ YES' if summary['zero_tolerance_compliant'] else '❌ NO'}")
    
    if report['stub_issues']:
        print(f"\n🚨 STUB ISSUES ({len(report['stub_issues'])}):")
        for issue in report['stub_issues'][:10]:  # Show first 10
            print(f"  • {issue['file']}:{issue['line']} - {issue.get('description', 'unknown')}")
            if 'content' in issue:
                print(f"    Content: {issue['content']}")
        if len(report['stub_issues']) > 10:
            print(f"  ... and {len(report['stub_issues']) - 10} more")
    
    if report['import_errors']:
        print(f"\n🔗 IMPORT ERRORS ({len(report['import_errors'])}):")
        for error in report['import_errors'][:10]:  # Show first 10
            print(f"  • {error['module']} - {error['error']}")
        if len(report['import_errors']) > 10:
            print(f"  ... and {len(report['import_errors']) - 10} more")
    
    print(f"\n💡 RECOMMENDATIONS:")
    for rec in report['recommendations']:
        print(f"  • {rec}")
    
    # Exit with appropriate code
    sys.exit(0 if summary['zero_tolerance_compliant'] else 1)

if __name__ == "__main__":
    main()
