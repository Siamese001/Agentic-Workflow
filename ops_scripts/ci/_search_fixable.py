#!/usr/bin/env python3
"""Search for potentially fixable SSOT hardcoding cases that might have been missed."""

import sys, os, ast, re
from pathlib import Path

sys.path.insert(0, '.')
from agentic_core.L5_safety.config.structure_blueprint.ssot import ENFORCED_TERRITORIES, SOVEREIGN_EXCLUDED_FOLDERS

ROOT = Path('.')
fixable_found = []

for territory in sorted(ENFORCED_TERRITORIES):
    scan_root = ROOT / territory
    if not scan_root.exists():
        continue
    for dirpath, dirs, files in os.walk(scan_root):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        for fname in files:
            if not fname.endswith('.py'):
                continue
            fpath = Path(dirpath) / fname
            try:
                content = fpath.read_text(encoding='utf-8', errors='replace')
                lines = content.splitlines()
                for lineno, line in enumerate(lines, 1):
                    # Look for simple list elements that might have been missed
                    if '"reports"' in line and 'L6_observability' not in line:
                        # Check if it's a simple list element (not in dict)
                        if re.search(r'^\s*"reports"', line) or re.search(r'\[\s*"reports"', line):
                            fixable_found.append((str(fpath.relative_to(ROOT)), lineno, line.strip()))
            except (OSError, UnicodeDecodeError):
                pass

print('Potentially fixable "reports" cases:')
for p, l, line in fixable_found[:10]:
    print(f'  {p}:{l} {line}')
