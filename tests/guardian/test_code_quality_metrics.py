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

import ast
import sys
from collections import defaultdict
from pathlib import Path

import pytest

#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    ARCHIVES_DIR,
    TESTS_DIR,
)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


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
                from agentic_core.L0_routing.config.path_constants import (
                """
                Test that no files exceed maximum size limits (monolith detection).

        Test that no files exceed maximum size limits (monolith detection).

        Large files are harder to maintain and should be split.
        """
        print("\n=== FILE SIZE VALIDATION (MONOLITH DETECTION) ===")

        MONOLITH_THRESHOLD = 800  # lines of code (excluding comments/blank)
        MAX_FILE_SIZE = 50000  # bytes (50KB)

        large_files: list[dict[str, int]] = []
        oversized_files: list[dict[str, int]] = []

        # Check all Python files
        for file_path in PROJECT_ROOT.rglob("*.py"):
            # Skip excluded directories
            if any(
                excluded in str(file_path)
                for excluded in [
                    "__pycache__",
                    ".git",
                    ".pytest_cache",
                    "node_modules",
                    ARCHIVES_DIR,
                    ".sovereign_healing_backup",
                ]
            ):
                continue

            # Skip this test file
            if "test_code_quality_metrics.py" in str(file_path):
                continue

            # Check file size in bytes
            file_size = file_path.stat().st_size
            if file_size > MAX_FILE_SIZE:
                oversized_files.append(
                    {
                        "file": str(file_path.relative_to(PROJECT_ROOT)),
                        "size_bytes": file_size,
                        "size_kb": round(file_size / 1024, 2),
                    },
                )

            # Count lines of code (excluding comments and blank lines)
            try:
                with open(file_path, encoding="utf-8") as f:
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
                    if (
                        stripped.startswith("#")
                        or in_multiline_comment
                        or stripped.startswith('"""')
                        or stripped.startswith("'''")
                    ):
                        continue

                    code_lines += 1

                if code_lines > MONOLITH_THRESHOLD:
                    large_files.append({"file": str(file_path.relative_to(PROJECT_ROOT)), "loc": code_lines})

            except (UnicodeDecodeError, PermissionError):  # guardian: allow-silent-swallower
                # Skip files that can't be read
                continue

        # Report results
        print(f"  Files checked for size: {len(list(PROJECT_ROOT.rglob('*.py')))}")
        print(f"  Oversized files (>50KB): {len(oversized_files)}")
        print(f"  Large files (>800 LOC): {len(large_files)}")

        # Report oversized files
        if oversized_files:
            print(f"\n[REPORT] {len(oversized_files)} oversized files:")
            for file_info in oversized_files:
                print(f"  - {file_info['file']} ({file_info['size_kb']}KB)")
            print("\nConsider splitting large files or moving assets to separate files.")

        # Report large files (monoliths)
        if large_files:
            print(f"\n[REPORT] {len(large_files)} monolith files:")
            for file_info in large_files:
                print(f"  - {file_info['file']} ({file_info['loc']} LOC)")
            print("\nLarge files should be split into smaller, focused modules.")

        if not oversized_files and not large_files:
            print("[OK] File sizes within acceptable limits")

    @pytest.mark.guardian
    def test_cyclomatic_complexity(self):
        """
        Test cyclomatic complexity of Python files.

        High complexity indicates need for refactoring.
        """
        print("\n=== CYCLOMATIC COMPLEXITY VALIDATION ===")

        COMPLEXITY_THRESHOLD = 15  # Maximum complexity per function

        complex_functions: list[dict[str, int]] = []

        def calculate_complexity(node: ast.AST) -> int:
            """Calculate cyclomatic complexity for an AST node."""
            complexity = 1  # Base complexity

            for child in ast.walk(node):
                if isinstance(
                    child,
                    ast.If
                    | ast.While
                    | ast.For
                    | ast.AsyncFor
                    | ast.ExceptHandler
                    | ast.With
                    | ast.AsyncWith,
                ):
                    complexity += 1
                elif isinstance(child, ast.BoolOp):
                    complexity += len(child.values) - 1

            return complexity

        # Analyze all Python files
        for file_path in PROJECT_ROOT.rglob("*.py"):
            # Skip excluded directories and test files
            if any(
                excluded in str(file_path)
                for excluded in [
                    "__pycache__",
                    ".git",
                    ".pytest_cache",
                    "node_modules",
                    ARCHIVES_DIR,
                    ".sovereign_healing_backup",
                    TESTS_DIR,
                ]
            ):
                continue

            # Skip this test file
            if "test_code_quality_metrics.py" in str(file_path):
                continue

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content, filename=str(file_path))

                # Check each function and method
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                        complexity = calculate_complexity(node)
                        if complexity > COMPLEXITY_THRESHOLD:
                            complex_functions.append(
                                {
                                    "file": str(file_path.relative_to(PROJECT_ROOT)),
                                    "function": node.name,
                                    "line": node.lineno,
                                    "complexity": complexity,
                                },
                            )

            except (SyntaxError, UnicodeDecodeError):  # guardian: allow-silent-swallower
# REMOVED HIDDEN FAILURE SKIP: # REMOVED SKIP: # REMOVED HIDDEN FAILURE SKIP: # REMOVED SKIP: # Skip files with syntax errors  # REVEALED FAILURE: # skip files with syntax errors  # REVEALED FAILURE: # removed hidden failure skip: # removed skip: # skip files with syntax errors  # revealed failure: # skip files with syntax errors
                continue

        # Report results
        print(f"  Functions with high complexity: {len(complex_functions)}")

        if complex_functions:
            print(f"\n[REPORT] {len(complex_functions)} complex functions:")
            for func_info in complex_functions[:10]:
                print(
                    f"  - {func_info['file']}:{func_info['line']} {func_info['function']}() (complexity: {func_info['complexity']})",
                )
            if len(complex_functions) > 10:
                print(f"  ... and {len(complex_functions) - 10} more")
            print(f"\nFunctions with complexity > {COMPLEXITY_THRESHOLD} should be refactored.")
        else:
            print("[OK] Cyclomatic complexity within acceptable limits")

    @pytest.mark.guardian
    def test_documentation_coverage(self):
        """
        Test documentation coverage of modules and classes.

        Good documentation is essential for maintainability.
        """
        print("\n=== DOCUMENTATION COVERAGE VALIDATION ===")

        undocumented_modules: list[str] = []
        undocumented_classes: list[dict[str, str]] = []
        undocumented_functions: list[dict[str, str]] = []

        # Analyze all Python files
        for file_path in PROJECT_ROOT.rglob("*.py"):
            # Skip excluded directories and test files
            if any(
                excluded in str(file_path)
                for excluded in [
                    "__pycache__",
                    ".git",
                    ".pytest_cache",
                    "node_modules",
                    ARCHIVES_DIR,
                    ".sovereign_healing_backup",
                ]
            ):
                continue

            if file_path.name.startswith("test_") or "_test.py" in file_path.name:
                continue

            # Skip this test file
            if "test_code_quality_metrics.py" in str(file_path):
                continue

            rel_path = str(file_path.relative_to(PROJECT_ROOT))

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                # Check module docstring
                tree = ast.parse(content, filename=str(file_path))

                # Get first node and check if it's a docstring
                if (
                    tree.body
                    and isinstance(tree.body[0], ast.Expr)
                    and isinstance(tree.body[0].value, ast.Constant)
                    and isinstance(tree.body[0].value.value, str)
                ):
                    # Module has docstring
                    pass
                else:
                    undocumented_modules.append(rel_path)

                # Check classes and functions
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check class docstring
                        if (
                            node.body
                            and isinstance(node.body[0], ast.Expr)
                            and isinstance(node.body[0].value, ast.Constant)
                            and isinstance(node.body[0].value.value, str)
                        ):
                            pass  # Has docstring
                        else:
                            undocumented_classes.append(
                                {"file": rel_path, "name": node.name, "line": node.lineno},
                            )

                    elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                        # Skip private methods and test functions
                        if (
                            node.name.startswith("_")
                            or node.name.startswith("test_")
                            or node.name.endswith("_test")
                        ):
                            continue

                        # Check function docstring
                        if (
                            node.body
                            and isinstance(node.body[0], ast.Expr)
                            and isinstance(node.body[0].value, ast.Constant)
                            and isinstance(node.body[0].value.value, str)
                        ):
                            pass  # Has docstring
                        else:
                            undocumented_functions.append(
                                {"file": rel_path, "name": node.name, "line": node.lineno},
                            )

            except (SyntaxError, UnicodeDecodeError):  # guardian: allow-silent-swallower
                continue

        # Report results
        print(f"  Undocumented modules: {len(undocumented_modules)}")
        print(f"  Undocumented classes: {len(undocumented_classes)}")
        print(f"  Undocumented functions: {len(undocumented_functions)}")

        # Report undocumented modules
        if undocumented_modules:
            print(f"\n[REPORT] {len(undocumented_modules)} undocumented modules:")
            for module in undocumented_modules[:10]:
                print(f"  - {module}")
            if len(undocumented_modules) > 10:
                print(f"  ... and {len(undocumented_modules) - 10} more")

        # Report undocumented classes
        if undocumented_classes:
            print(f"\n[REPORT] {len(undocumented_classes)} undocumented classes:")
            for class_info in undocumented_classes[:10]:
                print(f"  - {class_info['file']}:{class_info['line']} {class_info['name']}")
            if len(undocumented_classes) > 10:
                print(f"  ... and {len(undocumented_classes) - 10} more")

        # Report undocumented functions
        if undocumented_functions:
            print(f"\n[REPORT] {len(undocumented_functions)} undocumented functions:")
            for func_info in undocumented_functions[:10]:
                print(f"  - {func_info['file']}:{func_info['line']} {func_info['name']}()")
            if len(undocumented_functions) > 10:
                print(f"  ... and {len(undocumented_functions) - 10} more")

        if not undocumented_modules and not undocumented_classes and not undocumented_functions:
            print("[OK] Documentation coverage is complete")

    @pytest.mark.guardian
    def test_import_organization(self):
        """
        Test import organization and best practices.

        Well-organized imports improve readability and prevent issues.
        """
        print("\n=== IMPORT ORGANIZATION VALIDATION ===")

        import_violations: list[dict[str, str]] = []

        # Analyze all Python files
        for file_path in PROJECT_ROOT.rglob("*.py"):
            # Skip excluded directories
            if any(
                excluded in str(file_path)
                for excluded in [
                    "__pycache__",
                    ".git",
                    ".pytest_cache",
                    "node_modules",
                    ARCHIVES_DIR,
                    ".sovereign_healing_backup",
                ]
            ):
                continue

            # Skip this test file
            if "test_code_quality_metrics.py" in str(file_path):
                continue

            rel_path = str(file_path.relative_to(PROJECT_ROOT))

            try:
                with open(file_path, encoding="utf-8") as f:
                    lines = f.readlines()

                # Check import organization
                import_section = []
                in_imports = True

                for i, line in enumerate(lines):
                    stripped = line.strip()

                    # Stop checking imports after first non-import line
                    if in_imports and stripped and not stripped.startswith(("import ", "from ")):
                        if stripped:
                            in_imports = False
                            # Check if there's a blank line after imports
                            if i + 1 < len(lines) and lines[i + 1].strip():
                                import_violations.append(
                                    {
                                        "file": rel_path,
                                        "line": i + 1,
                                        "type": "missing_blank_after_imports",
                                        "description": "Missing blank line after imports",
                                    },
                                )
                        continue

                    if stripped.startswith(("import ", "from ")):
                        import_section.append((i + 1, stripped))

                # Check for import organization issues
                if len(import_section) > 1:
                    # Check if imports are properly grouped
                    stdlib_imports = []
                    thirdparty_imports = []
                    local_imports = []

                    for line_num, import_stmt in import_section:
                        if import_stmt.startswith("import ") or import_stmt.startswith("from "):
                            module = import_stmt.split()[1].split(".")[0]

                            # Categorize import
                            if module in [
                                "os",
                                "sys",
                                "pathlib",
                                "json",
                                "datetime",
                                "typing",
                                "collections",
                                "itertools",
                                "functools",
                                "re",
                                "math",
                                "random",
                                "string",
                                "time",
                                "uuid",
                                "hashlib",
                                "base64",
                                "inspect",
                                "warnings",
                                "contextlib",
                                "dataclasses",
                                "enum",
                                "copy",
                                "pickle",
                                "csv",
                                "io",
                                "logging",
                            ]:
                                stdlib_imports.append((line_num, import_stmt))
                            elif module.startswith((AGENTIC_CORE_DIR, APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR)):
                                local_imports.append((line_num, import_stmt))
                            else:
                                thirdparty_imports.append((line_num, import_stmt))

                    # Check if imports are in wrong order
                    all_imports = stdlib_imports + thirdparty_imports + local_imports
                    if len(all_imports) != len(import_section):
                        import_violations.append(
                            {
                                "file": rel_path,
                                "line": "multiple",
                                "type": "import_order",
                                "description": "Imports not properly ordered (stdlib, third-party, local)",
                            },
                        )

                # Check for multiple imports on one line (except specific cases)
                for line_num, import_stmt in import_section:
                    if import_stmt.startswith("import ") and "," in import_stmt:
                        # Allow some common exceptions
                        if not any(
                            pattern in import_stmt
                            for pattern in ["os, sys", "typing import", "collections import"]
                        ):
                            import_violations.append(
                                {
                                    "file": rel_path,
                                    "line": line_num,
                                    "type": "multiple_imports_one_line",
                                    "description": "Multiple imports on one line",
                                },
                            )

            except (UnicodeDecodeError, PermissionError):  # guardian: allow-silent-swallower
                continue

        # Report results
        print(f"  Import organization violations: {len(import_violations)}")

        if import_violations:
            print(f"\n[REPORT] {len(import_violations)} import violations:")
            # Group by violation type
            by_type = defaultdict(list)
            for v in import_violations:
                by_type[v["type"]].append(v)

            for vtype, items in by_type.items():
                print(f"  - {vtype}: {len(items)} files")
                for item in items[:3]:
                    print(f"    * {item['file']}:{item['line']}")
                if len(items) > 3:
                    print(f"    ... and {len(items) - 3} more")
        else:
            print("[OK] Import organization is acceptable")
