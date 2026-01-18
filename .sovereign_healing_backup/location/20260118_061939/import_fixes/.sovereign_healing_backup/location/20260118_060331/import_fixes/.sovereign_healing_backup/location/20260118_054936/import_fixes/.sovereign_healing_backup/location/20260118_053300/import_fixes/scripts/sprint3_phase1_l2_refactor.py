#!/usr/bin/env python3
"""
Sprint 3 - Phase 1: L2 → L5 Quick Win

Batch refactor all L2 execution layer files to use MCPHardenedMixin
from utils/core_extensions instead of L5_safety/guardrails.

Target: 27 violations (35 files found)
Expected: +2.2% compliance
"""

from pathlib import Path

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)

REPO = Path(__file__).parent.parent

# Old import (L2 → L5 violation)
OLD_IMPORT = "from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin"

# New import (utils - foundational)
NEW_IMPORT = "from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin"

def refactor_file(file_path: Path) -> bool:
    """Replace L5 MCPHardenedMixin import with utils location."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        if OLD_IMPORT not in content:
            return False
        
        # Replace the import
        new_content = content.replace(OLD_IMPORT, NEW_IMPORT)
        
        # Write back
        file_path.write_text(new_content, encoding='utf-8')
        
        print(f"✅ Fixed: {file_path.relative_to(REPO)}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {file_path.name}: {e}")
        return False

def main():
    """Refactor all L2 files with MCPHardenedMixin imports."""
    
    print("=" * 80)
    print("  Sprint 3 - Phase 1: L2 → L5 Quick Win")
    print("=" * 80)
    print()
    print(f"Old: {OLD_IMPORT}")
    print(f"New: {NEW_IMPORT}")
    print()
    
    # Find all Python files in L2_execution
    l2_dir = REPO / AGENTIC_CORE_DIR / "L2_execution"
    
    if not l2_dir.exists():
        print(f"❌ Directory not found: {l2_dir}")
        return 1
    
    files_modified = 0
    files_scanned = 0
    
    # Recursively find all .py files
    for py_file in l2_dir.rglob("*.py"):
        if py_file.name.startswith("_") or ".backup" in py_file.name:
            continue
        
        files_scanned += 1
        if refactor_file(py_file):
            files_modified += 1
    
    print()
    print("=" * 80)
    print("  Phase 1 Summary")
    print("=" * 80)
    print(f"Files scanned: {files_scanned}")
    print(f"Files modified: {files_modified}")
    print()
    
    if files_modified > 0:
        print("✅ Phase 1 complete!")
        print()
        print("Expected impact:")
        print("  • ~27 L2→L5 violations eliminated")
        print("  • Compliance gain: ~+2.2%")
        print()
        print("Next: Verify compliance improvement")
        print("  python scripts/ssot.py validate --summary")
    else:
        print("ℹ️  No files needed refactoring")
    
    return 0

if __name__ == "__main__":
    exit(main())
