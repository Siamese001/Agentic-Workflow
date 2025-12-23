#!/usr/bin/env python3
"""
Gravity Violation Fixer - Systematic Circular Import Resolution
Fixes all gravity violations in agentic_core using:
1. TYPE_CHECKING blocks for runtime-unnecessary imports
2. String forward references for type hints
3. Proper absolute/relative import paths
"""
import re
from pathlib import Path
from typing import List, Tuple, Set

# Files that commonly have circular dependencies
CIRCULAR_PRONE_FILES = {
    'runtime/subatomic_hop.py',
    'runtime/subatomic_hop_l5.py', 
    'runtime/subatomic_hop_l5_integrated.py',
    'L3_orchestration/nervous_system.py',
    'L3_orchestration/mission_runner.py',
    'L5_safety/safety_layer.py',
    'tools/filesystem.py',
    'tools/examples.py'
}

def find_cross_layer_imports(file_path: Path) -> List[Tuple[int, str, str]]:
    """
    Find imports that cross L-layers (potential gravity violations).
    Returns: [(line_num, full_line, imported_module)]
    """
    violations = []
    
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines, 1):
        # Match: from agentic_core.LX_layer import ...
        match = re.match(r'^from agentic_core\.(L\d+_\w+)\.', line)
        if match:
            layer = match.group(1)
            violations.append((i, line.strip(), layer))
    
    return violations

def apply_type_checking_fix(file_path: Path, import_lines: List[int]) -> bool:
    """
    Wrap imports in TYPE_CHECKING block.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        
        # Check if TYPE_CHECKING already imported
        has_type_checking = any('TYPE_CHECKING' in line for line in lines[:30])
        
        # Find typing import line
        typing_import_idx = None
        for i, line in enumerate(lines):
            if line.startswith('from typing import'):
                typing_import_idx = i
                break
        
        if typing_import_idx is None:
            # Add typing import at top after docstring
            insert_idx = 0
            for i, line in enumerate(lines):
                if '"""' in line or "'''" in line:
                    # Find closing docstring
                    for j in range(i+1, len(lines)):
                        if '"""' in lines[j] or "'''" in lines[j]:
                            insert_idx = j + 1
                            break
                    break
            
            lines.insert(insert_idx, 'from typing import TYPE_CHECKING\n')
            typing_import_idx = insert_idx
        elif not has_type_checking:
            # Add TYPE_CHECKING to existing import
            lines[typing_import_idx] = lines[typing_import_idx].rstrip()
            if 'TYPE_CHECKING' not in lines[typing_import_idx]:
                lines[typing_import_idx] = lines[typing_import_idx].replace(
                    'from typing import',
                    'from typing import TYPE_CHECKING,'
                )
                lines[typing_import_idx] += '\n'
        
        # Wrap target imports in TYPE_CHECKING
        # Find first import to wrap
        first_import = min(import_lines)
        last_import = max(import_lines)
        
        # Insert TYPE_CHECKING block
        lines.insert(first_import - 1, '\nif TYPE_CHECKING:\n')
        
        # Indent wrapped imports
        for i in range(first_import, last_import + 2):
            if i < len(lines) and lines[i].startswith('from '):
                lines[i] = '    ' + lines[i]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return True
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def scan_agentic_core(project_root: Path) -> dict:
    """Scan agentic_core for all cross-layer imports."""
    agentic_core = project_root / 'agentic_core'
    results = {}
    
    for py_file in agentic_core.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue
        
        violations = find_cross_layer_imports(py_file)
        if violations:
            rel_path = py_file.relative_to(agentic_core)
            results[str(rel_path)] = violations
    
    return results

def main():
    """Main execution."""
    project_root = Path(__file__).parent.parent.parent
    
    print("="*70)
    print("GRAVITY VIOLATION SCANNER")
    print("="*70)
    
    violations = scan_agentic_core(project_root)
    
    print(f"\nFound {len(violations)} files with cross-layer imports:\n")
    
    for file_path, imports in sorted(violations.items()):
        print(f"\n{file_path}:")
        for line_num, line, layer in imports:
            print(f"  Line {line_num}: {line}")
    
    print(f"\n{'='*70}")
    print(f"Total files with violations: {len(violations)}")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    main()
