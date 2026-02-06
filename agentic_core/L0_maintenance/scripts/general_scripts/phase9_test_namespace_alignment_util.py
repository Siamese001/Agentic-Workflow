#!/usr/bin/env python3
"""
Phase 9: Test Namespace Alignment

Renames all test_unified_*.py files to test_*.py and performs deep AST refactoring
of internal imports and class names to match sovereign standards.
"""

import re
import shutil
from pathlib import Path


def phase9_test_namespace_alignment():
    """Execute Phase 9: Rename test files and refactor imports."""
    project_root = Path(__file__).resolve().parents[3]

    print("=" * 80)
    print("PHASE 9: TEST NAMESPACE ALIGNMENT")
    print("=" * 80)
    print(f"Project Root: {project_root}")
    print()

    # Find all test_unified_*.py files (excluding archives)
    test_files = []
    for test_file in project_root.rglob("test_unified_*.py"):
        if "archives" not in str(test_file):
            test_files.append(test_file)

    print(f"Found {len(test_files)} test files to rename")
    print()

    files_renamed = 0
    files_refactored = 0

    # Step 1: Rename test files
    print("--- STEP 1: Test File Renaming ---")
    renamed_mappings = []

    for test_file in test_files:
        # Generate new name by removing "unified_" prefix
        new_name = test_file.name.replace("test_unified_", "test_")
        new_path = test_file.parent / new_name

        if not new_path.exists():
            shutil.move(str(test_file), str(new_path))
            print(f"[RENAMED] {test_file.relative_to(project_root)} -> {new_name}")
            renamed_mappings.append(
                {
                    "old": str(test_file.relative_to(project_root)),
                    "new": str(new_path.relative_to(project_root)),
                },
            )
            files_renamed += 1
        else:
            print(f"[SKIP] {new_name} already exists")

    print()
    print("--- STEP 2: Deep Import Refactoring ---")

    # Build replacement patterns for class names from Phase 8
    replacements = [
        # Phase 8 artifact class names
        (re.compile(r"\bUnifiedHygieneMixin\b"), "HygieneMixin"),
        (re.compile(r"\bUnifiedOrchestratorAgent\b"), "Orchestrator"),
        (re.compile(r"\bUnifiedCheckpointManagerAgent\b"), "CheckpointManagerAgent"),
        (re.compile(r"\bUnifiedStateManagementAgent\b"), "StateManagementAgent"),
        (re.compile(r"\bUnifiedASTValidatorAgent\b"), "ASTValidatorAgent"),
        # Phase 8 import paths
        (
            re.compile(r"agentic_core\.base_agents\.UnifiedHygieneMixin"),
            "agentic_core.base_agents.HygieneMixin",
        ),
        (
            re.compile(r"agentic_core\.L3_orchestration\.UnifiedOrchestratorAgent"),
            "agentic_core.L3_orchestration.Orchestrator",
        ),
        (
            re.compile(r"agentic_core\.L4_state\.validation_context\.UnifiedCheckpointManagerAgent"),
            "agentic_core.L4_state.validation_context.CheckpointManagerAgent",
        ),
        (
            re.compile(r"agentic_core\.L4_state\.validation_context\.UnifiedStateManagementAgent"),
            "agentic_core.L4_state.validation_context.StateManagementAgent",
        ),
        (
            re.compile(r"agentic_core\.L1_cognition\.thought_engine\.UnifiedASTValidatorAgent"),
            "agentic_core.L1_cognition.agents.ASTValidatorAgent",
        ),
    ]

    # Refactor all Python files (tests and source)
    for py_file in project_root.rglob("*.py"):
        if "archives" in str(py_file) or "__pycache__" in str(py_file):
            continue

        if py_file.name == Path(__file__).name:
            continue

        try:
            content = py_file.read_text(encoding="utf-8")
            original_content = content

            for pattern, replacement in replacements:
                content = pattern.sub(replacement, content)

            if content != original_content:
                py_file.write_text(content, encoding="utf-8")
                print(f"[REFACTOR] {py_file.relative_to(project_root)}")
                files_refactored += 1
        except Exception as e:
            print(f"[ERROR] {py_file.relative_to(project_root)}: {e}")

    print()
    print("=" * 80)
    print("PHASE 9 STATISTICS")
    print("=" * 80)
    print(f"Test Files Renamed: {files_renamed}")
    print(f"Files Refactored: {files_refactored}")
    print()
    print("=" * 80)
    print("PHASE 9: COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    phase9_test_namespace_alignment()
