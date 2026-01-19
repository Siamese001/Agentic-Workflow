from __future__ import annotations
"""
Check depth violations using SSOT.
[SSOT] All depth requirements derived from SOVEREIGN_REGISTRY in structure_blueprint.py
"""
from pathlib import Path
from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_REGISTRY
from typing import Any
root: Any = Path('c:/Git/Agentic-Workflow')
violations: Any = []
required_depth: Any = SOVEREIGN_REGISTRY['agentic_core']['depth']
for py_file in root.glob('agentic_core/**/*.py'):
    rel_path: Any = py_file.relative_to(root)
    # [FIX] Depth = folder level where file resides, not path length
    depth: Any = len(rel_path.parts) - 1  # Subtract 1 because file itself is not a level
    if depth > required_depth:
        violations.append((str(rel_path), depth))
print(f'Total violations: {len(violations)}')
print(f'[SSOT] agentic_core required depth: {required_depth}')
if violations:
    print('\nFirst 20 violations:')
    for path, depth in violations[:20]:
        print(f'  Depth {depth}: {path}')
