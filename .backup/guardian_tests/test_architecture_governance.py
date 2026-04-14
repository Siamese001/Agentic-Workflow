#!/usr/bin/env python3
"""
Deterministic Guardian Test for Architecture Governance
Tests layer boundaries, naming conventions, and structural compliance.
"""

import ast
import sys
from pathlib import Path

# Layer hierarchy (lower layers cannot import from higher layers)
LAYER_HIERARCHY = {
    "L0_maintenance": 0,
    "L1_cognition": 1,
    "L2_execution": 2,
    "L3_orchestration": 3,
    "L4_state": 4,
    "L5_safety": 5,
    "L6_observability": 6,
}


def get_layer_from_path(file_path: Path) -> tuple[str, int]:
    """
    Extract layer from file path.

    Returns:
        Tuple of (layer_name, layer_number) or ("unknown", -1)
    """
    parts = file_path.parts
    for part in parts:
        if part in LAYER_HIERARCHY:
            return (part, LAYER_HIERARCHY[part])
    return ("unknown", -1)


def check_gravity_violations(file_path: Path) -> list[str]:
    """
    Check for gravity violations (lower layers importing from higher layers).

    Returns:
        List of violation messages
    """
    violations = []

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content)

        current_layer, current_level = get_layer_from_path(file_path)

        if current_level == -1:
            return []  # Not in a layer directory

        # Check all imports
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom) and node.module:
                    module_parts = node.module.split(".")

                    # Check if importing from agentic_core layer
                    if len(module_parts) >= 2 and module_parts[0] == "agentic_core":
                        imported_layer = module_parts[1]
                        if imported_layer in LAYER_HIERARCHY:
                            imported_level = LAYER_HIERARCHY[imported_layer]

                            # Gravity violation: lower layer importing higher layer
                            if current_level < imported_level:
                                violations.append(
                                    f"Gravity violation: {current_layer} (L{current_level}) "
                                    f"importing from {imported_layer} (L{imported_level})"
                                )
    except (ValueError, TypeError, RuntimeError) as e:
        violations.append(f"Error parsing file: {e}")

    return violations


def check_naming_convention(file_path: Path) -> list[str]:
    """
    Check that agent files follow naming conventions.

    Returns:
        List of violation messages
    """
    violations = []

    # Check if file is in agentic_core and contains agent classes
    if "agentic_core" not in str(file_path):
        return []

    if not file_path.suffix == ".py":
        return []

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content)

        # Find agent classes
        agent_classes = [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef) and node.name.endswith("Agent")
        ]

        # If file contains agent classes, it should end with Agent.py
        if agent_classes and not file_path.stem.endswith("Agent"):
            violations.append(
                f"Naming violation: File contains agent classes {agent_classes} "
                f"but doesn't end with 'Agent.py'"
            )
    except (ValueError, TypeError, RuntimeError) as e:
        # Syntax errors are not naming violations
        pass

    return violations


def test_architecture_governance(file_path: str) -> None:
    """
    Test architecture governance for a single file.

    Args:
        file_path: Path to the file to test

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

    violations = []

    # Check gravity violations
    gravity_violations = check_gravity_violations(path)
    violations.extend(gravity_violations)

    # Check naming conventions
    naming_violations = check_naming_convention(path)
    violations.extend(naming_violations)

    if violations:
        print(f"VIOLATION: Architecture governance violations in {file_path}:")
        for violation in violations:
            print(f"  - {violation}")
        sys.exit(1)
    else:
        print(f"COMPLIANT: Architecture governance validated for {file_path}")
        sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_architecture_governance.py <file_path>")
        sys.exit(1)

    test_architecture_governance(sys.argv[1])