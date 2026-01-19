#!/usr/bin/env python3
"""
Sprint 1: L1 → L5 MCPHardenedMixin Refactoring

Updates all L1 cognition files to use MCPHardenedMixin from utils/core_extensions
instead of L5_safety/guardrails.

Target: ~27 L1 → L5 violations
"""

from pathlib import Path

from agentic_core.L5_safety.validators.structure_blueprint import (
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
from archives.location_violations.sovereign_index import SovereignIndex

REPO = Path(__file__).parent.parent

# Old import (L5 - violates hierarchy)
OLD_IMPORT = "from agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin"

# New import (utils - foundational)
NEW_IMPORT = "from agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin"

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
    for py_file in l1_dir.rglob("*.py"):
        if py_file.name.startswith("_") or ".backup" in py_file.name:
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
        print("✅ L1 refactoring complete!")
        print()
        print("Next: Verify compliance improvement")
        print("  python scripts/ssot.py validate --summary")
    else:
        print("ℹ️  No files needed refactoring")
    
    return 0

if __name__ == "__main__":
    exit(main())
