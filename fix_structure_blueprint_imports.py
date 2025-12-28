#!/usr/bin/env python3
"""
Fix all remaining structure_blueprint imports after P1_core relocation
"""
import re
from pathlib import Path

project_root = Path(__file__).parent

# Pattern 1: sys.path.insert with P1_core
pattern1 = r'sys\.path\.insert\(0, str\(.*?["\']config["\']\s*\/\s*["\']P1_core["\']\)\)'
replacement1 = '# Path insert no longer needed - using absolute import'

# Pattern 2: from structure_blueprint import
pattern2 = r'from structure_blueprint import'
replacement2 = 'from agentic_core.config.blueprint_sovereign.structure_blueprint import'

# Pattern 3: sys.path.append with P1_core
pattern3 = r'sys\.path\.append\(BLUEPRINT_DIR\)'
replacement3 = '# Path append no longer needed - using absolute import'

files_updated = []
files_checked = 0

# Search all Python files in agentic_core
for py_file in (project_root / 'agentic_core').rglob("*.py"):
    if '__pycache__' in str(py_file) or 'archives' in str(py_file):
        continue
    
    try:
        content = py_file.read_text(encoding='utf-8')
        original_content = content
        files_checked += 1
        
        # Apply fixes
        content = re.sub(pattern1, replacement1, content)
        content = re.sub(pattern2, replacement2, content)
        content = re.sub(pattern3, replacement3, content)
        
        # Also fix BLUEPRINT_DIR definitions
        content = re.sub(
            r'BLUEPRINT_DIR = .*?["\']config["\']\s*\/\s*["\']P1_core["\']',
            'BLUEPRINT_DIR = str(Path(__file__).resolve().parent.parent.parent / "config" / "blueprint_sovereign")',
            content
        )
        
        if content != original_content:
            py_file.write_text(content, encoding='utf-8')
            files_updated.append(str(py_file.relative_to(project_root)))
            print(f"✓ Updated: {py_file.relative_to(project_root)}")
    
    except Exception as e:
        print(f"✗ Error processing {py_file.name}: {e}")

print(f"\n{'='*70}")
print(f"STRUCTURE_BLUEPRINT IMPORT FIX SUMMARY")
print(f"{'='*70}")
print(f"Files checked: {files_checked}")
print(f"Files updated: {len(files_updated)}")

if files_updated:
    print(f"\nUpdated files:")
    for f in files_updated:
        print(f"  • {f}")
else:
    print("\n✓ No files needed updating")
