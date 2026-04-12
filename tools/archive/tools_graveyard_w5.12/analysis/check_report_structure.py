#!/usr/bin/env python3
"""Check closure validation report structure."""

import json

with open("C:/Git/Agentic-Workflow/artifacts/adg/closure_validation_report_03252026_0345.json") as f:
    report = json.load(f)

print("Report keys:", list(report.keys()))
if "gates" in report:
    print("\nGates:")
    for gate in report["gates"]:
        if "STRUCTURAL" in gate.get("name", ""):
            print(
                "  "
                + gate["name"]
                + ": status="
                + str(gate.get("status"))
                + ", ratio="
                + str(gate.get("ratio"))
                + ", threshold="
                + str(gate.get("threshold"))
            )
            print("    Numerator: " + str(gate.get("numerator")))
            print("    Denominator: " + str(gate.get("denominator")))
