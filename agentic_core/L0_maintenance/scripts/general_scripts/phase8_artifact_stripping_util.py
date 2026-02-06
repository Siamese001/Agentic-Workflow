#!/usr/bin/env python3
"""
Phase 8: Artifact Stripping & Domain Relocation

Relocates and renames the 5 remaining "Unified" artifacts to their sovereign
domain directories and strips all transitional prefixes.

Targets:
1. HygieneMixin.py -> HygieneMixin.py (base_agents/)
2. Orchestrator.py -> Orchestrator.py (L3_orchestration/)
3. CheckpointManagerAgent.py -> CheckpointManagerAgent.py (L4_state/validation_context/)
4. StateManagementAgent.py -> StateManagementAgent.py (L4_state/validation_context/)
5. ASTValidatorAgent.py -> ASTValidatorAgent.py (L1_cognition/thought_engine/)
"""

import re
import shutil
from pathlib import Path


def phase8_artifact_stripping():
    """Execute Phase 8: Strip Unified prefixes from remaining artifacts."""
    project_root = Path(__file__).resolve().parents[3]

    print("=" * 80)
    print("PHASE 8: ARTIFACT STRIPPING & DOMAIN RELOCATION")
    print("=" * 80)
    print(f"Project Root: {project_root}")
    print()

    # Define artifact mappings (same directory, just rename)
    ARTIFACT_MAPPINGS = [
        {
            "old": "agentic_core/base_agents/HygieneMixin.py",
            "new": "agentic_core/base_agents/HygieneMixin.py",
            "class_old": "HygieneMixin",
            "class_new": "HygieneMixin",
        },
        {
            "old": "agentic_core/L3_orchestration/Orchestrator.py",
            "new": "agentic_core/L3_orchestration/Orchestrator.py",
            "class_old": "Orchestrator",
            "class_new": "Orchestrator",
        },
        {
            "old": "agentic_core/L4_state/validation_context/CheckpointManagerAgent.py",
            "new": "agentic_core/L4_state/validation_context/CheckpointManagerAgent.py",
            "class_old": "CheckpointManagerAgent",
            "class_new": "CheckpointManagerAgent",
        },
        {
            "old": "agentic_core/L4_state/validation_context/StateManagementAgent.py",
            "new": "agentic_core/L4_state/validation_context/StateManagementAgent.py",
            "class_old": "StateManagementAgent",
            "class_new": "StateManagementAgent",
        },
        {
            "old": "agentic_core/L1_cognition/thought_engine/ASTValidatorAgent.py",
            "new": "agentic_core/L1_cognition/thought_engine/ASTValidatorAgent.py",
            "class_old": "ASTValidatorAgent",
            "class_new": "ASTValidatorAgent",
        },
    ]

    files_renamed = 0
    files_refactored = 0

    # Step 1: Rename files
    print("--- STEP 1: File Renaming ---")
    for mapping in ARTIFACT_MAPPINGS:
        old_path = project_root / mapping["old"]
        new_path = project_root / mapping["new"]

        if old_path.exists():
            if not new_path.exists():
                shutil.move(str(old_path), str(new_path))
                print(f"[RENAMED] {mapping['old']} -> {mapping['new']}")
                files_renamed += 1
            else:
                print(f"[SKIP] {mapping['new']} already exists")
        else:
            print(f"[MISSING] {mapping['old']} not found")

    print()
    print("--- STEP 2: Deep Content Refactoring ---")

    # Build regex patterns for class name replacements
    replacements = []
    for mapping in ARTIFACT_MAPPINGS:
        # Match class definitions and imports
        replacements.append((re.compile(rf"\b{mapping['class_old']}\b"), mapping["class_new"]))
        # Match file imports
        old_import = mapping["old"].replace("/", ".")
        new_import = mapping["new"].replace("/", ".")
        replacements.append((re.compile(rf"{old_import}"), new_import))

    # Refactor all Python files
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
    print("PHASE 8 STATISTICS")
    print("=" * 80)
    print(f"Files Renamed: {files_renamed}")
    print(f"Files Refactored: {files_refactored}")
    print()
    print("=" * 80)
    print("PHASE 8: COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    phase8_artifact_stripping()
