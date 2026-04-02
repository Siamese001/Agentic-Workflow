#!/usr/bin/env python3
"""Check closure validation summary."""

import json

with open('C:/Git/Agentic-Workflow/artifacts/adg/closure_validation_report_03252026_0345.json', 'r') as f:
    report = json.load(f)

print('=== SUMMARY ===')
summary = report.get('summary', {})
for key, value in summary.items():
    print(f'{key}: {value}')

print('\n=== CLOSURE ROWS ===')
for row in report.get('closure_rows', []):
    if 'STRUCTURAL' in row.get('gate_name', ''):
        print(f'Gate: {row.get("gate_name")}')
        print(f'  Status: {row.get("status")}')
        print(f'  Ratio: {row.get("ratio")}')
        print(f'  Threshold: {row.get("threshold")}')
        print(f'  Numerator: {row.get("numerator")}')
        print(f'  Denominator: {row.get("denominator")}')
        missing = row.get('denominator', 0) - row.get('numerator', 0)
        print(f'  Missing: {missing} modules')
