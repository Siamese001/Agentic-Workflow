#!/usr/bin/env python3
"""Find files containing agent classes that don't follow *Agent.py naming."""
import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

AGENT_SUFFIXES = {'Agent', 'Handler', 'Manager', 'Controller', 'Executor', 'Validator', 
                  'Orchestrator', 'Governor', 'Enforcer', 'Analyzer', 'Sentinel'}

EXCLUDE = {'Mixin', 'Base', 'Abstract', 'Protocol'}

def has_agent_class(path: Path) -> list:
    """Return agent class names in file."""
    try:
        tree = ast.parse(path.read_text(encoding='utf-8', errors='ignore'))
    except:
        return []
    
    agents = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if any(p in node.name for p in EXCLUDE):
                continue
            if any(node.name.endswith(s) for s in AGENT_SUFFIXES):
                agents.append(node.name)
    return agents

# Scan directories
scan_dirs = ['agentic_core', 'apps_lic', 'apps_rg', 'apps_shared']
misnamed = []
properly_named = 0

for d in scan_dirs:
    dir_path = PROJECT_ROOT / d
    if not dir_path.exists():
        continue
    for py_file in dir_path.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue
        
        agents = has_agent_class(py_file)
        if agents:
            if 'Agent' in py_file.name:
                properly_named += 1
            else:
                misnamed.append((py_file.relative_to(PROJECT_ROOT), agents))

print(f"Properly named (*Agent.py with agent classes): {properly_named}")
print(f"Misnamed (contains agents but no 'Agent' in filename): {len(misnamed)}")
print(f"\n{'='*60}")
print("FILES NEEDING RENAME:")
print(f"{'='*60}\n")

for path, classes in sorted(misnamed)[:50]:  # Show first 50
    print(f"{path}")
    print(f"  Classes: {', '.join(classes)}")
    print()

if len(misnamed) > 50:
    print(f"... and {len(misnamed) - 50} more files")
