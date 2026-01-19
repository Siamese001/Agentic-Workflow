#!/usr/bin/env python3
"""
Fix corrupted agent files where imports are in wrong order.
Ensures proper Python file structure:
1. Docstring (if any)
2. from __future__ imports
3. Standard library imports
4. Third-party imports
5. Local imports (including SubatomicTestingMixin)
"""
import re
from pathlib import Path
from archives.location_violations.sovereign_index import SovereignIndex

def fix_file(py_file: Path) -> bool:
    """Fix a single Python file's import order."""
    try:
        content = py_file.read_text(encoding='utf-8')
        
        # Skip if no SubatomicTestingMixin import
        if 'SubatomicTestingMixin' not in content:
            return False
        
        lines = content.split('\n')
        
        # Separate into sections
        docstring_lines = []
        future_imports = []
        other_imports = []
        code_lines = []
        
        in_docstring = False
        docstring_delim_count = 0
        past_imports = False
        
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Handle docstring at start
            if i == 0 or (not docstring_lines and not future_imports and not other_imports):
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    # Multi-line docstring
                    delim = stripped[:3]
                    if stripped.count(delim) >= 2 and len(stripped) > 6:
                        # Single line docstring
                        docstring_lines.append(line)
                        i += 1
                        continue
                    else:
                        # Multi-line docstring start
                        in_docstring = True
                        docstring_lines.append(line)
                        i += 1
                        continue
            
            if in_docstring:
                docstring_lines.append(line)
                if '"""' in line or "'''" in line:
                    in_docstring = False
                i += 1
                continue
            
            # After docstring, categorize lines
            if stripped.startswith('from __future__'):
                future_imports.append(line)
            elif stripped.startswith('import ') or stripped.startswith('from '):
                if not past_imports:
                    other_imports.append(line)
                else:
                    code_lines.append(line)
            elif stripped == '' and not past_imports:
                # Empty line in import section - skip
                pass
            elif stripped.startswith('@') or stripped.startswith('class ') or stripped.startswith('def '):
                past_imports = True
                code_lines.append(line)
            elif past_imports or (stripped and not stripped.startswith('#')):
                past_imports = True
                code_lines.append(line)
            else:
                if not past_imports:
                    # Comment in import area
                    other_imports.append(line)
                else:
                    code_lines.append(line)
            
            i += 1
        
        # Rebuild file with correct order
        new_lines = []
        
        # 1. Docstring
        if docstring_lines:
            new_lines.extend(docstring_lines)
            if not docstring_lines[-1].strip() == '':
                new_lines.append('')
        
        # 2. __future__ imports
        if future_imports:
            new_lines.extend(future_imports)
        
        # 3. Other imports (ensure SubatomicTestingMixin is included)
        subatomic_import = 'from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin'
        has_subatomic = any(subatomic_import in imp for imp in other_imports)
        
        # Filter out any misplaced imports that ended up in wrong place
        clean_imports = [imp for imp in other_imports if imp.strip() and not imp.strip().startswith('#')]
        
        if clean_imports:
            new_lines.extend(clean_imports)
        
        if not has_subatomic:
            new_lines.append(subatomic_import)
        
        # Add blank line before code
        if new_lines and new_lines[-1].strip():
            new_lines.append('')
        
        # 4. Rest of code
        # Remove leading empty lines from code
        while code_lines and not code_lines[0].strip():
            code_lines.pop(0)
        
        new_lines.extend(code_lines)
        
        new_content = '\n'.join(new_lines)
        
        # Only write if changed
        if new_content != content:
            py_file.write_text(new_content, encoding='utf-8')
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error with {py_file}: {e}")
        return False

# Get all agent files
agent_dirs = [
    'apps_lic',
    'apps_rg', 
    'apps_shared',
    'agentic_core'
]

fixed_count = 0

for base_dir in agent_dirs:
    base_path = Path(base_dir)
    if not base_path.exists():
        continue
    
    # Phase 6.9: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files
    for py_file in get_python_files(base_path):
        if fix_file(py_file):
            print(f"✅ Fixed: {py_file}")
            fixed_count += 1

print(f"\n{'='*70}")
print(f"Fixed {fixed_count} files")
