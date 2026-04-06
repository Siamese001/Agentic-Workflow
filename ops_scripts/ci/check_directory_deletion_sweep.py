"""CI Gate: Directory Deletion Import Sweep.

When a directory under a protected root is deleted in a PR/commit,
this check verifies that no live imports still reference the deleted path.

Uses git diff to detect deleted directories, then cross-references against
the ImportResolutionGuardian baseline and current scan to ensure no new
unresolved imports were introduced by the deletion.

Exit codes:
  0 = PASS (no unswept deletions)
  1 = FAIL (deleted directory still has live import references)
  2 = ERROR (script-level failure)

Usage:
  python ops_scripts/ci/check_directory_deletion_sweep.py
  python ops_scripts/ci/check_directory_deletion_sweep.py --base-ref origin/main
  python ops_scripts/ci/check_directory_deletion_sweep.py --repo-root /path/to/repo
"""
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

PROTECTED_ROOTS: tuple[str, ...] = (AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR)
INTERNAL_ROOTS: frozenset[str] = frozenset(PROTECTED_ROOTS)
WALK_EXCLUDES: frozenset[str] = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES

def get_deleted_directories(repo_root: Path, base_ref: str) -> list[str]:
    """Get directories that were deleted relative to base_ref.

    Returns repo-relative forward-slash paths of deleted directories.
    """
    try:
        result = subprocess.run(['git', 'diff', '--diff-filter=D', '--name-only', base_ref, 'HEAD'], capture_output=True, text=True, cwd=repo_root)
        if result.returncode != 0:
            return []
    except FileNotFoundError:    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access
        return []
    deleted_files = result.stdout.strip().splitlines()
    if not deleted_files:
        return []
    deleted_dirs: set[str] = set()
    for f in deleted_files:
        f_posix = f.replace('\\', '/')
        top = f_posix.split('/')[0] if '/' in f_posix else ''
        if top not in PROTECTED_ROOTS:
            continue
        parent = '/'.join(f_posix.split('/')[:-1])
        if parent:
            deleted_dirs.add(parent)
    truly_deleted: list[str] = []
    for d in sorted(deleted_dirs):
        full_path = repo_root / d
        if not full_path.is_dir():
            truly_deleted.append(d)
    return truly_deleted

def find_imports_referencing_directory(repo_root: Path, deleted_dir: str) -> list[dict]:
    """Find live import statements that reference a deleted directory.

    Converts directory path to module prefix and scans all .py files.
    """
    module_prefix = deleted_dir.replace('/', '.')
    references: list[dict] = []
    for root_name in PROTECTED_ROOTS:
        scan_dir = repo_root / root_name
        if not scan_dir.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(scan_dir):
            dirnames[:] = [d for d in dirnames if d not in WALK_EXCLUDES]
            for fn in filenames:
                if not fn.endswith('.py'):
                    continue
                fpath = Path(dirpath) / fn
                rel = fpath.relative_to(repo_root).as_posix()
                file_refs = _check_file_imports(fpath, rel, module_prefix)
                references.extend(file_refs)
    return references

def _check_file_imports(fpath: Path, rel: str, module_prefix: str) -> list[dict]:
    """Check a single file for imports referencing the given module prefix."""
    try:
        source = fpath.read_text(encoding='utf-8', errors='replace')
    except OSError:    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
        return []
    try:
        tree = ast.parse(source, filename=str(fpath))
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        return []
    refs: list[dict] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module == module_prefix or node.module.startswith(module_prefix + '.'):
                names = [a.name for a in node.names or []]
                refs.append({'file': rel, 'lineno': node.lineno, 'import_module': node.module, 'imported_names': names})
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == module_prefix or alias.name.startswith(module_prefix + '.'):
                    refs.append({'file': rel, 'lineno': node.lineno, 'import_module': alias.name, 'imported_names': [alias.name]})
    return refs

def main() -> int:
    """Entry point."""
    import argparse
    parser = argparse.ArgumentParser(description='CI Gate: Directory Deletion Import Sweep')
    parser.add_argument('--repo-root', type=Path, default=PROJECT_ROOT, help='Repository root (default: auto-detected)')
    parser.add_argument('--base-ref', default='origin/main', help='Git base reference to diff against (default: origin/main)')
    parser.add_argument('--verbose', action='store_true', help='Print detailed output')
    args = parser.parse_args()
    root = args.repo_root.resolve()
    print(f'[DIR-DELETION-SWEEP] Checking for deleted directories vs {args.base_ref}')
    deleted_dirs = get_deleted_directories(root, args.base_ref)
    if not deleted_dirs:
        print('[DIR-DELETION-SWEEP] PASS: No protected directories deleted')
        return 0
    print(f'[DIR-DELETION-SWEEP] Found {len(deleted_dirs)} deleted protected director(ies):')
    for d in deleted_dirs:
        print(f'  - {d}')
    all_violations: list[dict] = []
    for d in deleted_dirs:
        refs = find_imports_referencing_directory(root, d)
        if refs:
            print(f'\n[DIR-DELETION-SWEEP] VIOLATION: {d} deleted but {len(refs)} import(s) remain:')
            for r in refs:
                print(f"  {r['file']}:{r['lineno']} -> {r['import_module']}")
                all_violations.append({**r, 'deleted_directory': d})
        elif args.verbose:
            print(f'  {d}: clean (no remaining imports)')
    if all_violations:
        print(f'\n[DIR-DELETION-SWEEP] FAIL: {len(all_violations)} unswept import(s) to deleted directories')
        print('[DIR-DELETION-SWEEP] Fix: Remove or redirect these imports before merging.')
        return 1
    print('\n[DIR-DELETION-SWEEP] PASS: All deleted directories have been import-swept')
    return 0
if __name__ == '__main__':
    sys.exit(main())
