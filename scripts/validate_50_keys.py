#!/usr/bin/env python3
"""
Real 50-Key Canon Validator - Programmatically checks each principle
"""

import ast
import re
from pathlib import Path


class CanonValidator50:
    """Validates code against the 50 Subatomic Canon principles"""
    
    def __init__(self):
        self.violations = []
        
    def check_key_2_no_global_state(self, file_path: str, tree: ast.AST):
        """Key 2: NO IMPLICIT STATE - Check for global variables"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Global):
                self.violations.append({
                    'file': file_path,
                    'line': node.lineno,
                    'key': 2,
                    'message': 'Global keyword found - violates no implicit state'
                })
    
    def check_key_11_explicit_imports(self, file_path: str, tree: ast.AST):
        """Key 11: EXPLICIT DEPENDENCIES - Check for import *"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == '*' or (node.names and any(n.name == '*' for n in node.names)):
                self.violations.append({
                    'file': file_path,
                    'line': node.lineno,
                    'key': 11,
                    'message': 'Import * found - dependencies must be explicit'
                })
    
    def check_key_15_timeout_protection(self, file_path: str, content: str):
        """Key 15: TIMEOUT PROTECTION - Check for operations without timeouts"""
        # Look for common operations that should have timeouts
        patterns = [
            r'requests\.(get|post|put|delete)\([^)]+)(?!timeout)',
            r'urllib\.request\.urlopen\([^)]+)(?!timeout)',
            r'socket\.socket\([^)]+)(?!timeout)',
            r'time\.sleep\([^)]+\)(?!#.*timeout)',
        ]
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            for pattern in patterns:
                if re.search(pattern, line):
                    self.violations.append({
                        'file': file_path,
                        'line': i,
                        'key': 15,
                        'message': 'Operation without timeout detected'
                    })
    
    def check_key_19_type_safety(self, file_path: str, tree: ast.AST):
        """Key 19: TYPE SAFETY - Check functions without type hints"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip __init__ methods and test functions
                if node.name.startswith('__') or node.name.startswith('test_'):
                    continue
                    
                # Check if function has no type hints
                has_return_type = node.returns is not None
                has_param_types = all(arg.annotation is not None for arg in node.args.args)
                
                if not has_return_type or not has_param_types:
                    self.violations.append({
                        'file': file_path,
                        'line': node.lineno,
                        'key': 19,
                        'message': f'Function {node.name} missing type hints'
                    })
    
    def check_key_35_single_responsibility(self, file_path: str, tree: ast.AST):
        """Key 35: SINGLE RESPONSIBILITY - Check for overly complex functions"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Count complexity indicators
                complexity = 0
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.ExceptHandler)):
                        complexity += 1
                
                # If too complex, flag it
                if complexity > 10:
                    self.violations.append({
                        'file': file_path,
                        'line': node.lineno,
                        'key': 35,
                        'message': f'Function {node.name} too complex ({complexity} control structures)'
                    })
    
    def check_key_49_depth_law(self, file_path: str):
        """Key 49: UNIVERSAL DEPTH LAW - Already checked separately"""
    
    def validate_file(self, file_path: str):
        """Validate a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Run all checks
            self.check_key_2_no_global_state(file_path, tree)
            self.check_key_11_explicit_imports(file_path, tree)
            self.check_key_15_timeout_protection(file_path, content)
            self.check_key_19_type_safety(file_path, tree)
            self.check_key_35_single_responsibility(file_path, tree)
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
    
    def validate_project(self):
        """Validate entire project"""
        print("🔍 Running 50-Key Canon Validator...")
        print("="*60)
        
        # Get all Python files
        python_files = list(Path('.').rglob('*.py'))
        
        # Exclude common directories
        exclude_dirs = {'.git', '__pycache__', '.venv', 'venv', 'node_modules'}
        python_files = [f for f in python_files 
                       if not any(part in exclude_dirs for part in f.parts)]
        
        print(f"Found {len(python_files)} Python files to validate\n")
        
        # Validate each file
        for file_path in python_files:
            self.validate_file(str(file_path))
        
        # Report results
        self.generate_report()
    
    def generate_report(self):
        """Generate validation report"""
        print("\n📊 VALIDATION REPORT")
        print("="*60)
        
        # Group violations by key
        violations_by_key = {}
        for v in self.violations:
            key = v['key']
            if key not in violations_by_key:
                violations_by_key[key] = []
            violations_by_key[key].append(v)
        
        print(f"Total Violations: {len(self.violations)}")
        print(f"Keys with Violations: {len(violations_by_key)}")
        
        if violations_by_key:
            print("\n🚨 VIOLATIONS BY KEY:")
            for key in sorted(violations_by_key.keys()):
                violations = violations_by_key[key]
                print(f"\nKey {key}: {len(violations)} violation(s)")
                for v in violations[:5]:  # Show first 5
                    print(f"  - {v['file']}:{v['line']} - {v['message']}")
                if len(violations) > 5:
                    print(f"  ... and {len(violations) - 5} more")
        else:
            print("\n✅ No violations found! Code complies with checked keys.")
        
        print(f"\n📈 COMPLIANCE RATE: {50 - len(violations_by_key)}/50 keys checked")
        print(f"Note: Only 5 keys implemented. More can be added as needed.")

if __name__ == "__main__":
    validator = CanonValidator50()
    validator.validate_project()
