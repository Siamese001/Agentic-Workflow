from __future__ import annotations
"""
Check depth violations using SSOT.
[SSOT] All depth requirements derived from SOVEREIGN_REGISTRY in structure_blueprint.py
"""
from pathlib import Path
from agentic_core.config.blueprint_sovereign.structure_blueprint import SOVEREIGN_REGISTRY
from typing import Any
root: Any = Path('c:/Git/Agentic-Workflow')
violations: Any = []
required_depth: Any = SOVEREIGN_REGISTRY['agentic_core']['depth']
for py_file in root.glob('agentic_core/**/*.py'):
    rel_path: Any = py_file.relative_to(root)
    depth: Any = len(rel_path.parts)
    if depth > REQUIRED_DEPTH + 1:
        violations.append((str(rel_path), depth))
print(f'Total violations: {len(violations)}')
print(f'[SSOT] agentic_core required depth: {REQUIRED_DEPTH}')
if violations:
    print('\nFirst 20 violations:')
    for path, depth in violations[:20]:
        print(f'  Depth {depth}: {path}')
