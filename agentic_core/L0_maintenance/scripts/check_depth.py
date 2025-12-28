import os
from pathlib import Path

root = Path("c:/Git/Agentic-Workflow")
violations = []

for py_file in root.glob("agentic_core/**/*.py"):
    rel_path = py_file.relative_to(root)
    depth = len(rel_path.parts)
    if depth > 5:  # agentic_core max depth is 4, so parts should be ≤5 (root + 4 levels)
        violations.append((str(rel_path), depth))

print(f"Total violations: {len(violations)}")
if violations:
    print("\nFirst 20 violations:")
    for path, depth in violations[:20]:
        print(f"  Depth {depth}: {path}")
