#!/usr/bin/env python3
"""Check config core syntax errors."""

import json

with open('C:/Git/Agentic-Workflow/syntax_error_report.json') as f:
    report = json.load(f)

print('Config core files:')
for err in report['details']:
    if 'config/core' in err['file']:
        file = err['file']
        line = err['line']
        msg = err['message'][:60] + '...' if len(err['message']) > 60 else err['message']
        print(f'  {file}:{line} - {msg}')
