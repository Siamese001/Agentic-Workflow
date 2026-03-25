#!/usr/bin/env python3
"""Check closure validation report."""

import json

with open('C:/Git/Agentic-Workflow/artifacts/adg/closure_validation_report_03252026_0345.json') as f:
    report = json.load(f)

print('=== STRUCTURAL COVERAGE STATUS ===')
for cap in report['capabilities']:
    if cap['name'] == 'STRUCTURAL COVERAGE':
        print(f'Name: {cap["name"]}')
        print(f'Status: {cap["status"]}')
        print(f'Ratio: {cap["ratio"]}')
        print(f'Threshold: {cap["threshold"]}')
        print(f'Numerator (parsed): {cap["numerator"]}')
        print(f'Denominator (discovered): {cap["denominator"]}')
        missing = cap["denominator"] - cap["numerator"]
        print(f'Missing: {missing} modules')

        # Check if we made progress
        if missing <= 12:
            print(f'\nPROGRESS: Only {missing} modules left to fix!')
        else:
            print(f'\nStill need to fix {missing} modules')
        break
