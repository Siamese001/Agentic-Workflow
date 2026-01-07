#!/usr/bin/env python3
"""
Update SubatomicTestingMixin imports across the codebase
Changes: L2_execution/ToolRegistry -> L0_maintenance/mixins
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent

OLD_IMPORT = "from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import"
NEW_IMPORT = "from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import"

files_updated = 0
total_replacements = 0

for py_file in project_root.rglob("*.py"):
    if "__pycache__" in py_file.parts:
        continue
    
    try:
        content = py_file.read_text(encoding="utf-8")
        
        if OLD_IMPORT in content:
            new_content = content.replace(OLD_IMPORT, NEW_IMPORT)
            replacements = content.count(OLD_IMPORT)
            
            py_file.write_text(new_content, encoding="utf-8")
            files_updated += 1
            total_replacements += replacements
            
            print(f"✅ Updated: {py_file.relative_to(project_root)} ({replacements} replacement(s))")
    
    except Exception as e:
        print(f"❌ Failed: {py_file.relative_to(project_root)} - {e}")

print(f"\n{'=' * 80}")
print(f"IMPORT UPDATE COMPLETE")
print(f"{'=' * 80}")
print(f"Files updated: {files_updated}")
print(f"Total replacements: {total_replacements}")
