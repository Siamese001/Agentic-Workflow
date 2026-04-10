"""
CI validation gate for timeout recovery pattern compliance.

Enforces Constitutional Rule §9.6: Automatic timeout recovery using ADG.
"""

import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    OPS_SCRIPTS_DIR,
    SYSTEM_LEARNING_DIR,
    TESTS_DIR,
    TOOLS_DIR,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import REPORTS_DIR


def validate_timeout_recovery_patterns(file_path: Path) -> list[str]:
    """Validate timeout recovery patterns in Python file."""
    violations = []

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError, SyntaxError) as e:    # guardian: Parsing and encoding errors need separate handling strategies
        print(f"Error reading {file_path}: {e}")
        return []

    # Check for timeout handling without recovery
    timeout_catches = list(re.finditer(r"except\s+TimeoutError", content))

    for match in timeout_catches:
        line_num = content[: match.start()].count("\n") + 1

        # Get the exception handler block (next ~50 lines)
        context_start = match.start()
        context_end = min(len(content), match.start() + 2000)
        handler_context = content[context_start:context_end]

        # Check if handler has ADG-based recovery
        has_adg_recovery = any(
            [
                "build_dependency_graph" in handler_context,
                "identify_bottleneck" in handler_context,
                "isolate_scope" in handler_context,
                "adg" in handler_context.lower(),
                "dependency_graph" in handler_context.lower(),
            ],
        )

        # Check if handler just re-raises without recovery attempt
        has_bare_reraise = re.search(r"raise\s*$", handler_context, re.MULTILINE)

        # If timeout is caught but no recovery and no bare re-raise, it's a violation
        if not has_adg_recovery and not has_bare_reraise:
            # Check if it's a simple re-raise with message
            has_reraise_with_msg = re.search(r"raise\s+TimeoutError", handler_context)
            if not has_reraise_with_msg:
                violations.append(
                    f"{file_path}:{line_num}: TimeoutError caught without ADG-based recovery "
                    f"(§9.6 requires automatic recovery with dependency graph analysis)",
                )

    return violations


def validate_evidence_timeout_recovery(evidence_path: Path) -> list[str]:
    """Validate evidence file documents timeout recovery per §9.6."""
    violations = []

    try:
        with open(evidence_path, encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError) as e:    # guardian: File operations with encoding need error-specific handling
        return [f"{evidence_path}: Failed to read file: {e}"]

    # If evidence mentions timeout, check for recovery documentation
    has_timeout_mention = "timeout" in content.lower() or "timed out" in content.lower()

    if has_timeout_mention:
        # Check for TIMEOUT_RECOVERY section
        if "## TIMEOUT_RECOVERY" not in content:
            # Check if it's just configuration, not actual timeout
            has_timeout_config = "## TIMEOUT_CONFIGURATION" in content
            has_actual_timeout = re.search(
                r"timed?\s+out|timeout\s+(exceeded|triggered)", content, re.IGNORECASE,
            )

            if has_actual_timeout and not has_timeout_config:
                violations.append(
                    f"{evidence_path}: Timeout occurred but missing ## TIMEOUT_RECOVERY section "
                    f"(§9.6 requires ADG analysis and recovery documentation)",
                )
        else:
            # Validate TIMEOUT_RECOVERY section has required fields
            recovery_section_match = re.search(r"## TIMEOUT_RECOVERY.*?(?=##|\Z)", content, re.DOTALL)

            if recovery_section_match:
                recovery_content = recovery_section_match.group(0)

                required_fields = ["Initial Timeout", "ADG Analysis", "Isolation Strategy", "Recovery Result"]

                for field in required_fields:
                    if field not in recovery_content:
                        violations.append(
                            f"{evidence_path}: TIMEOUT_RECOVERY section missing '{field}' subsection",
                        )

    return violations


def validate_module_level_blocking_ops(repo_path: Path) -> list[str]:
    """Find module-level blocking operations that could cause timeouts."""
    warnings = []

    # Check test files for module-level blocking operations
    test_dirs = [
        repo_path / TESTS_DIR,
    ]

    for test_dir in test_dirs:
        if not test_dir.exists():
            continue

        for test_file in test_dir.rglob("*.py"):
            if "__pycache__" in str(test_file):
                continue

            try:
                source = test_file.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(source, filename=str(test_file))
            except (OSError, UnicodeDecodeError, SyntaxError):    # guardian: Parsing and encoding errors need separate handling strategies
                continue

            # Find module-level calls
            for node in ast.iter_child_nodes(tree):
                # Skip function/class definitions
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    continue

                # Check assignments with calls
                if isinstance(node, ast.Assign):
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            op_name = _get_call_name(child)
                            if _is_blocking_op(op_name):
                                warnings.append(
                                    f"WARNING: {test_file}:{node.lineno} - Module-level {op_name} "
                                    f"(executes at collection time, may cause timeout)",
                                )
                                break

                # Check expression calls
                if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                    op_name = _get_call_name(node.value)
                    if _is_blocking_op(op_name):
                        warnings.append(
                            f"WARNING: {test_file}:{node.lineno} - Module-level {op_name} "
                            f"(executes at collection time, may cause timeout)",
                        )

    return warnings


def _get_call_name(call_node: ast.Call) -> str:
    """Extract call name from AST Call node."""
    func = call_node.func
    if isinstance(func, ast.Attribute):
        return func.attr
    elif isinstance(func, ast.Name):
        return func.id
    return ""


def _is_blocking_op(op_name: str) -> bool:
    """Check if operation is blocking at module scope."""
    blocking_patterns = [
        "read_text",
        "read",
        "open",
        "read_bytes",
        "subprocess",
        "run",
        "Popen",
        "check_output",
        "requests",
        "get",
        "post",
        "urlopen",
        "sleep",
        "wait",
    ]
    return any(pattern in op_name.lower() for pattern in blocking_patterns)


def run_full_validation(repo_path: Path) -> dict[str, list[str]]:
    """Run full timeout recovery validation on repository."""

    all_violations = {"code": [], "evidence": [], "warnings": []}

    # Validate Python files for timeout recovery patterns
    key_dirs = [
        repo_path / AGENTIC_CORE_DIR,
        repo_path / APPS_LIC_DIR,
        repo_path / APPS_RG_DIR,
        repo_path / APPS_SHARED_DIR,
        repo_path / OPS_SCRIPTS_DIR,
        repo_path / TOOLS_DIR,
        repo_path / SYSTEM_LEARNING_DIR,
    ]

    for key_dir in key_dirs:
        if not key_dir.exists():
            continue

        for py_file in key_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            violations = validate_timeout_recovery_patterns(py_file)
            all_violations["code"].extend(violations)

    # Validate evidence files
    evidence_dir = repo_path / "docs" / REPORTS_DIR / "plans"
    if evidence_dir.exists():
        for evidence_file in evidence_dir.glob("EVIDENCE_*.md"):
            violations = validate_evidence_timeout_recovery(evidence_file)
            all_violations["evidence"].extend(violations)

    # Check for module-level blocking operations (warnings only)
    warnings = validate_module_level_blocking_ops(repo_path)
    all_violations["warnings"].extend(warnings)

    return all_violations


def main() -> int:
    """CI gate for timeout recovery compliance."""

    repo_path = Path.cwd()

    print("=" * 80)
    print("TIMEOUT RECOVERY PATTERN VALIDATION")
    print("Constitutional Rule §9.6 Enforcement")
    print("=" * 80)
    print()

    violations = run_full_validation(repo_path)

    total_violations = len(violations["code"]) + len(violations["evidence"])
    total_warnings = len(violations["warnings"])

    if total_violations > 0:
        print(f"❌ FOUND {total_violations} VIOLATIONS\n")

        if violations["code"]:
            print(f"Code violations ({len(violations['code'])}):")
            for v in violations["code"]:
                print(f"  - {v}")
            print()

        if violations["evidence"]:
            print(f"Evidence violations ({len(violations['evidence'])}):")
            for v in violations["evidence"]:
                print(f"  - {v}")
            print()

        print("=" * 80)
        print("REMEDIATION:")
        print("  1. Add ADG-based recovery to TimeoutError handlers")
        print("  2. Document recovery in evidence with ## TIMEOUT_RECOVERY section")
        print("  3. See: .windsurf/skills/timeout-progress-enforcement/adg_timeout_recovery.md")
        print("=" * 80)

        return 1  # Fail CI

    print("✅ All timeout recovery requirements met")

    if total_warnings > 0:
        print(f"\n⚠️  {total_warnings} WARNINGS (module-level blocking operations):\n")
        for w in violations["warnings"][:10]:  # Show first 10
            print(f"  {w}")
        if total_warnings > 10:
            print(f"  ... and {total_warnings - 10} more")
        print("\nThese operations execute at import/collection time and may cause timeouts.")
        print("Consider moving to function scope or using lazy initialization.")

    print()
    return 0  # Pass CI


if __name__ == "__main__":
    sys.exit(main())
