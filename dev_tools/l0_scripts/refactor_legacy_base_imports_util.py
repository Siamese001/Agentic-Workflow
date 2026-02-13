#!/usr/bin/env python3
"""
Global Refactor Script: Phase 4 - Legacy Base Class Removal

This script performs the global search and replace to repoint all agents
from legacy base classes to SovereignBaseAgent SSOT.

Usage: python scripts/refactor_legacy_base_imports_util.py
"""

import os
import re
from pathlib import Path

# Legacy to SovereignBaseAgent mapping
LEGACY_IMPORTS = {
    "L1CognitionBase": "agentic_core.base_agents.L1CognitionBase",
    "L2ExecutionBase": "agentic_core.L2_execution.L2ExecutionBase",
    "L3OrchestrationBase": "agentic_core.L3_orchestration.reasoning.L3OrchestrationBase",
    "L4StateBase": "agentic_core.L4_state.memory.L4StateBase",
    "L5SafetyBase": "agentic_core.L5_safety.validators.L5SafetyBase",
    "L6ObservabilityBase": "agentic_core.L6_observability.L6ObservabilityBase",
    "MaintenanceBaseAgent": "agentic_core.L5_safety.validators.MaintenanceBaseAgent",
}


def find_python_files(directory: Path) -> list[Path]:
    """Find all Python files in the directory recursively."""
    python_files = []
    for root, _dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(Path(root) / file)
    return python_files


def refactor_file(file_path: Path) -> tuple[bool, list[str]]:
    """Refactor a single file to replace legacy base class imports."""
    changes_made = []
    modified = False

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Replace import statements
        for legacy_name, legacy_path in LEGACY_IMPORTS.items():
            # Pattern: from legacy_path import legacy_name
            import_pattern = f"from {legacy_path} import {legacy_name}"
            if import_pattern in content:
                content = content.replace(
                    import_pattern,
                    "from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent",
                )
                changes_made.append(
                    f"Import: {import_pattern} -> from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent",
                )
                modified = True

            # Pattern: relative imports like from .L5SafetyBase import L5SafetyBase
            relative_import_pattern = f"from .{legacy_name} import {legacy_name}"
            if relative_import_pattern in content:
                content = content.replace(
                    relative_import_pattern,
                    "from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent",
                )
                changes_made.append(
                    f"Import: {relative_import_pattern} -> from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent",
                )
                modified = True

        # Replace class inheritance
        for legacy_name in LEGACY_IMPORTS.keys():
            # Pattern: class SomeAgent(LegacyBaseAgent):
            inheritance_pattern = re.compile(rf"class\s+(\w+)\s*\(\s*{legacy_name}\s*\):")
            matches = inheritance_pattern.findall(content)
            if matches:
                content = inheritance_pattern.sub(r"class \1(SovereignBaseAgent):", content)
                for class_name in matches:
                    changes_made.append(
                        f"Inheritance: class {class_name}({legacy_name}) -> class {class_name}(SovereignBaseAgent)",
                    )
                modified = True

            # Replace references in comments and docstrings
            if legacy_name in content:
                # Replace in comments and docstrings but not in strings
                lines = content.splitlines()
                for i, line in enumerate(lines):
                    if legacy_name in line:
                        # Check if it's a comment or docstring
                        stripped = line.strip()
                        if (
                            stripped.startswith("#")
                            or stripped.startswith('"""')
                            or stripped.startswith("'''")
                            or '"""' in line
                            or "'''" in line
                        ):
                            # Replace the legacy name with SovereignBaseAgent in comments/docstrings
                            lines[i] = line.replace(legacy_name, "SovereignBaseAgent")
                            changes_made.append(f"Comment/Docstring: {legacy_name} -> SovereignBaseAgent")
                            modified = True
                content = "\n".join(lines)

        # Write back if modified
        if modified:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Refactored: {file_path}")
            for change in changes_made:
                print(f"   - {change}")

        return modified, changes_made

    # guardian: allow-silent-swallow
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False, [f"Error: {e}"]


def main():
    """Main refactoring function."""
    print("=" * 80)
    print("PHASE 4: GLOBAL REFACTOR - LEGACY BASE CLASS REMOVAL")
    print("=" * 80)

    # Target directory
    agentic_core = Path("agentic_core")

    if not agentic_core.exists():
        print(f"❌ Directory not found: {agentic_core}")
        return False

    # Find all Python files
    python_files = find_python_files(agentic_core)
    print(f"📁 Found {len(python_files)} Python files to process")

    # Refactor files
    files_modified = 0
    total_changes = 0

    for file_path in python_files:
        modified, changes = refactor_file(file_path)
        if modified:
            files_modified += 1
            total_changes += len(changes)

    print("\n" + "=" * 80)
    print("REFACTOR SUMMARY:")
    print(f"  Files processed: {len(python_files)}")
    print(f"  Files modified: {files_modified}")
    print(f"  Total changes: {total_changes}")
    print("=" * 80)

    return files_modified > 0


if __name__ == "__main__":
    main()
