"""Search for potentially fixable SSOT hardcoding cases that might have been missed."""
import ast
import os
import re
import sys
from pathlib import Path

# guardian: allow-global-mutation
sys.path.insert(0, '.')
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    ENFORCED_TERRITORIES,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

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
                    if '"reports"' in line and 'L6_observability' not in line:
                        if re.search('^\\s*"reports"', line) or re.search('\\[\\s*"reports"', line):
                            fixable_found.append((str(fpath.relative_to(ROOT)), lineno, line.strip()))
            except (OSError, UnicodeDecodeError):    # guardian: File operations with encoding need error-specific handling
                pass
print('Potentially fixable "reports" cases:')
for p, l, line in fixable_found[:10]:
    print(f'  {p}:{l} {line}')
