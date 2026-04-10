"""Manifest SSOT Check — CI Gate.

Fails if any CI script or workflow references legacy manifest filenames
(target_paths_v2.json, target_paths.json).  Only target_manifest_v3.json
is the allowed SSOT.

Exit 0 = pass, exit 1 = violations found.

Merge-ready gate.
"""
from __future__ import annotations

import sys
from pathlib import Path

LEGACY_FILENAMES = ['target_paths_v2.json', 'target_paths.json']
SCAN_DIRS = ['ops_scripts/ci', '.github/workflows']
SCAN_EXTENSIONS = {'.py', '.yml', '.yaml'}
ALLOWLIST = {'ops_scripts/ci/manifest_ssot_check.py'}

def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    violations: list[str] = []
    for scan_dir in SCAN_DIRS:
        root = project_root / scan_dir
        if not root.is_dir():
            continue
        for filepath in root.rglob('*'):
            if not filepath.is_file():
                continue
            if filepath.suffix not in SCAN_EXTENSIONS:
                continue
            rel = str(filepath.relative_to(project_root)).replace('\\', '/')
            if rel in ALLOWLIST:
                continue
            try:
                content = filepath.read_text(encoding='utf-8', errors='replace')
            except OSError:    # guardian: Add error context logging
                continue
            for legacy_name in LEGACY_FILENAMES:
                if legacy_name in content:
                    violations.append(f"{rel}: references legacy manifest '{legacy_name}'")
    print('Manifest SSOT Check:')
    print(f'  scanned={len(SCAN_DIRS)} dirs  legacy_names={LEGACY_FILENAMES}')
    if violations:
        print(f'FAIL: {len(violations)} legacy manifest reference(s):')
        for v in violations:
            print(f'  - {v}')
        return 1
    print('PASS: no legacy manifest references found')
    return 0
if __name__ == '__main__':
    sys.exit(main())
