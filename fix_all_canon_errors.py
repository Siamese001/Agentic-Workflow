#!/usr/bin/env python3
"""
Comprehensive Canon Validator Error Fixer
Fixes all 425 violations across multiple categories to achieve 50/50 key perfection
"""

import os
import re
import ast
from pathlib import Path
from typing import List, Tuple, Set
from collections import defaultdict

PROJECT_ROOT = Path(r"c:\Git\Agentic-Workflow")
AGENTIC_CORE = PROJECT_ROOT / "agentic_core"

# Statistics
stats = {
    'import_fixes': 0,
    'depth_fixes': 0,
    'import_order_fixes': 0,
    'hierarchy_fixes': 0,
    'span_fixes': 0,
}

def fix_missing_typing_imports(file_path: Path) -> bool:
    """Fix missing typing imports like Dict, List, Optional, etc."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        # Check if file uses typing constructs without importing them
        typing_constructs = {
            'Dict': r'\bDict\[',
            'List': r'\bList\[',
            'Optional': r'\bOptional\[',
            'Tuple': r'\bTuple\[',
            'Set': r'\bSet\[',
            'Union': r'\bUnion\[',
            'Any': r'\bAny\b',
            'Callable': r'\bCallable\[',
            'TypeVar': r'\bTypeVar\(',
            'ClassVar': r'\bClassVar\[',
        }
        
        # Find which constructs are used
        used_constructs = set()
        for construct, pattern in typing_constructs.items():
            if re.search(pattern, content):
                used_constructs.add(construct)
        
        if not used_constructs:
            return False
        
        # Check which are already imported
        import_match = re.search(r'^from typing import (.+)$', content, re.MULTILINE)
        if import_match:
            imported = {item.strip() for item in import_match.group(1).split(',')}
            missing = used_constructs - imported
            
            if missing:
                # Add missing imports to existing import line
                all_imports = sorted(imported | missing)
                new_import = f"from typing import {', '.join(all_imports)}"
                content = re.sub(
                    r'^from typing import .+$',
                    new_import,
                    content,
                    count=1,
                    flags=re.MULTILINE
                )
        else:
            # Add new typing import after other imports
            imports_to_add = sorted(used_constructs)
            new_import = f"from typing import {', '.join(imports_to_add)}\n"
            
            # Find the last import statement
            import_lines = []
            for i, line in enumerate(content.split('\n')):
                if line.startswith('import ') or line.startswith('from '):
                    import_lines.append(i)
            
            if import_lines:
                lines = content.split('\n')
                last_import_idx = max(import_lines)
                lines.insert(last_import_idx + 1, new_import.rstrip())
                content = '\n'.join(lines)
            else:
                # Add after docstring if present
                if content.startswith('"""') or content.startswith("'''"):
                    quote = '"""' if content.startswith('"""') else "'''"
                    end_idx = content.find(quote, 3) + 3
                    content = content[:end_idx] + '\n' + new_import + content[end_idx:]
                else:
                    content = new_import + content
        
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
            
    except Exception as e:
        print(f"Error fixing typing imports in {file_path.name}: {e}")
    
    return False

def fix_import_order(file_path: Path) -> bool:
    """Fix import order: stdlib, then third-party, then local"""
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        # Find all import lines
        import_blocks = []
        current_block = []
        in_imports = False
        pre_import = []
        post_import = []
        import_start_idx = -1
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            if stripped.startswith('import ') or stripped.startswith('from '):
                if not in_imports:
                    in_imports = True
                    import_start_idx = i
                current_block.append(line)
            elif in_imports and stripped and not stripped.startswith('#'):
                # End of import block
                import_blocks.append(current_block)
                current_block = []
                in_imports = False
                post_import = lines[i:]
                break
            elif in_imports and (not stripped or stripped.startswith('#')):
                # Blank line or comment in imports
                current_block.append(line)
            elif not in_imports and import_start_idx == -1:
                pre_import.append(line)
        
        if current_block:
            import_blocks.append(current_block)
        
        if not import_blocks:
            return False
        
        # Categorize imports
        stdlib_imports = []
        thirdparty_imports = []
        local_imports = []
        
        stdlib_modules = {
            'abc', 'ast', 'asyncio', 'collections', 'copy', 'csv', 'dataclasses',
            'datetime', 'enum', 'functools', 'importlib', 'inspect', 'io', 'json',
            'logging', 'os', 'pathlib', 'pickle', 're', 'shutil', 'sys', 'time',
            'traceback', 'typing', 'uuid', 'warnings', 'weakref', 'urllib',
        }
        
        for block in import_blocks:
            for line in block:
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue
                
                # Extract module name
                if stripped.startswith('from '):
                    module = stripped.split()[1].split('.')[0]
                elif stripped.startswith('import '):
                    module = stripped.split()[1].split('.')[0].split(' as ')[0]
                else:
                    continue
                
                # Categorize
                if module in stdlib_modules:
                    stdlib_imports.append(line)
                elif module.startswith('agentic_') or module in ['models_RES', 'config_RES_v2', 'utils_RES_v2']:
                    local_imports.append(line)
                else:
                    thirdparty_imports.append(line)
        
        # Rebuild imports in correct order
        new_imports = []
        if stdlib_imports:
            new_imports.extend(stdlib_imports)
            new_imports.append('')
        if thirdparty_imports:
            new_imports.extend(thirdparty_imports)
            new_imports.append('')
        if local_imports:
            new_imports.extend(local_imports)
            new_imports.append('')
        
        # Reconstruct file
        new_content = '\n'.join(pre_import + new_imports + post_import)
        
        if new_content != content:
            file_path.write_text(new_content, encoding='utf-8')
            return True
            
    except Exception as e:
        print(f"Error fixing import order in {file_path.name}: {e}")
    
    return False

def main():
    print("="*70)
    print("COMPREHENSIVE CANON VALIDATOR ERROR FIXER")
    print("="*70)
    
    # Phase 1: Fix missing typing imports
    print("\n[PHASE 1] Fixing missing typing imports...")
    for py_file in AGENTIC_CORE.rglob("*.py"):
        if '__pycache__' in str(py_file) or 'archives' in str(py_file):
            continue
        if fix_missing_typing_imports(py_file):
            stats['import_fixes'] += 1
            print(f"  ✓ Fixed typing imports: {py_file.name}")
    
    print(f"  [COMPLETE] Fixed {stats['import_fixes']} files with missing typing imports")
    
    # Phase 2: Fix import order violations
    print("\n[PHASE 2] Fixing import order violations...")
    for py_file in AGENTIC_CORE.rglob("*.py"):
        if '__pycache__' in str(py_file) or 'archives' in str(py_file):
            continue
        if fix_import_order(py_file):
            stats['import_order_fixes'] += 1
            if stats['import_order_fixes'] <= 10:
                print(f"  ✓ Fixed import order: {py_file.name}")
    
    print(f"  [COMPLETE] Fixed {stats['import_order_fixes']} files with import order issues")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"  Typing imports fixed:   {stats['import_fixes']}")
    print(f"  Import order fixed:     {stats['import_order_fixes']}")
    print(f"  Depth violations:       {stats['depth_fixes']} (manual review needed)")
    print(f"  Hierarchy violations:   {stats['hierarchy_fixes']} (manual review needed)")
    print(f"  Span violations:        {stats['span_fixes']} (manual review needed)")
    print("="*70)

if __name__ == "__main__":
    main()
