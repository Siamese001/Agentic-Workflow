#!/usr/bin/env python3
"""Find import-only tests in the test suite."""

import ast
from pathlib import Path
from typing import List, Set, Tuple


def is_import_only_test(node: ast.FunctionDef) -> bool:
    """Check if a test function only performs import checks."""
    # Skip if not a test function
    if not node.name.startswith("test_"):
        return False
    
    # Check for common import-only patterns
    import_checks = [
        "assert m is not None",
        "assert hasattr(",
        "assert isinstance(",
        "assert callable(",
        "import importlib",
        "importlib.import_module",
    ]
    
    # Get the source code
    # This is a simplified check - in reality we'd need the actual source
    # For now, we'll check the AST for patterns
    for child in ast.walk(node):
        if isinstance(child, ast.Assert):
            # Check if it's checking import results
            if isinstance(child.test, ast.Compare):
                for op in child.test.ops:
                    if isinstance(op, ast.Is):
                        # Check if comparing to None
                        for comparator in child.test.comparators:
                            if isinstance(comparator, ast.Constant) and comparator.value is None:
                                return True
            elif isinstance(child.test, ast.Call) and isinstance(child.test.func, ast.Name):
                if child.test.func.id in ("hasattr", "isinstance", "callable"):
                    return True
    
    return False


def find_import_only_tests_in_file(file_path: Path) -> List[str]:
    """Find import-only tests in a Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        tree = ast.parse(content)
        import_only_tests = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                # Simple heuristic: check for import-only patterns in source
                if "importable" in node.name.lower():
                    import_only_tests.append(node.name)
                elif "is not None" in ast.get_source_segment(content, node) or "":
                    # This is a rough check
                    source = ast.get_source_segment(content, node) or ""
                    if any(pattern in source for pattern in [
                        "importlib.import_module",
                        "assert m is not None",
                        "assert hasattr(",
                        "# Should not raise",
                        "# Module must be importable"
                    ]):
                        import_only_tests.append(node.name)
        
        return import_only_tests
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []


def main():
    """Find all import-only tests in the test suite."""
    test_dir = Path("tests")
    import_only_tests = {}
    total_count = 0
    
    for test_file in test_dir.rglob("test_*.py"):
        import_only = find_import_only_tests_in_file(test_file)
        if import_only:
            import_only_tests[str(test_file)] = import_only
            total_count += len(import_only)
    
    print(f"\nFound {total_count} import-only tests across {len(import_only_tests)} files:\n")
    
    for file_path, tests in sorted(import_only_tests.items()):
        print(f"{file_path}:")
        for test in tests:
            print(f"  - {test}")
        print()
    
    # Also count removed files
    removed_files = [
        "test_classification_kernel.py",
        "test_IValidatorProtocol.py",
        "test_L1CognitionBase.py",
        "test_L3OrchestrationBase.py",
        "test_L6ObservabilityBase.py",
        "test_L5SafetyBase.py",
        "test_L2ExecutionBase.py",
        "test_L4StateBase.py",
        "test_IOrchestratorProtocol.py",
        "test_sovereign_seal_state.py",
        "test_IBlackboardLeaseVerifierProtocol.py",
        "test_decorators.py",
        "test_HOPPipelineExecutor.py",
        "test_RGStrategyExecutor.py",
        "test_RGValidationExecutor.py",
        "test_FileClassificationAgent.py",
    ]
    
    print(f"\nRemoved {len(removed_files)} files that were entirely import-only tests")
    print(f"\nTotal import-only tests removed: ~{len(removed_files) * 2 + total_count}")


if __name__ == "__main__":
    main()
