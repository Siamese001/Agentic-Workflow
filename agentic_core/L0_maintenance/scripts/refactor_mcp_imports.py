#!/usr/bin/env python3
"""
Batch Refactoring Script - Fix MCPHardenedMixin Import Violations

Updates all L0 files to use the new MCPHardenedMixin location in utils/core_extensions
instead of L5_safety/guardrails (which violates layer hierarchy).

This fixes ~10 critical L0 → L5 upward dependency violations.
"""

from pathlib import Path

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
)

# Project root
REPO = Path(__file__).parent.parent

# Old import pattern (L5 - violates hierarchy)
OLD_IMPORT = "from agentic_core.L2_execution.mcp.mcp_hardened_mixin import MCPHardenedMixin"

# New import pattern (utils - foundational layer)
NEW_IMPORT = "from agentic_core.L2_execution.mcp.mcp_hardened_mixin import MCPHardenedMixin"


def refactor_file(file_path: Path) -> bool:
    """
    Replace old MCPHardenedMixin import with new location.

    Returns:
        True if file was modified, False otherwise
    """
    try:
        content = file_path.read_text(encoding="utf-8")

        if OLD_IMPORT not in content:
            return False

        # Replace the import
        new_content = content.replace(OLD_IMPORT, NEW_IMPORT)

        # Write back
        file_path.write_text(new_content, encoding="utf-8")

        print(f"✅ Fixed: {file_path.relative_to(REPO)}")
        return True

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False


def main():
    """Refactor all L0 files with MCPHardenedMixin imports."""

    print("=" * 80)
    print("  MCPHardenedMixin Import Refactoring")
    print("=" * 80)
    print()
    print(f"Old import: {OLD_IMPORT}")
    print(f"New import: {NEW_IMPORT}")
    print()

    # Find all Python files in L0_maintenance/scripts
    l0_scripts = REPO / AGENTIC_CORE_DIR / "L0_maintenance" / SCRIPTS_DIR

    if not l0_scripts.exists():
        print(f"❌ Directory not found: {l0_scripts}")
        return 1

    files_modified = 0
    files_scanned = 0

    # Phase 6.9 Sub-50: Use ssot_discovery instead of glob
    from agentic_core.utils.ssot_discovery import get_python_files

    for py_file in get_python_files(l0_scripts):
        if py_file.name.startswith("_"):
            continue

        files_scanned += 1
        if refactor_file(py_file):
            files_modified += 1

    print()
    print("=" * 80)
    print("  Summary")
    print("=" * 80)
    print(f"Files scanned: {files_scanned}")
    print(f"Files modified: {files_modified}")
    print()

    if files_modified > 0:
        print("✅ Refactoring complete!")
        print()
        print("Next steps:")
        print("  1. Run: python scripts/ssot.py validate --summary")
        print("  2. Verify import violations decreased")
        print("  3. Test affected agents to ensure functionality")
    else:
        print("ℹ️  No files needed refactoring")

    return 0


if __name__ == "__main__":
    exit(main())
