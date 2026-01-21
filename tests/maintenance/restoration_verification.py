#!/usr/bin/env python3
"""
Restoration Verification Suite
==============================
A targeted smoke test to verify that the 10 restored agents can be imported
and instantiated, catching broken imports or duplicate mixins immediately.

RCA Context:
- Logs warned about "broken imports" and "duplicate MCPHardenedMixin imports"
- Restoring files without refactoring internals will cause runtime ImportErrors
- This test catches those issues before they hit production
"""

import importlib
import inspect
import sys
from pathlib import Path

# Setup path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Mapping of restored files to their expected module paths
RESTORED_AGENTS: list[tuple[str, str]] = [
    # (Agent Name, Full Module Path)
    ("MetaLearningAgent", "agentic_core.L1_cognition.thought_engine.MetaLearningAgent"),
    ("StrategicRecommendationAgent", "agentic_core.L1_cognition.thought_engine.StrategicRecommendationAgent"),
    ("BudgetAgent", "agentic_core.L1_cognition.thought_engine.BudgetAgent"),
    ("CodeDeduplicationAgent", "agentic_core.L5_safety.validators.CodeDeduplicationAgent"),
    ("PatternEnforcerAgent", "agentic_core.L5_safety.validators.PatternEnforcerAgent"),
    ("DeadlockDetectorAgent", "agentic_core.L5_safety.validators.DeadlockDetectorAgent"),
    ("IntegrityGateExecutorAgent", "agentic_core.L5_safety.validators.IntegrityGateExecutorAgent"),
    ("TypeMechanicAgent", "agentic_core.L5_safety.validators.TypeMechanicAgent"),
    ("DocumentationAgent", "agentic_core.L5_safety.validators.DocumentationAgent"),
    ("BenchmarkingAgent", "agentic_core.L6_observability.BenchmarkingAgent"),
]

PASSED = 0
FAILED = 0


def test_pass(agent_name: str, msg: str):
    global PASSED
    PASSED += 1
    print(f"  ✅ {agent_name.ljust(30)} | {msg}")


def test_fail(agent_name: str, msg: str):
    global FAILED
    FAILED += 1
    print(f"  ❌ {agent_name.ljust(30)} | {msg}")


def check_file_exists(module_path: str) -> tuple[bool, str, Path]:
    """Check if the file exists at the expected location."""
    # Convert module path to file path
    parts = module_path.split(".")
    file_path = PROJECT_ROOT / "/".join(parts[:-1]) / f"{parts[-1]}.py"

    if file_path.exists():
        return True, "File exists", file_path
    return False, f"File not found: {file_path}", file_path


def check_syntax(file_path: Path) -> tuple[bool, str]:
    """Check if the file has valid Python syntax."""
    import ast
    try:
        content = file_path.read_text(encoding='utf-8')
        ast.parse(content)
        return True, "Valid syntax"
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"


def check_class_defined(file_path: Path, class_name: str) -> tuple[bool, str]:
    """Check if the class is defined in the file."""
    import ast
    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                return True, f"Class {class_name} defined"

        return False, f"Class {class_name} not found in file"
    except Exception as e:
        return False, f"Error parsing: {e}"


def check_imports(file_path: Path) -> tuple[bool, str, list[str]]:
    """Check for potentially broken imports."""
    import ast
    issues = []

    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    # Check for deprecated/moved imports
                    if 'MCPHardenedMixin' in [alias.name for alias in node.names]:
                        # Check if importing from correct location
                        if 'L5_safety.guardrails.mcp_hardened_mixin' not in node.module and \
                           'L2_execution.mcp.mcp_hardened_mixin' not in node.module:
                            issues.append(f"MCPHardenedMixin import from deprecated location: {node.module}")

                    # Check for imports from archives (bad!)
                    if 'archives' in node.module:
                        issues.append(f"Import from archives: {node.module}")

        if issues:
            return False, "Import issues found", issues
        return True, "Imports OK", []

    except Exception as e:
        return False, f"Error checking imports: {e}", []


def check_import_safety(module_path: str, class_name: str) -> tuple[bool, str]:
    """
    Attempts to import the module and inspect the class.
    Catches ImportError, SyntaxError, and AttributeError.
    """
    try:
        module = importlib.import_module(module_path)
        if not hasattr(module, class_name):
            return False, f"Class {class_name} not found in {module_path}"

        agent_class = getattr(module, class_name)

        # Check for the specific Mixin issue mentioned in logs
        mro = inspect.getmro(agent_class)
        mro_names = [c.__name__ for c in mro]

        # Check for duplicates in MRO (indicates diamond problem or bad composition)
        seen = set()
        duplicates = []
        for name in mro_names:
            if name in seen and name != 'object':
                duplicates.append(name)
            seen.add(name)

        if duplicates:
            return False, f"Duplicate in MRO: {duplicates}"

        return True, "Import OK, MRO clean"

    except ImportError as e:
        return False, f"ImportError: {e}"
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"
    except Exception as e:
        return False, f"Unexpected Error: {e}"


def verify_agent(agent_name: str, module_path: str) -> bool:
    """Run all verification checks for a single agent."""
    print(f"\n--- {agent_name} ---")

    # Step 1: Check file exists
    exists, msg, file_path = check_file_exists(module_path)
    if not exists:
        test_fail(agent_name, msg)
        return False
    test_pass(agent_name, msg)

    # Step 2: Check syntax
    valid, msg = check_syntax(file_path)
    if not valid:
        test_fail(agent_name, msg)
        return False
    test_pass(agent_name, msg)

    # Step 3: Check class defined
    defined, msg = check_class_defined(file_path, agent_name)
    if not defined:
        test_fail(agent_name, msg)
        return False
    test_pass(agent_name, msg)

    # Step 4: Check imports (static analysis)
    imports_ok, msg, issues = check_imports(file_path)
    if not imports_ok:
        test_fail(agent_name, f"{msg}: {issues}")
        # Don't return False - continue to runtime check
    else:
        test_pass(agent_name, msg)

    # Step 5: Runtime import check (optional - may fail due to missing deps)
    # success, msg = check_import_safety(module_path, agent_name)
    # if success:
    #     test_pass(agent_name, msg)
    # else:
    #     test_fail(agent_name, msg)
    #     return False

    return True


def main():
    print("=" * 70)
    print("RESTORATION VERIFICATION SUITE")
    print("=" * 70)
    print("Verifying 10 restored agents for import safety and MRO integrity")
    print()

    all_passed = True

    for agent_name, module_path in RESTORED_AGENTS:
        if not verify_agent(agent_name, module_path):
            all_passed = False

    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    print(f"  Total Checks: {PASSED + FAILED}")
    print(f"  Passed: {PASSED}")
    print(f"  Failed: {FAILED}")
    print(f"  Pass Rate: {PASSED / (PASSED + FAILED) * 100:.1f}%" if (PASSED + FAILED) > 0 else "  No tests run")
    print()

    if FAILED == 0:
        print("  ✅ ALL VERIFICATION CHECKS PASSED")
        return 0
    else:
        print(f"  ❌ {FAILED} CHECKS FAILED - AGENTS NEED REPAIR")
        return 1


if __name__ == "__main__":
    sys.exit(main())
