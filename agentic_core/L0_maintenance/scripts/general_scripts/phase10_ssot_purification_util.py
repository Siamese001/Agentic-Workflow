#!/usr/bin/env python3
"""
Phase 10: SSOT Registry Purification

Scans and purges all remaining "Unified" string references and transitional logic
from structure_blueprint.py and other SSOT registries.
"""

import re
from pathlib import Path


def phase10_ssot_purification():
    """Execute Phase 10: Purge Unified references from SSOT registries."""
    project_root = Path(__file__).resolve().parents[3]

    print("=" * 80)
    print("PHASE 10: SSOT REGISTRY PURIFICATION")
    print("=" * 80)
    print(f"Project Root: {project_root}")
    print()

    files_purified = 0
    references_removed = 0

    # Target SSOT files
    ssot_files = [
        project_root / "agentic_core/L5_safety/validators/structure_blueprint.py",
        project_root / "agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py",
        project_root / "agentic_core/config/core/hygiene_registry_config.py",
    ]

    print("--- SSOT Files to Purify ---")
    for ssot_file in ssot_files:
        if ssot_file.exists():
            print(f"  ✓ {ssot_file.relative_to(project_root)}")
        else:
            print(f"  ✗ {ssot_file.relative_to(project_root)} (not found)")
    print()

    # Purification patterns
    purifications = [
        # Comments mentioning "unified"
        (
            re.compile(r"# .*[Uu]nified.*orchestrator.*", re.IGNORECASE),
            "# Orchestrator at layer root",
        ),
        # Variable names with "unified"
        (re.compile(r"unified_orchestrator\.py"), "orchestrator.py"),
        # Documentation strings
        (re.compile(r"UNIFIED SOVEREIGN", re.IGNORECASE), "SOVEREIGN"),
    ]

    print("--- Purifying SSOT Registries ---")
    for ssot_file in ssot_files:
        if not ssot_file.exists():
            continue

        try:
            content = ssot_file.read_text(encoding="utf-8")
            original_content = content
            local_changes = 0

            for pattern, replacement in purifications:
                matches = pattern.findall(content)
                if matches:
                    local_changes += len(matches)
                    content = pattern.sub(replacement, content)

            if content != original_content:
                ssot_file.write_text(content, encoding="utf-8")
                print(f"[PURIFIED] {ssot_file.relative_to(project_root)} ({local_changes} references)")
                files_purified += 1
                references_removed += local_changes
            else:
                print(f"[CLEAN] {ssot_file.relative_to(project_root)}")
        except Exception as e:
            print(f"[ERROR] {ssot_file.relative_to(project_root)}: {e}")

    print()
    print("=" * 80)
    print("PHASE 10 STATISTICS")
    print("=" * 80)
    print(f"Files Purified: {files_purified}")
    print(f"References Removed: {references_removed}")
    print()
    print("=" * 80)
    print("PHASE 10: COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    phase10_ssot_purification()
