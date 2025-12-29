"""
Check depth violations using SSOT.
[SSOT] All depth requirements derived from SOVEREIGN_REGISTRY in structure_blueprint.py
"""
from pathlib import Path

from agentic_core.config.blueprint_sovereign.structure_blueprint import SOVEREIGN_REGISTRY

root = Path("c:/Git/Agentic-Workflow")
violations = []

# [SSOT] Get required depth for agentic_core from SOVEREIGN_REGISTRY
REQUIRED_DEPTH = SOVEREIGN_REGISTRY["agentic_core"]["depth"]

for py_file in root.glob("agentic_core/**/*.py"):
    rel_path = py_file.relative_to(root)
    depth = len(rel_path.parts)
    # [SSOT] Check against required depth (parts = depth + 1 for filename)
    if depth > REQUIRED_DEPTH + 1:
        violations.append((str(rel_path), depth))

print(f"Total violations: {len(violations)}")
print(f"[SSOT] agentic_core required depth: {REQUIRED_DEPTH}")
if violations:
    print("\nFirst 20 violations:")
    for path, depth in violations[:20]:
        print(f"  Depth {depth}: {path}")
