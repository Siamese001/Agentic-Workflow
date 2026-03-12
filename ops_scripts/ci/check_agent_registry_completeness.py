"""AST-based CI guard: every apps_* reasoning agent class is in AGENT_REGISTRY.

Scans all apps_*/reasoning/*.py files, extracts class names, cross-checks
against the AGENT_REGISTRY dict keys.  Hard-fails on any missing entry.
"""
from __future__ import annotations
import ast
import sys
from pathlib import Path
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
REPO_ROOT = Path(__file__).resolve().parents[2]
REASONING_GLOBS = ['apps_lic/reasoning/*.py', 'apps_rg/reasoning/*.py', 'apps_shared/reasoning/*.py']

def _extract_classes(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding='utf-8', errors='replace'))
    except SyntaxError:
        return []
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

def _load_registry_keys() -> set[str]:
    # guardian: allow-global-mutation
    sys.path.insert(0, str(REPO_ROOT))
    try:
        from agentic_core.agents.agent_registry import AGENT_REGISTRY
        return set(AGENT_REGISTRY.keys())
    except (ImportError, AttributeError):
        return set()

def main() -> int:
    agent_classes: list[tuple[str, str]] = []
    for glob in REASONING_GLOBS:
        for path in REPO_ROOT.glob(glob):
            for cls in _extract_classes(path):
                agent_classes.append((cls, path.relative_to(REPO_ROOT).as_posix()))
    registry_keys = _load_registry_keys()
    missing = [(cls, path) for cls, path in agent_classes if cls not in registry_keys]
    print(f'Registry keys: {len(registry_keys)}')
    print(f'Agent classes scanned: {len(agent_classes)}')
    print(f'Missing from registry: {len(missing)}')
    if missing:
        print('FAIL: unregistered agent classes:')
        for cls, path in sorted(missing):
            print(f'  {cls}  ({path})')
        return 1
    print('OK: all agent classes registered')
    return 0
if __name__ == '__main__':
    sys.exit(main())
