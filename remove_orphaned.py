#!/usr/bin/env python3
"""Remove orphaned except blocks in analyze_persistent_memory_opportunities.py"""

import pathlib

p = pathlib.Path('tools/analyze_persistent_memory_opportunities.py')
content = p.read_text(encoding='utf-8')
lines = content.splitlines(True)

# Remove orphaned except at line 133
for i, line in enumerate(lines):
    if i == 132:  # Line 133 (0-indexed)
        if 'except (ValueError, TypeError, RuntimeError):' in line:
            # Remove this except and the continue after it
            lines[i] = ''
            if i+1 < len(lines) and 'continue' in lines[i+1]:
                lines[i+1] = ''

p.write_text(''.join(lines), encoding='utf-8')
print('Removed orphaned except in analyze_persistent_memory_opportunities.py')
