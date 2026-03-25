#!/usr/bin/env python3
"""Check remaining cache layer syntax errors."""

import json

with open('C:/Git/Agentic-Workflow/syntax_fix_phases.json', 'r') as f:
    phases = json.load(f)

print('Cache layer files:')
for err in phases['Phase 2 - Cache Layer']:
    file = err['file']
    line = err['line']
    msg = err['message'][:60] + '...' if len(err['message']) > 60 else err['message']
    print(f'  {file}:{line} - {msg}')
