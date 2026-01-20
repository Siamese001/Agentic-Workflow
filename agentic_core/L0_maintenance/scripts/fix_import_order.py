#!/usr/bin/env python3
"""
Fix import order issues caused by previous script.
Ensure SubatomicTestingMixin import comes AFTER __future__ imports.
"""
import re
from pathlib import Path
from agentic_core.utils.sovereign_index import SovereignIndex

# Find all Python files that have the problematic import pattern
problematic_pattern = r'from agentic_core\.utils\.core_extensions\.subatomic_testing_mixin import SubatomicTestingMixin\s*\n.*from __future__'

# Get all agent files
agent_dirs = [
    'apps_lic',
    'apps_rg', 
    'apps_shared',
    'agentic_core'
]

fixed_count = 0
error_count = 0

for base_dir in agent_dirs:
    base_path = Path(base_dir)
    if not base_path.exists():
        continue
    
    # Phase 6.9: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files
    for py_file in get_python_files(base_path):
        try:
            content = py_file.read_text(encoding='utf-8')
            
            # Check if file has the SubatomicTestingMixin import
            if 'from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin' not in content:
                continue
            
            # Check if there's a __future__ import
            if 'from __future__' not in content:
                continue
            
            # Get all lines
            lines = content.split('\n')
            
            # Find the SubatomicTestingMixin import line
            subatomic_line_idx = None
            future_line_idx = None
            last_import_idx = 0
            
            for i, line in enumerate(lines):
                if 'from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin' in line:
                    subatomic_line_idx = i
                if 'from __future__' in line:
                    future_line_idx = i
                if line.startswith('import ') or line.startswith('from '):
                    last_import_idx = i
            
            # If SubatomicTestingMixin import is BEFORE __future__ import, we need to fix
            if subatomic_line_idx is not None and future_line_idx is not None:
                if subatomic_line_idx < future_line_idx:
                    # Remove the SubatomicTestingMixin import line
                    subatomic_import = lines[subatomic_line_idx]
                    lines.pop(subatomic_line_idx)
                    
                    # Recalculate indices after removal
                    future_line_idx = None
                    last_import_idx = 0
                    for i, line in enumerate(lines):
                        if 'from __future__' in line:
                            future_line_idx = i
                        if line.startswith('import ') or line.startswith('from '):
                            last_import_idx = i
                    
                    # Insert after all __future__ imports but at beginning of other imports
                    # Find the first non-future import after __future__
                    insert_idx = future_line_idx + 1
                    while insert_idx < len(lines) and (lines[insert_idx].strip() == '' or lines[insert_idx].startswith('from __future__')):
                        insert_idx += 1
                    
                    lines.insert(insert_idx, subatomic_import)
                    
                    # Write back
                    py_file.write_text('\n'.join(lines), encoding='utf-8')
                    print(f"✅ Fixed: {py_file}")
                    fixed_count += 1
                    
        except Exception as e:
            print(f"❌ Error with {py_file}: {e}")
            error_count += 1

print(f"\n{'='*70}")
print(f"SUMMARY")
print(f"{'='*70}")
print(f"Fixed: {fixed_count}")
print(f"Errors: {error_count}")
