#!/usr/bin/env python3
"""Check all closure rows."""

import json

with open("C:/Git/Agentic-Workflow/artifacts/adg/closure_validation_report_03252026_0345.json") as f:
    report = json.load(f)

print("=== ALL CLOSURE ROWS ===")
for i, row in enumerate(report.get("closure_rows", [])):
    print(f"{i + 1}. Gate: {row.get('gate_name')}")
    print(f"   Status: {row.get('status')}")
    if "ratio" in row:
        print(f"   Ratio: {row.get('ratio')} (threshold: {row.get('threshold')})")
        print(f"   Numerator: {row.get('numerator')}, Denominator: {row.get('denominator')}")
    print()
