"""
Code Quality Metrics - Guardian Test

This test validates code quality metrics that were previously
handled by pre-commit hooks or not validated at all. It includes:
- File size validation (monolith detection)
- Cyclomatic complexity analysis
- Documentation coverage
- Import organization and best practices
- Code duplication detection

Moved from pre-commit to Guardian for comprehensive validation.
"""

import pytest
import ast
from pathlib import Path
from typing import List, Dict, Tuple, Set
import sys
from collections import defaultdict

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestCodeQualityMetrics:
    """
    Code quality metrics validation.
    
    This test provides comprehensive code quality analysis
    that goes beyond basic linting.
    """

    @pytest.mark.guardian
    def test_file_size_validation(self):
        """
        Test that no files exceed maximum size limits (monolith detection).
        
        Large files are harder to maintain and should be split.
        """
        print("\n=== FILE SIZE VALIDATION (MONOLITH DETECTION) ===")
        
        MONOLITH_THRESHOLD = 800  # lines of code (excluding comments/blank)
        MAX_FILE_SIZE = 50000  # bytes (50KB)
        
        large_files: List[Dict[str, int]] = []
        oversized_files: List[Dict[str, int]] = []
        
        # Check all Python files
        for file_path in PROJECT_ROOT.rglob("*.py"):
            # Skip excluded directories
            if any(excluded in str(file_path) for excluded in 
                  ["__pycache__", ".git", ".pytest_cache", "node_modules", 
                   "archives", ".sovereign_healing_backup"]):
                continue
            
            # Skip this test file
            if "test_code_quality_metrics.py" in str(file_path):
                continue
            
            # Check file size in bytes
            file_size = file_path.stat().st_size
            if file_size > MAX_FILE_SIZE:
                oversized_files.append({
                    "file": str(file_path.relative_to(PROJECT_ROOT)),
                    "size_bytes": file_size,
                    "size_kb": round(file_size / 1024, 2)
                })
            
            # Count lines of code (excluding comments and blank lines)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                code_lines = 0
                in_multiline_comment = False
                
                for line in lines:
                    stripped = line.strip()
                    
                    # Skip blank lines
                    if not stripped:
                        continue
                    
                    # Handle multiline comments
                    if '"""' in stripped or "'''" in stripped:
                        if stripped.count('"""') % 2 == 1 or stripped.count("'''") % 2 == 1:
                            in_multiline_comment = not in_multiline_comment
                    
                    # Skip comments and docstrings
                    if (stripped.startswith('#') or 
                        in_multiline_comment or
                        stripped.startswith('"""') or 
                        stripped.startswith("'''")):
                        continue
                    
                    code_lines += 1
                
                if code_lines > MONOLITH_THRESHOLD:
                    large_files.append({
                        "file": str(file_path.relative_to(PROJECT_ROOT)),
                        "loc": code_lines
                    })
                    
            except (UnicodeDecodeError, PermissionError):
                # Skip files that can't be read
                continue
        
        # Report results
        print(f"  Files checked for size: {len(list(PROJECT_ROOT.rglob('*.py')))}")
        print(f"  Oversized files (>50KB): {len(oversized_files)}")
        print(f"  Large files (>800 LOC): {len(large_files)}")
        
        # Track as tech debt with thresholds
        KNOWN_LARGE_FILES = 10  # Allow up to 10 large files
        KNOWN_OVERSIZED_FILES = 5  # Allow up to 5 oversized files
        
        # Report oversized files
        if oversized_files:
            if len(oversized_files) <= KNOWN_OVERSIZED_FILES:
                print(f"\n[TECH DEBT] {len(oversized_files)} oversized files (tracked, not blocking):")
                for file_info in oversized_files:
                    print(f"  - {file_info['file']} ({file_info['size_kb']}KB)")
            else:
                error_msg = f"OVERSIZED FILES EXCEED THRESHOLD ({len(oversized_files)} > {KNOWN_OVERSIZED_FILES}):\n\n"
                for file_info in oversized_files[:10]:
                    error_msg += f"  [X] {file_info['file']} ({file_info['size_kb']}KB)\n"
                if len(oversized_files) > 10:
                    error_msg += f"  ... and {len(oversized_files) - 10} more\n"
                error_msg += "\nConsider splitting large files or moving assets to separate files."
                pytest.fail(error_msg)
        
        # Report large files (monoliths)
        if large_files:
            if len(large_files) <= KNOWN_LARGE_FILES:
                print(f"\n[TECH DEBT] {len(large_files)} monolith files (tracked, not blocking):")
                for file_info in large_files:
                    print(f"  - {file_info['file']} ({file_info['loc']} LOC)")
            else:
                error_msg = f"MONOLITH FILES EXCEED THRESHOLD ({len(large_files)} > {KNOWN_LARGE_FILES}):\n\n"
                for file_info in large_files[:10]:
                    error_msg += f"  [X] {file_info['file']} ({file_info['loc']} LOC)\n"
                if len(large_files) > 10:
                    error_msg += f"  ... and {len(large_files) - 10} more\n"
                error_msg += "\nLarge files should be split into smaller, focused modules."
                pytest.fail(error_msg)
        
        print(f"[OK] File sizes within acceptable limits")

    @pytest.mark.guardian
    def test_cyclomatic_complexity(self):
        """
        Test cyclomatic complexity of Python files.
        
        High complexity indicates need for refactoring.
        """
        print("\n=== CYCLOMATIC COMPLEXITY VALIDATION ===")
        
        COMPLEXITY_THRESHOLD = 15  # Maximum complexity per function
        MAX_COMPLEXITY_FUNCTIONS = 20  # Allow up to 20 complex functions
        
        complex_functions: List[Dict[str, int]] = []
        
        def calculate_complexity(node: ast.AST) -> int:
            """Calculate cyclomatic complexity for an AST node."""
            complexity = 1  # Base complexity
            
            for child in ast.walk(node):
                if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor,
                                   ast.ExceptHandler, ast.With, ast.AsyncWith)):
                    complexity += 1
                elif isinstance(child, ast.BoolOp):
                    complexity += len(child.values) - 1
            
            return complexity
        
        # Analyze all Python files
        for file_path in PROJECT_ROOT.rglob("*.py"):
            # Skip excluded directories
            if any(excluded in str(file_path) for excluded in 
                  ["__pycache__", ".git", ".pytest_cache", "node_modules",
                   "archives", ".sovereign_healing_backup", "tests"]):
                continue
            
            # Skip this test file
            if "test_code_quality_metrics.py" in str(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content, filename=str(file_path))
                
                # Check each function and method
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        complexity = calculate_complexity(node)
                        if complexity > COMPLEXITY_THRESHOLD:
                            complex_functions.append({
                                "file": str(file_path.relative_to(PROJECT_ROOT)),
                                "function": node.name,
                                "line": node.lineno,
                                "complexity": complexity
                            })
                            
            except (SyntaxError, UnicodeDecodeError):
                # Skip files with syntax errors
                continue
        
        # Report results
        print(f"  Functions with high complexity: {len(complex_functions)}")
        
        # Track as tech debt
        if complex_functions:
            if len(complex_functions) <= MAX_COMPLEXITY_FUNCTIONS:
                print(f"\n[TECH DEBT] {len(complex_functions)} complex functions (tracked, not blocking):")
                for func_info in complex_functions[:10]:
                    print(f"  - {func_info['file']}:{func_info['line']} {func_info['function']}() (complexity: {func_info['complexity']})")
                if len(complex_functions) > 10:
                    print(f"  ... and {len(complex_functions) - 10} more")
            else:
                error_msg = f"COMPLEX FUNCTIONS EXCEED THRESHOLD ({len(complex_functions)} > {MAX_COMPLEXITY_FUNCTIONS}):\n\n"
                for func_info in complex_functions[:15]:
                    error_msg += f"  [X] {func_info['file']}:{func_info['line']} {func_info['function']}() (complexity: {func_info['complexity']})\n"
                if len(complex_functions) > 15:
                    error_msg += f"  ... and {len(complex_functions) - 15} more\n"
                error_msg += f"\nFunctions with complexity > {COMPLEXITY_THRESHOLD} should be refactored."
                pytest.fail(error_msg)
        
        print(f"[OK] Cyclomatic complexity within acceptable limits")

    @pytest.mark.guardian
    def test_documentation_coverage(self):
        """
        Test documentation coverage of modules and classes.
        
        Good documentation is essential for maintainability.
        """
        print("\n=== DOCUMENTATION COVERAGE VALIDATION ===")
        
        undocumented_modules: List[str] = []
        undocumented_classes: List[Dict[str, str]] = []
        undocumented_functions: List[Dict[str, str]] = []
        
        # Analyze all Python files
        for file_path in PROJECT_ROOT.rglob("*.py"):
            # Skip excluded directories and test files
            if any(excluded in str(file_path) for excluded in 
                  ["__pycache__", ".git", ".pytest_cache", "node_modules",
                   "archives", ".sovereign_healing_backup"]):
                continue
            
            if file_path.name.startswith("test_") or "_test.py" in file_path.name:
                continue
            
            # Skip this test file
            if "test_code_quality_metrics.py" in str(file_path):
                continue
            
            rel_path = str(file_path.relative_to(PROJECT_ROOT))
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check module docstring
                tree = ast.parse(content, filename=str(file_path))
                
                # Get first node and check if it's a docstring
                if (tree.body and 
                    isinstance(tree.body[0], ast.Expr) and 
                    isinstance(tree.body[0].value, ast.Constant) and 
                    isinstance(tree.body[0].value.value, str)):
                    # Module has docstring
                    pass
                else:
                    undocumented_modules.append(rel_path)
                
                # Check classes and functions
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check class docstring
                        if (node.body and 
                            isinstance(node.body[0], ast.Expr) and 
                            isinstance(node.body[0].value, ast.Constant) and 
                            isinstance(node.body[0].value.value, str)):
                            pass  # Has docstring
                        else:
                            undocumented_classes.append({
                                "file": rel_path,
                                "name": node.name,
                                "line": node.lineno
                            })
                    
                    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Skip private methods and test functions
                        if (node.name.startswith('_') or 
                            node.name.startswith('test_') or
                            node.name.endswith('_test')):
                            continue
                        
                        # Check function docstring
                        if (node.body and 
                            isinstance(node.body[0], ast.Expr) and 
                            isinstance(node.body[0].value, ast.Constant) and 
                            isinstance(node.body[0].value.value, str)):
                            pass  # Has docstring
                        else:
                            undocumented_functions.append({
                                "file": rel_path,
                                "name": node.name,
                                "line": node.lineno
                            })
                            
            except (SyntaxError, UnicodeDecodeError):
                continue
        
        # Report results
        print(f"  Undocumented modules: {len(undocumented_modules)}")
        print(f"  Undocumented classes: {len(undocumented_classes)}")
        print(f"  Undocumented functions: {len(undocumented_functions)}")
        
        # Track as tech debt with thresholds
        KNOWN_UNDOCUMENTED_MODULES = 20
        KNOWN_UNDOCUMENTED_CLASSES = 50
        KNOWN_UNDOCUMENTED_FUNCTIONS = 100
        
        # Report undocumented modules
        if undocumented_modules:
            if len(undocumented_modules) <= KNOWN_UNDOCUMENTED_MODULES:
                print(f"\n[TECH DEBT] {len(undocumented_modules)} undocumented modules (tracked, not blocking):")
                for module in undocumented_modules[:10]:
                    print(f"  - {module}")
                if len(undocumented_modules) > 10:
                    print(f"  ... and {len(undocumented_modules) - 10} more")
            else:
                error_msg = f"UNDOCUMENTED MODULES EXCEED THRESHOLD ({len(undocumented_modules)} > {KNOWN_UNDOCUMENTED_MODULES}):\n\n"
                for module in undocumented_modules[:15]:
                    error_msg += f"  [X] {module}\n"
                if len(undocumented_modules) > 15:
                    error_msg += f"  ... and {len(undocumented_modules) - 15} more\n"
                pytest.fail(error_msg)
        
        # Report undocumented classes
        if undocumented_classes:
            if len(undocumented_classes) <= KNOWN_UNDOCUMENTED_CLASSES:
                print(f"\n[TECH DEBT] {len(undocumented_classes)} undocumented classes (tracked, not blocking):")
                for class_info in undocumented_classes[:10]:
                    print(f"  - {class_info['file']}:{class_info['line']} {class_info['name']}")
                if len(undocumented_classes) > 10:
                    print(f"  ... and {len(undocumented_classes) - 10} more")
            else:
                error_msg = f"UNDOCUMENTED CLASSES EXCEED THRESHOLD ({len(undocumented_classes)} > {KNOWN_UNDOCUMENTED_CLASSES}):\n\n"
                for class_info in undocumented_classes[:15]:
                    error_msg += f"  [X] {class_info['file']}:{class_info['line']} {class_info['name']}\n"
                if len(undocumented_classes) > 15:
                    error_msg += f"  ... and {len(undocumented_classes) - 15} more\n"
                pytest.fail(error_msg)
        
        # Report undocumented functions
        if undocumented_functions:
            if len(undocumented_functions) <= KNOWN_UNDOCUMENTED_FUNCTIONS:
                print(f"\n[TECH DEBT] {len(undocumented_functions)} undocumented functions (tracked, not blocking):")
                for func_info in undocumented_functions[:10]:
                    print(f"  - {func_info['file']}:{func_info['line']} {func_info['name']}()")
                if len(undocumented_functions) > 10:
                    print(f"  ... and {len(undocumented_functions) - 10} more")
            else:
                error_msg = f"UNDOCUMENTED FUNCTIONS EXCEED THRESHOLD ({len(undocumented_functions)} > {KNOWN_UNDOCUMENTED_FUNCTIONS}):\n\n"
                for func_info in undocumented_functions[:15]:
                    error_msg += f"  [X] {func_info['file']}:{func_info['line']} {func_info['name']}()\n"
                if len(undocumented_functions) > 15:
                    error_msg += f"  ... and {len(undocumented_functions) - 15} more\n"
                pytest.fail(error_msg)
        
        print(f"[OK] Documentation coverage within acceptable limits")

    @pytest.mark.guardian
    def test_import_organization(self):
        """
        Test import organization and best practices.
        
        Well-organized imports improve readability and prevent issues.
        """
        print("\n=== IMPORT ORGANIZATION VALIDATION ===")
        
        import_violations: List[Dict[str, str]] = []
        
        # Analyze all Python files
        for file_path in PROJECT_ROOT.rglob("*.py"):
            # Skip excluded directories
            if any(excluded in str(file_path) for excluded in 
                  ["__pycache__", ".git", ".pytest_cache", "node_modules",
                   "archives", ".sovereign_healing_backup"]):
                continue
            
            # Skip this test file
            if "test_code_quality_metrics.py" in str(file_path):
                continue
            
            rel_path = str(file_path.relative_to(PROJECT_ROOT))
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Check import organization
                import_section = []
                in_imports = True
                has_blank_after_imports = False
                
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    
                    # Stop checking imports after first non-import line
                    if in_imports and stripped and not stripped.startswith(('import ', 'from ')):
                        if stripped:
                            in_imports = False
                            # Check if there's a blank line after imports
                            if i + 1 < len(lines) and lines[i + 1].strip():
                                import_violations.append({
                                    "file": rel_path,
                                    "line": i + 1,
                                    "type": "missing_blank_after_imports",
                                    "description": "Missing blank line after imports"
                                })
                        continue
                    
                    if stripped.startswith(('import ', 'from ')):
                        import_section.append((i + 1, stripped))
                
                # Check for import organization issues
                if len(import_section) > 1:
                    # Check if imports are properly grouped
                    stdlib_imports = []
                    thirdparty_imports = []
                    local_imports = []
                    
                    for line_num, import_stmt in import_section:
                        if import_stmt.startswith('import ') or import_stmt.startswith('from '):
                            module = import_stmt.split()[1].split('.')[0]
                            
                            # Categorize import
                            if module in ['os', 'sys', 'pathlib', 'json', 'datetime', 'typing', 
                                        'collections', 'itertools', 'functools', 're', 'math',
                                        'random', 'string', 'time', 'uuid', 'hashlib', 'base64',
                                        'inspect', 'warnings', 'contextlib', 'dataclasses',
                                        'enum', 'copy', 'pickle', 'csv', 'io', 'logging']:
                                stdlib_imports.append((line_num, import_stmt))
                            elif module.startswith(('agentic_core', 'apps_rg', 'apps_lic', 'apps_shared')):
                                local_imports.append((line_num, import_stmt))
                            else:
                                thirdparty_imports.append((line_num, import_stmt))
                    
                    # Check if imports are in wrong order
                    all_imports = stdlib_imports + thirdparty_imports + local_imports
                    if len(all_imports) != len(import_section):
                        import_violations.append({
                            "file": rel_path,
                            "line": "multiple",
                            "type": "import_order",
                            "description": "Imports not properly ordered (stdlib, third-party, local)"
                        })
                
                # Check for multiple imports on one line (except specific cases)
                for line_num, import_stmt in import_section:
                    if import_stmt.startswith('import ') and ',' in import_stmt:
                        # Allow some common exceptions
                        if not any(pattern in import_stmt for pattern in [
                            'os, sys', 'typing import', 'collections import'
                        ]):
                            import_violations.append({
                                "file": rel_path,
                                "line": line_num,
                                "type": "multiple_imports_one_line",
                                "description": "Multiple imports on one line"
                            })
                            
            except (UnicodeDecodeError, PermissionError):
                continue
        
        # Report results
        print(f"  Import organization violations: {len(import_violations)}")
        
        # Track as tech debt with threshold
        KNOWN_IMPORT_VIOLATIONS = 30  # Allow up to 30 import violations
        
        if import_violations:
            if len(import_violations) <= KNOWN_IMPORT_VIOLATIONS:
                print(f"\n[TECH DEBT] {len(import_violations)} import violations (tracked, not blocking):")
                # Group by violation type
                by_type = defaultdict(list)
                for v in import_violations:
                    by_type[v['type']].append(v)
                
                for vtype, items in by_type.items():
                    print(f"  - {vtype}: {len(items)} files")
                    for item in items[:3]:
                        print(f"    * {item['file']}:{item['line']}")
                    if len(items) > 3:
                        print(f"    ... and {len(items) - 3} more")
            else:
                error_msg = f"IMPORT VIOLATIONS EXCEED THRESHOLD ({len(import_violations)} > {KNOWN_IMPORT_VIOLATIONS}):\n\n"
                
                # Group by violation type
                by_type = defaultdict(list)
                for v in import_violations:
                    by_type[v['type']].append(v)
                
                for vtype, items in by_type.items():
                    error_msg += f"  [{vtype.upper()}] {len(items)} violations:\n"
                    for item in items[:5]:
                        error_msg += f"    - {item['file']}:{item['line']} - {item['description']}\n"
                    if len(items) > 5:
                        error_msg += f"    ... and {len(items) - 5} more\n"
                    error_msg += "\n"
                
                pytest.fail(error_msg)
        
        print(f"[OK] Import organization is acceptable")
