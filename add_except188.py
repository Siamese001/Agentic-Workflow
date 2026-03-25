#!/usr/bin/env python3
"""Add except after line 188"""

import pathlib

p = pathlib.Path('tools/analyze_persistent_memory_opportunities.py')
content = p.read_text(encoding='utf-8')
lines = content.splitlines(True)

# Add except after line 188
if len(lines) > 188:
    lines.insert(189, '            except (ValueError, TypeError, RuntimeError):\n')
    lines.insert(190, '                continue\n')

p.write_text(''.join(lines), encoding='utf-8')
print('Added except after line 188')
