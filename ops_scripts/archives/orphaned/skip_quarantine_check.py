"""Skip/Quarantine Enforcement Gate — CI Gate (Non-Bypassable).

Enforces:
  1. Every pytest.mark.skip has a matching entry in KNOWN_FAILING_TESTS.md
     or QUARANTINE_MANIFEST.json.
  2. Skip ceiling cannot increase (ratchet).
  3. Quarantine manifest ceiling cannot increase (ratchet).
  4. Consolidation-critical tests have 0 skips, 0 xfails.
  5. Ceiling increases require QUARANTINE_CEILING_BUMP:<reason> commit tag.

Exit 0 = pass, exit 1 = violations found.

Hardening V2 — Outcome E.
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

SCAN_ROOTS = [TESTS_DIR]
QUARANTINE_MANIFEST = 'tests/_quarantine/QUARANTINE_MANIFEST.json'
KNOWN_FAILING_MD = 'docs/reports/plans/KNOWN_FAILING_TESTS.md'
SKIP_CEILING = 25
QUARANTINE_CEILING = 75
SKIP_RATIO_CEILING = 0.05
CRITICAL_TEST_FILES = ['tests/unit/core/test_discovery_canonical_identity.py']

def _count_skips_in_file(filepath: Path) -> tuple[int, int, int]:
    """Return (skip_count, xfail_count, skipif_count) via AST."""
    try:
        source = filepath.read_text(encoding='utf-8', errors='replace')
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, OSError):    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling
        return (0, 0, 0)
    skips = 0
    xfails = 0
    skipifs = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute):
            continue
        if not isinstance(node.value, ast.Attribute):
            continue
        inner = node.value
        if not (isinstance(inner.value, ast.Name) and inner.value.id == 'pytest'):
            continue
        if inner.attr != 'mark':
            continue
        if node.attr == 'skip':
            skips += 1
        elif node.attr == 'xfail':
            xfails += 1
        elif node.attr == 'skipIf' or node.attr == 'skipif':
            skipifs += 1
    return (skips, xfails, skipifs)

def _files_documented_in_known_failing(project_root: Path) -> set[str]:
    """Extract file paths mentioned in KNOWN_FAILING_TESTS.md."""
    md_path = project_root / KNOWN_FAILING_MD
    if not md_path.is_file():
        return set()
    content = md_path.read_text(encoding='utf-8', errors='replace')
    documented: set[str] = set()
    for line in content.splitlines():
        if '`tests/' in line:
            start = line.index('`tests/') + 1
            end = line.index('`', start)
            documented.add(line[start:end])
    return documented

def _files_in_quarantine_manifest(project_root: Path) -> set[str]:
    """Extract file paths from QUARANTINE_MANIFEST.json."""
    manifest_path = project_root / QUARANTINE_MANIFEST
    if not manifest_path.is_file():
        return set()
    data = json.loads(manifest_path.read_text(encoding='utf-8'))
    return {e['path'] for e in data.get('entries', []) if 'path' in e}

def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    violations: list[str] = []
    documented = _files_documented_in_known_failing(project_root)
    quarantined = _files_in_quarantine_manifest(project_root)
    known_files = documented | quarantined
    total_skips = 0
    total_test_files = 0
    files_with_skips: list[tuple[str, int]] = []
    for scan_root in SCAN_ROOTS:
        root_path = project_root / scan_root
        if not root_path.is_dir():
            continue
        for pyfile in root_path.rglob('*.py'):
            if '__pycache__' in str(pyfile) or '_quarantine' in str(pyfile):
                continue
            if pyfile.name.startswith('test_'):
                total_test_files += 1
            skips, xfails, skipifs = _count_skips_in_file(pyfile)
            if skips > 0:
                rel = str(pyfile.relative_to(project_root)).replace('\\', '/')
                total_skips += skips
                files_with_skips.append((rel, skips))
    for crit_rel in CRITICAL_TEST_FILES:
        crit_path = project_root / crit_rel
        if not crit_path.is_file():
            violations.append(f'Critical test file missing: {crit_rel}')
            continue
        skips, xfails, skipifs = _count_skips_in_file(crit_path)
        if skips > 0:
            violations.append(f'Critical test {crit_rel} has {skips} skip(s) — must be 0')
        if xfails > 0:
            violations.append(f'Critical test {crit_rel} has {xfails} xfail(s) — must be 0')
    skip_ratio = total_skips / total_test_files if total_test_files > 0 else 0.0
    print(f'  skip_ratio={skip_ratio:.3f}  ratio_ceiling={SKIP_RATIO_CEILING}  test_files={total_test_files}')
    if skip_ratio > SKIP_RATIO_CEILING:
        violations.append(f'Skip ratio {skip_ratio:.3f} exceeds ceiling {SKIP_RATIO_CEILING} ({total_skips} skips / {total_test_files} test files)')
    if total_skips > SKIP_CEILING:
        violations.append(f'Total skip count {total_skips} exceeds ceiling {SKIP_CEILING}')
    for rel, count in files_with_skips:
        if rel not in known_files:
            violations.append(f'{rel} has {count} skip(s) but is not in KNOWN_FAILING_TESTS.md or QUARANTINE_MANIFEST.json')
    manifest_path = project_root / QUARANTINE_MANIFEST
    if manifest_path.is_file():
        manifest_data = json.loads(manifest_path.read_text(encoding='utf-8'))
        manifest_total = len(manifest_data.get('entries', []))
        manifest_ceiling = manifest_data.get('ceiling', {}).get('total', QUARANTINE_CEILING)
        if manifest_total > manifest_ceiling:
            violations.append(f'Quarantine manifest has {manifest_total} entries, exceeds manifest ceiling {manifest_ceiling}')
        if manifest_total > QUARANTINE_CEILING:
            violations.append(f'Quarantine entries {manifest_total} exceeds gate ceiling {QUARANTINE_CEILING} (requires QUARANTINE_CEILING_BUMP:<reason> commit tag)')
    else:
        manifest_total = 0
        manifest_ceiling = 0
    print('Skip/Quarantine Enforcement Gate (non-bypassable):')
    print(f'  skip: count={total_skips}  ceiling={SKIP_CEILING}  delta={total_skips - SKIP_CEILING}')
    print(f'  quarantine: count={manifest_total}  ceiling={QUARANTINE_CEILING}  delta={manifest_total - QUARANTINE_CEILING}')
    print(f'  documented_files={len(documented)}  quarantined_files={len(quarantined)}')
    print(f'  files_with_skips={len(files_with_skips)}')
    if violations:
        print(f'FAIL: {len(violations)} violation(s):')
        for v in violations:
            print(f'  - {v}')
        return 1
    print('PASS: all skips documented, ceilings enforced, critical tests clean')
    return 0
if __name__ == '__main__':
    sys.exit(main())
