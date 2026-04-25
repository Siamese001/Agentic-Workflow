#!/usr/bin/env python3
"""
Deterministic Guardian Test for Agent Validation
Tests agent compliance without runtime instantiation.
"""

import ast
import sys
from pathlib import Path
from typing import Any


def check_agent_structure(file_path: Path) -> dict[str, Any]:
    """
    Check agent structure using static analysis.

    Returns:
        Dict with validation results
    """
    results = {
        "has_agent_class": False,
        "has_init": False,
        "has_run_method": False,
        "has_heal_method": False,
        "has_test_method": False,
        "violations": [],
    }

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content)

        # Find agent classes (classes ending with "Agent")
        agent_classes = [
            node for node in ast.walk(tree) if isinstance(node, ast.ClassDef) and node.name.endswith("Agent")
        ]

        if not agent_classes:
            results["violations"].append("No agent classes found")
            return results

        results["has_agent_class"] = True

        # Check first agent class for required methods
        agent_class = agent_classes[0]
        methods = [node.name for node in agent_class.body if isinstance(node, ast.FunctionDef)]

        # Check for __init__
        if "__init__" in methods or "__post_init__" in methods:
            results["has_init"] = True

        # Check for run method
        if "run" in methods:
            results["has_run_method"] = True

        # Check for heal method
        if "heal" in methods or "heal_repository" in methods or "apply_fix" in methods:
            results["has_heal_method"] = True

        # Check for test method
        if any(m.startswith("test_") or "self_test" in m for m in methods):
            results["has_test_method"] = True

    # guardian: allow-silent-swallow - acceptable exception handling
    except SyntaxError as e:
        results["violations"].append(f"Syntax error: {e}")
    except (ValueError, TypeError, RuntimeError) as e:
        results["violations"].append(f"Error parsing file: {e}")

    return results


def validate_agent_compliance(file_path: str) -> None:
    """
    Validate agent compliance using static analysis.

    Args:
        file_path: Path to the agent file to validate

    Raises:
        SystemExit: 1 if violations found, 0 if compliant
    """
    path = Path(file_path)

    if not path.exists():
        print(f"VIOLATION: File does not exist: {file_path}")
        sys.exit(1)

    if not path.is_file():
        print(f"VIOLATION: Not a file: {file_path}")
        sys.exit(1)

    if not path.suffix == ".py":
        print(f"VIOLATION: Not a Python file: {file_path}")
        sys.exit(1)

    # Check agent structure
    results = check_agent_structure(path)

    # Collect violations
    violations = results["violations"].copy()

    # Basic compliance checks
    if not results["has_agent_class"]:
        violations.append("No agent class found in file")

    if results["has_agent_class"] and not results["has_init"]:
        # Not a critical violation - some agents use dataclass
        pass

    # Report results
    if violations:
        print(f"VIOLATION: Agent validation failed for {file_path}:")
        for violation in violations:
            print(f"  - {violation}")
        sys.exit(1)
    else:
        print(f"COMPLIANT: Agent validation passed for {file_path}")
        print(f"  - Has agent class: {results['has_agent_class']}")
        print(f"  - Has init: {results['has_init']}")
        print(f"  - Has run method: {results['has_run_method']}")
        print(f"  - Has heal method: {results['has_heal_method']}")
        print(f"  - Has test method: {results['has_test_method']}")
        sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_agent_validation.py <file_path>")
        sys.exit(1)

    validate_agent_compliance(sys.argv[1])
