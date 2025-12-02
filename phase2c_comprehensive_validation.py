#!/usr/bin/env python3
"""
Phase 2C Comprehensive Validation Script

Validates all Phase 2C reconstruction requirements:
- Semantic cache usage verification
- File count and structure validation
- Syntax validation (py_compile)
- Import validation
- TODO/placeholder detection
- Missing helper method detection
- Exception class validation
- L1-L5 layer responsibility enforcement
"""

import ast
import py_compile
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any


class Phase2CValidator:
    """Comprehensive validator for Phase 2C reconstruction"""
    
    def __init__(self, project_root: Path, cache_dir: Path):
        self.project_root = project_root
        self.cache_dir = cache_dir
        self.validation_results = {}
        
    def get_all_agentic_files(self) -> List[Path]:
        """Get all agentic_core Python files (excluding __init__.py)"""
        agentic_core_dir = self.project_root / "agentic_core"
        files = []
        for file_path in agentic_core_dir.rglob("*.py"):
            if file_path.name != "__init__.py":
                files.append(file_path)
        return files
    
    def validate_file_count(self) -> Dict[str, Any]:
        """Validate exactly 96 files exist"""
        files = self.get_all_agentic_files()
        return {
            'expected': 96,
            'actual': len(files),
            'valid': len(files) == 96,
            'files': [f.relative_to(self.project_root) for f in files]
        }
    
    def validate_semantic_cache_usage(self) -> Dict[str, Any]:
        """Validate semantic cache exists and contains expected entries"""
        cache_files = list(self.cache_dir.glob("agentic_core_*.meta.json"))
        
        # Load a few cache entries to verify structure
        sample_entries = []
        for cache_file in cache_files[:5]:  # Sample first 5
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    entry = json.load(f)
                    sample_entries.append({
                        'file_path': entry.get('file_path'),
                        'has_signature_map': 'signature_map' in entry,
                        'has_ast_tree': 'ast_tree' in entry,
                        'has_responsibility_tags': 'responsibility_tags' in entry,
                        'responsibility_tags': entry.get('responsibility_tags', [])
                    })
            except Exception as e:
                sample_entries.append({'error': str(e)})
        
        return {
            'cache_files_found': len(cache_files),
            'expected_entries': 96,
            'valid': len(cache_files) >= 96,  # At least 96 entries
            'sample_entries': sample_entries
        }
    
    def validate_syntax(self) -> Dict[str, Any]:
        """Validate all files compile without syntax errors"""
        files = self.get_all_agentic_files()
        valid_files = []
        invalid_files = []
        
        for file_path in files:
            try:
                py_compile.compile(str(file_path), doraise=True)
                valid_files.append(file_path.relative_to(self.project_root))
            except py_compile.PyCompileError as e:
                invalid_files.append({
                    'file': file_path.relative_to(self.project_root),
                    'error': str(e)
                })
        
        return {
            'total_files': len(files),
            'valid_files': len(valid_files),
            'invalid_files': len(invalid_files),
            'valid': len(invalid_files) == 0,
            'invalid_details': invalid_files
        }
    
    def validate_importability(self) -> Dict[str, Any]:
        """Validate agentic_core can be imported"""
        try:
            import agentic_core
            return {
                'valid': True,
                'message': 'agentic_core imports successfully'
            }
        except Exception as e:
            return {
                'valid': False,
                'message': f'Import failed: {e}'
            }
    
    def validate_no_placeholders(self) -> Dict[str, Any]:
        """Check for TODOs, pass statements, and other placeholders"""
        files = self.get_all_agentic_files()
        files_with_issues = []
        
        placeholder_patterns = [
            (r'TODO', 'TODO comment found'),
            (r'todo', 'todo comment found'),
            (r'FIXME', 'FIXME comment found'),
            (r'NotImplemented', 'NotImplemented found'),
            (r'raise NotImplementedError', 'NotImplementedError found')
        ]
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                issues = []
                for pattern, message in placeholder_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        issues.append({
                            'type': message,
                            'line': line_num,
                            'content': match.group()
                        })
                
                # Check for 'pass' statements that might be placeholders
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if line.strip() == 'pass':
                        # Check if it's in a function/class (likely placeholder)
                        if i > 1:
                            prev_line = lines[i-2].strip()
                            if prev_line.startswith('def ') or prev_line.startswith('class '):
                                issues.append({
                                    'type': 'Placeholder pass statement',
                                    'line': i,
                                    'content': 'pass'
                                })
                
                if issues:
                    files_with_issues.append({
                        'file': file_path.relative_to(self.project_root),
                        'issues': issues
                    })
                    
            except Exception as e:
                files_with_issues.append({
                    'file': file_path.relative_to(self.project_root),
                    'error': str(e)
                })
        
        return {
            'total_files': len(files),
            'files_with_issues': len(files_with_issues),
            'valid': len(files_with_issues) == 0,
            'issue_details': files_with_issues
        }
    
    def validate_helper_methods(self) -> Dict[str, Any]:
        """Check for missing helper methods in generated code"""
        files = self.get_all_agentic_files()
        files_with_missing_methods = []
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find all self._method_name() calls
                method_calls = re.findall(r'self\._([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', content)
                called_methods = set(f"_{method}" for method in method_calls)
                
                # Parse AST to find defined methods
                tree = ast.parse(content)
                defined_methods = set()
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        defined_methods.add(node.name)
                
                # Find missing methods
                missing_methods = called_methods - defined_methods
                
                if missing_methods:
                    files_with_missing_methods.append({
                        'file': file_path.relative_to(self.project_root),
                        'missing_methods': sorted(list(missing_methods)),
                        'called_methods': sorted(list(called_methods)),
                        'defined_methods': sorted(list(defined_methods))
                    })
                    
            except Exception as e:
                files_with_missing_methods.append({
                    'file': file_path.relative_to(self.project_root),
                    'error': str(e)
                })
        
        return {
            'total_files': len(files),
            'files_with_missing_methods': len(files_with_missing_methods),
            'valid': len(files_with_missing_methods) == 0,
            'missing_method_details': files_with_missing_methods
        }
    
    def validate_exception_classes(self) -> Dict[str, Any]:
        """Validate exception class names are valid Python identifiers"""
        files = self.get_all_agentic_files()
        invalid_classes = []
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find exception class definitions
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check if it's an exception class
                        if any(base.id == 'Exception' for base in node.bases if isinstance(base, ast.Name)):
                            class_name = node.name
                            
                            # Check for invalid characters
                            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', class_name):
                                invalid_classes.append({
                                    'file': file_path.relative_to(self.project_root),
                                    'class_name': class_name,
                                    'line': node.lineno
                                })
                            
            except Exception as e:
                invalid_classes.append({
                    'file': file_path.relative_to(self.project_root),
                    'error': str(e)
                })
        
        return {
            'total_files': len(files),
            'invalid_classes': len(invalid_classes),
            'valid': len(invalid_classes) == 0,
            'invalid_class_details': invalid_classes
        }
    
    def validate_layer_responsibilities(self) -> Dict[str, Any]:
        """Validate L1-L5 layer responsibilities are enforced"""
        files = self.get_all_agentic_files()
        layer_violations = []
        
        layer_patterns = {
            'plan-layer': ['L1 Cognitive Planning Layer'],
            'exec-layer': ['L2 Execution Layer'], 
            'orc-layer': ['L3 Orchestration Layer'],
            'mem-layer': ['L4 Memory Layer'],
            'safe-layer': ['L5 Safety/Policy Layer']
        }
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Determine expected layer from path
                path_str = str(file_path).lower()
                expected_layer_patterns = None
                for layer_dir, layer_identifiers in layer_patterns.items():
                    if layer_dir in path_str:
                        expected_layer_patterns = layer_identifiers
                        break
                
                if expected_layer_patterns:
                    # Check for layer-specific patterns in docstrings
                    found_layer = False
                    for layer_identifier in expected_layer_patterns:
                        if layer_identifier in content:
                            found_layer = True
                            break
                    
                    if not found_layer:
                        layer_violations.append({
                            'file': file_path.relative_to(self.project_root),
                            'expected_patterns': expected_layer_patterns,
                            'issue': 'Layer responsibility not found in content'
                        })
                        
            except Exception as e:
                layer_violations.append({
                    'file': file_path.relative_to(self.project_root),
                    'error': str(e)
                })
        
        return {
            'total_files': len(files),
            'layer_violations': len(layer_violations),
            'valid': len(layer_violations) == 0,
            'violation_details': layer_violations
        }
    
    def validate_cross_layer_imports(self) -> Dict[str, Any]:
        """Validate no cross-layer import violations"""
        files = self.get_all_agentic_files()
        import_violations = []
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Determine current layer
                path_str = str(file_path).lower()
                current_layer = None
                for layer_dir in ['plan-layer', 'exec-layer', 'orc-layer', 'mem-layer', 'safe-layer']:
                    if layer_dir in path_str:
                        current_layer = layer_dir
                        break
                
                if current_layer:
                    # Find imports from other layers
                    import_pattern = r'from agentic_core\.([a-z-]+)'
                    imports = re.findall(import_pattern, content)
                    
                    for imported_layer in imports:
                        if imported_layer != current_layer.replace('-', '') and imported_layer in ['plan', 'exec', 'orc', 'mem', 'safe']:
                            import_violations.append({
                                'file': file_path.relative_to(self.project_root),
                                'current_layer': current_layer,
                                'imported_layer': imported_layer,
                                'issue': 'Cross-layer import detected'
                            })
                            
            except Exception as e:
                import_violations.append({
                    'file': file_path.relative_to(self.project_root),
                    'error': str(e)
                })
        
        return {
            'total_files': len(files),
            'import_violations': len(import_violations),
            'valid': len(import_violations) == 0,
            'violation_details': import_violations
        }
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run all validation checks"""
        print("=== Phase 2C Comprehensive Validation ===")
        
        validations = {
            'file_count': self.validate_file_count(),
            'semantic_cache_usage': self.validate_semantic_cache_usage(),
            'syntax_validation': self.validate_syntax(),
            'import_validation': self.validate_importability(),
            'placeholder_check': self.validate_no_placeholders(),
            'helper_method_validation': self.validate_helper_methods(),
            'exception_class_validation': self.validate_exception_classes(),
            'layer_responsibility_validation': self.validate_layer_responsibilities(),
            'cross_layer_import_validation': self.validate_cross_layer_imports()
        }
        
        # Calculate overall status
        all_valid = all(result['valid'] for result in validations.values())
        
        print(f"\n=== Validation Summary ===")
        print(f"Overall Status: {'✅ PASS' if all_valid else '❌ FAIL'}")
        
        for check_name, result in validations.items():
            status = '✅ PASS' if result['valid'] else '❌ FAIL'
            print(f"{check_name}: {status}")
            
            if not result['valid']:
                if 'violation_details' in result:
                    print(f"  Issues: {len(result['violation_details'])}")
                    # Show first few violations for debugging
                    for i, violation in enumerate(result['violation_details'][:3]):
                        print(f"    {i+1}. {violation.get('file', 'unknown')}: {violation.get('issue', 'unknown')}")
                elif 'invalid_details' in result:
                    print(f"  Issues: {len(result['invalid_details'])}")
                elif 'files_with_issues' in result:
                    print(f"  Issues: {len(result['files_with_issues'])}")
                elif 'missing_method_details' in result:
                    print(f"  Issues: {len(result['missing_method_details'])}")
        
        return {
            'overall_valid': all_valid,
            'individual_validations': validations
        }


def main():
    """Main validation execution"""
    project_root = Path(__file__).parent
    cache_dir = Path("C:\\Git\\.windsurf_cache\\semantic")
    
    validator = Phase2CValidator(project_root, cache_dir)
    results = validator.run_comprehensive_validation()
    
    return 0 if results['overall_valid'] else 1


if __name__ == "__main__":
    exit(main())
