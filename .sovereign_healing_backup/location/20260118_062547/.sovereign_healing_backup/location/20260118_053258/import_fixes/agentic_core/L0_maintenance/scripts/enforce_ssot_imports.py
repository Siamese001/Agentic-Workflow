from __future__ import annotations
#!/usr/bin/env python3
"""
SSOT Enforcement Script
Adds structure_blueprint.py import to files that reference L0-L5 layers 
but don't already import from SSOT.
"""
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
AGENTIC_CORE = PROJECT_ROOT / "agentic_core"

# The SSOT import block to add
SSOT_IMPORT = '''# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.validators.structure_blueprint_1 import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)
'''

# Pattern to detect layer references
LAYER_PATTERN = re.compile(r'L[0-5]_')

# Pattern to detect existing SSOT import
SSOT_IMPORT_PATTERN = re.compile(r'from agentic_core\.config\.blueprint_sovereign\.structure_blueprint')

def needs_ssot_import(content: str) -> bool:
    """Check if file references layers but doesn't import SSOT."""
    has_layer_ref = bool(LAYER_PATTERN.search(content))
    has_ssot_import = bool(SSOT_IMPORT_PATTERN.search(content))
    return has_layer_ref and not has_ssot_import

def add_ssot_import(file_path: Path) -> bool:
    """Add SSOT import to a file if needed."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception:
        return False
    
    if not needs_ssot_import(content):
        return False
    
    # Skip the SSOT file itself
    if 'structure_blueprint.py' in str(file_path):
        return False
    
    # Skip __init__.py files (usually just re-exports)
    if file_path.name == '__init__.py':
        return False
    
    # Find insertion point (after existing imports, before class/def)
    lines = content.split('\n')
    insert_idx = 0
    
    # Find last import line
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            insert_idx = i + 1
        elif line.startswith('class ') or line.startswith('def '):
            break
    
    # Insert SSOT import
    lines.insert(insert_idx, '')
    lines.insert(insert_idx + 1, SSOT_IMPORT)
    
    new_content = '\n'.join(lines)
    file_path.write_text(new_content, encoding='utf-8')
    return True

def main():
    """Process all Python files in agentic_core, tests, apps_shared, apps_rg, apps_lic."""
    updated = 0
    skipped = 0
    
    # Process all sovereign territories
    territories = [
        AGENTIC_CORE,
        PROJECT_ROOT / "tests",
        PROJECT_ROOT / "apps_shared",
        PROJECT_ROOT / "apps_rg",
        PROJECT_ROOT / "apps_lic",
    ]
    
    for territory in territories:
        if not territory.exists():
            continue
        
        for py_file in territory.rglob('*.py'):
            # Skip certain directories
            if any(x in str(py_file) for x in ['__pycache__', '.git', 'archives']):
                continue
            
            if add_ssot_import(py_file):
                print(f"[UPDATED] {py_file.relative_to(PROJECT_ROOT)}")
                updated += 1
            else:
                skipped += 1
    
    print(f"\n[DONE] Updated {updated} files, skipped {skipped}")

if __name__ == "__main__":
    main()
