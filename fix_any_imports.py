#!/usr/bin/env python3
"""Fix missing 'from typing import Any' in files that use Any."""
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
AGENTIC_CORE = PROJECT_ROOT / "agentic_core"

def needs_any_import(content: str) -> bool:
    """Check if file uses Any but doesn't import it."""
    uses_any = bool(re.search(r': Any\b|: Any =|\bAny\]|\[Any\b|-> Any\b', content))
    has_any_import = bool(re.search(r'from typing import.*\bAny\b', content))
    return uses_any and not has_any_import

def add_any_import(file_path: Path) -> bool:
    """Add Any to typing import if needed."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception:
        return False
    
    if not needs_any_import(content):
        return False
    
    # Check if there's an existing typing import to extend
    typing_import_match = re.search(r'from typing import ([^\n]+)', content)
    
    if typing_import_match:
        # Extend existing import
        existing = typing_import_match.group(1)
        if 'Any' not in existing:
            new_import = f"from typing import Any, {existing}"
            content = content.replace(typing_import_match.group(0), new_import)
    else:
        # Add new import after other imports or at top
        lines = content.split('\n')
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                insert_idx = i + 1
            elif line.startswith('class ') or line.startswith('def ') or line.startswith('@'):
                break
        
        lines.insert(insert_idx, 'from typing import Any')
        content = '\n'.join(lines)
    
    file_path.write_text(content, encoding='utf-8')
    return True

def main():
    """Fix all files in agentic_core."""
    fixed = 0
    for py_file in AGENTIC_CORE.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue
        if add_any_import(py_file):
            print(f"[FIXED] {py_file.relative_to(PROJECT_ROOT)}")
            fixed += 1
    
    print(f"\n[DONE] Fixed {fixed} files")

if __name__ == "__main__":
    main()
