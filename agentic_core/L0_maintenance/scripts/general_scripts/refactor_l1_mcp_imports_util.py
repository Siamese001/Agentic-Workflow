#!/usr/bin/env python3
"""
Sprint 1: L1 → L5 MCPHardenedMixin Refactoring

Updates all L1 cognition files to use MCPHardenedMixin from utils/core_extensions
instead of L5_safety/guardrails.

Target: ~27 L1 → L5 violations
"""

from pathlib import Path

from agentic_core.L5_safety.validators.structure_blueprint_config import (
    AGENTIC_CORE_DIR,
)

REPO = Path(__file__).parent.parent

# Old import (L5 - violates hierarchy)
OLD_IMPORT = "from agentic_core.mixins.mcp_hardened_mixin import MCPHardenedMixin"

# New import (utils - foundational)
NEW_IMPORT = "from agentic_core.mixins.mcp_hardened_mixin import MCPHardenedMixin"


def refactor_file(file_path: Path) -> bool:
    """Replace L5 MCPHardenedMixin import with utils location."""
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
        print(f"❌ Error: {file_path.name}: {e}")
        return False


def main():
    """Refactor all L1 files with MCPHardenedMixin imports."""

    print("=" * 80)
    print("  Sprint 1: L1 → L5 MCPHardenedMixin Refactoring")
    print("=" * 80)
    print()
    print(f"Old: {OLD_IMPORT}")
    print(f"New: {NEW_IMPORT}")
    print()

    # Find all Python files in L1_cognition
    l1_dir = REPO / AGENTIC_CORE_DIR / "L1_cognition"

    if not l1_dir.exists():
        print(f"❌ Directory not found: {l1_dir}")
        return 1

    files_modified = 0
    files_scanned = 0

    # Recursively find all .py files
    # Phase 6.7: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery_validator import get_python_files

    for py_file in get_python_files(l1_dir):
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
        print("✅ L1 refactoring complete!")
        print()
        print("Next: Verify compliance improvement")
        print("  python scripts/ssot.py validate --summary")
    else:
        print("ℹ️  No files needed refactoring")

    return 0


if __name__ == "__main__":
    exit(main())
