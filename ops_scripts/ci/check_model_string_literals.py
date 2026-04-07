"""CI guard G13: model string literals must only appear in config/registry, not agent code."""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATTERN = re.compile('(gpt-[0-9]|claude-[0-9]|gemini-[0-9]|text-embedding-3|qwen|llama)', re.I)
ALLOWED_PATHS = {'agentic_core/config/core/sovereign_config.py', 'agentic_core/agents/agent_registry.py', 'agentic_core/L2_execution/enforcement/SovereignLLMGateway.py', 'infrastructure/sdks_mcps/client_wrappers.py'}
SCAN_ROOTS = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR, SYSTEM_LEARNING_DIR]

def main() -> int:
    violations: list[str] = []
    for root in SCAN_ROOTS:
        for path in (REPO_ROOT / root).rglob('*.py'):
            rel = path.relative_to(REPO_ROOT).as_posix()
            if rel in ALLOWED_PATHS:
                continue
            try:
                tree = ast.parse(path.read_text(encoding='utf-8', errors='replace'))
            except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    if MODEL_PATTERN.search(node.value):
                        violations.append(f"{rel}:{node.lineno}: bare model literal '{node.value[:40]}'")
    if violations:
        print(f'FAIL: {len(violations)} bare model literal(s) found outside config/registry:')
        for v in violations:
            print(f'  {v}')
        return 1
    print('OK: no bare model string literals')
    return 0
if __name__ == '__main__':
    sys.exit(main())
