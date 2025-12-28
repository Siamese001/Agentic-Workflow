#!/usr/bin/env python3
"""
Fix all imports from agentic_core.config.P1_core to agentic_core.config.blueprint_sovereign
"""
import re
from pathlib import Path

project_root = Path(__file__).parent

# Pattern to match the old import path
old_pattern = r'from agentic_core\.config\.P1_core\.'
new_replacement = r'from agentic_core.config.blueprint_sovereign.'

# Also handle direct imports
old_pattern2 = r'import agentic_core\.config\.P1_core\.'
new_replacement2 = r'import agentic_core.config.blueprint_sovereign.'

files_updated = []
files_checked = 0

# Search all Python files
for py_file in project_root.rglob("*.py"):
    # Skip protected folders
    if any(p in str(py_file) for p in ['.git', '__pycache__', 'venv', '.venv', 'archives']):
        continue
    
    try:
        content = py_file.read_text(encoding='utf-8')
        original_content = content
        files_checked += 1
        
        # Replace old imports
        content = re.sub(old_pattern, new_replacement, content)
        content = re.sub(old_pattern2, new_replacement2, content)
        
        if content != original_content:
            py_file.write_text(content, encoding='utf-8')
            files_updated.append(str(py_file.relative_to(project_root)))
            print(f"✓ Updated: {py_file.relative_to(project_root)}")
    
    except Exception as e:
        print(f"✗ Error processing {py_file.name}: {e}")

print(f"\n{'='*70}")
print(f"IMPORT UPDATE SUMMARY")
print(f"{'='*70}")
print(f"Files checked: {files_checked}")
print(f"Files updated: {len(files_updated)}")

if files_updated:
    print(f"\nUpdated files:")
    for f in files_updated:
        print(f"  • {f}")
else:
    print("\n✓ No files needed updating")
