"""Pre-commit hook: reject generated artifacts that are tracked by git.

Deterministic, zero-network, no external dependencies.
Windows-safe (ASCII only).
"""
from __future__ import annotations

import fnmatch
import subprocess
import sys

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

FORBIDDEN_PATTERNS: list[str] = ['**/guardian_report.json', '**/.core_golden_seal', 'v15_d_evidence_*.json']

def _match(path: str, pattern: str) -> bool:
    """Match a git-relative path against a glob pattern.

    fnmatch does not handle '**/' natively, so we check both the full
    path and the basename for patterns that start with '**/' .
    """
    if pattern.startswith('**/'):
        suffix = pattern[3:]
        parts = path.replace('\\', '/').split('/')
        for i in range(len(parts)):
            if fnmatch.fnmatch('/'.join(parts[i:]), suffix):
                return True
        return False
    return fnmatch.fnmatch(path.replace('\\', '/'), pattern)

def main() -> int:
    try:
        result = subprocess.run(['git', 'ls-files'], capture_output=True, text=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:    # guardian: File operations should check existence before access
        print(f'ERROR: could not list tracked files: {exc}', file=sys.stderr)
        return 1
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    violations: list[str] = []
    for path in tracked:
        for pattern in FORBIDDEN_PATTERNS:
            if _match(path, pattern):
                violations.append(path)
                break
    if not violations:
        return 0
    print('FAIL: generated artifacts are tracked by git.', file=sys.stderr)
    print('', file=sys.stderr)
    for v in sorted(violations):
        print(f'  tracked: {v}', file=sys.stderr)
    print('', file=sys.stderr)
    print('Fix: for each path above, run:', file=sys.stderr)
    print('  git rm --cached <path>', file=sys.stderr)
    print('and ensure .gitignore excludes it.', file=sys.stderr)
    return 1
if __name__ == '__main__':
    raise SystemExit(main())
