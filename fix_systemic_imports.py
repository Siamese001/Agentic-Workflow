#!/usr/bin/env python3
"""
Systematically injects missing imports discovered during Phase 33 Hardening.
Targeting: Enum, Any, Protocol, Path, dataclass, field, and os.
"""
import os
import re
from pathlib import Path

def heal_imports():
    """
    Systematically injects missing imports discovered during Phase 33 Hardening.
    Targeting: Enum, Any, Protocol, Path, and os.
    """
    targets = {
        'Enum': 'from enum import Enum',
        'Any': 'from typing import Any',
        'Protocol': 'from typing import Protocol',
        'Path': 'from pathlib import Path',
        'os': 'import os',
        'logging': 'import logging',
        'dataclass': 'from dataclasses import dataclass',
        'field': 'from dataclasses import field',
    }

    core_path = Path('agentic_core')
    fixed_count = 0

    print(f"--- [STARTING IMPORT HEAL] Path: {core_path.absolute()} ---")

    for py_file in core_path.rglob('*.py'):
        content = py_file.read_text(encoding='utf-8', errors='ignore')
        lines = content.splitlines()
        modified = False
        
        # Check for missing imports based on usage
        new_imports = []
        for name, import_stmt in targets.items():
            # Use regex to find actual usage (not just occurrences in strings)
            # Looks for the name followed by a delimiter like '(', ':', '[', or a space
            usage_pattern = rf'(?<![\'"])\b{name}\b(?![\'"])'
            if re.search(usage_pattern, content) and import_stmt not in content:
                # Special case: don't import 'os' if it's already part of 'from os import path'
                if name == 'os' and 'from os import' in content:
                    continue
                # Special case: don't add dataclass if already imported
                if name == 'dataclass' and 'from dataclasses import' in content:
                    # Check if dataclass is already in the import
                    if re.search(r'from dataclasses import.*\bdataclass\b', content):
                        continue
                if name == 'field' and 'from dataclasses import' in content:
                    # Check if field is already in the import
                    if re.search(r'from dataclasses import.*\bfield\b', content):
                        continue
                # Special case: don't add Any if already imported
                if name == 'Any' and 'from typing import' in content:
                    if re.search(r'from typing import.*\bAny\b', content):
                        continue
                # Special case: don't add Protocol if already imported
                if name == 'Protocol' and 'from typing import' in content:
                    if re.search(r'from typing import.*\bProtocol\b', content):
                        continue
                new_imports.append(import_stmt)

        if new_imports:
            print(f"[!] Healing {py_file.relative_to(core_path)}: Adding {new_imports}")
            # Insert at the top, but after the docstring if it exists
            insert_idx = 0
            if lines and lines[0].startswith('"""'):
                try:
                    # Find closing docstring
                    for i, line in enumerate(lines[1:], 1):
                        if '"""' in line:
                            insert_idx = i + 1
                            break
                except IndexError:
                    pass
            elif lines and lines[0].startswith("from __future__"):
                insert_idx = 1
            
            for imp in reversed(new_imports):
                lines.insert(insert_idx, imp)
            
            py_file.write_text('\n'.join(lines) + '\n', encoding='utf-8')
            fixed_count += 1

    print(f"--- [HEAL COMPLETE] Fixed {fixed_count} files ---")

if __name__ == "__main__":
    heal_imports()
