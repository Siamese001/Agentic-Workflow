#!/usr/bin/env python3
"""Temporary script to check LocationAgent violations"""

from agentic_core.L5_safety.validators.LocationAgent import LocationAgent
from pathlib import Path

agent = LocationAgent(project_root=Path.cwd())
violations = agent.run()

print(f"Total violations: {len(violations)}")
print("\nFirst 10 violations:")
for i, v in enumerate(violations[:10]):
    if isinstance(v, dict):
        print(f"{i+1}. Type: {v.get('type', 'unknown')}")
        print(f"   File: {v.get('file', 'unknown')}")
        print(f"   Reason: {v.get('reason', 'unknown')}")
    else:
        print(f"{i+1}. {v}")
    print()

# Group violations by type
violation_types = {}
for v in violations:
    if isinstance(v, dict):
        vtype = v.get('type', 'unknown')
        violation_types[vtype] = violation_types.get(vtype, 0) + 1

print("\nViolations by type:")
for vtype, count in sorted(violation_types.items(), key=lambda x: x[1], reverse=True):
    print(f"  {vtype}: {count}")
